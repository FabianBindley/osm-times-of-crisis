import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic
import sys
import os
import pickle
import csv
import shutil
import osmium
from shapely import wkb
from collections import Counter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

class WayHandler(osmium.SimpleHandler):
    def __init__(self, way_ids_to_process):
        super().__init__()
        self.way_ids_to_process = set(way_ids_to_process)
        self.way_data = {}

    def way(self, w):
        if w.id in self.way_ids_to_process:
            nodes = [n.ref for n in w.nodes]
            self.way_data[(w.id,w.version)] = {
                "nodes": nodes,
            } 

def get_changes_and_previous(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    start_date = disaster_date - pre_disaster
    end_date = disaster_date + imm_disaster + post_disaster + timedelta(days=1)
    headers=["id", "element_id", "element_type", "edit_type",   "timestamp", "disaster_id", "version", "visible", "changeset", "tags", "building", "highway", "coordinates", "uid", "geojson_verified"]

    changes = db_utils.get_sample_changes_for_disaster(disaster_id, sample_size, sample, start_date, end_date, "all", random_sample, three_years_pre= pre_disaster_days > 370)
    changes_df = pd.DataFrame(changes, columns=headers)

    previous_version_query_set = set(
        (row["element_id"], row["disaster_id"], row["version"] - 1, row["element_type"])
        for _, row in changes_df.iterrows()
    )
    print(len(f"previous version query set length: {len(previous_version_query_set)}"))

    previous_versions = db_utils.get_existing_versions(list(previous_version_query_set), "all", three_years_pre= pre_disaster_days > 370)
    previous_versions_df = pd.DataFrame(previous_versions, columns=headers)
    previous_versions_df["version"] += 1

    # If a previous version doesn't exist because it's not in the DB, then we con't consider the change 
    merged = pd.merge(changes_df, previous_versions_df, on=["element_id","version"], suffixes=(f'_curr', f'_prev'))

    # Create separate columns for current and previous versions
    merged.rename(columns={"version": "version_curr"}, inplace=True)
    merged["version_prev"] = merged["version_curr"] - 1

    # Select and print only the relevant columns from the merged DataFrame
    pd.set_option("display.max_colwidth", None)
    merged.to_pickle(f'./Results/ChangeDifferences/disaster{disaster_id}/changes_curr_prev_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.pickle')

    return merged

def compute_coordinate_distance_change (coordinates_curr, coordinates_prev):
    point_cur = wkb.loads(bytes.fromhex(coordinates_curr))
    point_prev = wkb.loads(bytes.fromhex(coordinates_prev))

    lat_lon_cur = (point_cur.y, point_cur.x)  
    lat_lon_prev = (point_prev.y, point_prev.x)

    distance = geodesic(lat_lon_cur, lat_lon_prev).meters
    return distance


def diff_changes(curr, prev, way_handler, missing_way_count):
    diff = {
        "element_id": curr["element_id"],
        "edit_type_curr": curr["edit_type"],
        "edit_type_prev": prev["edit_type"],
        "element_type": curr["element_type"],
        "version_curr": curr["version"],
        "timestamp_curr": curr["timestamp"],
        "tags_created": [],
        "tags_edited": [],
        "tags_deleted": [],
        "coordinate_distance_change": None,
        "made_visible": False,
        "timestamp_between_edits": None,
        "way_nodes_created": [],
        #"way_nodes_moved": [], # This is pretty awkward to do without getting and caching the node coordinates, so we leave for now
        "way_nodes_deleted": [],
        "way_length_change": None, # Same as above
    }

    diff["coordinate_distance_change"] = round(compute_coordinate_distance_change(curr["coordinates"], prev["coordinates"]), 4)
    
    diff["timestamp_between_edits"] = curr["timestamp"] - prev["timestamp"]
    
    curr_tags = curr.get("tags", {})
    prev_tags = prev.get("tags", {})

    if curr_tags != prev_tags:
        diff['tags_created'] = [key for key in curr_tags if key not in prev_tags]
        diff['tags_deleted'] = [key for key in prev_tags if key not in curr_tags]
        diff['tags_edited'] = [key for key in curr_tags if key in prev_tags and curr_tags[key] != prev_tags[key]]

    if prev["visible"] == False and curr["visible"] == True:
        diff["made_visible"] = True 

    if curr["element_type"] == "way":
        curr_key = (curr["element_id"], curr["version"])
        prev_key = (curr["element_id"], curr["version"] - 1)

        # Perform the logic only if both keys exist
        if curr_key in way_handler.way_data and prev_key in way_handler.way_data:
            
            curr_way_nodes = way_handler.way_data[curr_key]["nodes"]
            prev_way_nodes = way_handler.way_data[prev_key]["nodes"]

            diff['way_nodes_created'] = [node for node in curr_way_nodes if node not in prev_way_nodes]
            diff['way_nodes_deleted'] = [node for node in prev_way_nodes if node not in curr_way_nodes]
            #diff['way_nodes_moved'] = [node for node in curr_way_nodes if node in prev_way_nodes]
        else:
            missing_way_count += 1

    return diff,  missing_way_count 


def compute_changes_diffs(disaster_area, disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days):
    #previous_edit_types = (len(changes_and_prev[changes_and_prev["edit_type_prev"]=="create"]), len(changes_and_prev[changes_and_prev["edit_type_prev"]=="edit"]), len(changes_and_prev[changes_and_prev["edit_type_prev"]=="delete"]))
    changes_and_prev = pd.read_pickle(f'./Results/ChangeDifferences/disaster{disaster_id}/changes_curr_prev_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.pickle')
    way_ids = set(changes_and_prev[changes_and_prev["element_type_curr"]=="way"]["element_id"])

    input_file = f'./Data/{disaster_area}/{disaster_area}NodesWays.osh.pbf'
    way_handler = WayHandler(way_ids)
    way_handler.apply_file(input_file)
    
    missing_way_count = 0

    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    pre_disaster_start_date = disaster_date - pre_disaster

    imm_disaster_start_date = disaster_date

    post_disaster_start_date = disaster_date + imm_disaster
    post_disaster_end_date = post_disaster_start_date + post_disaster + timedelta(days=1)

    intervals = [pre_disaster_start_date, imm_disaster_start_date, post_disaster_start_date, post_disaster_end_date]
    periods = ["pre","imm","post"]
    # Split this by period pre, imm, post

    for i in range(len(intervals)-1):
        start_date = intervals[i]
        end_date = intervals[i+1]
        print(f"Period: {periods[i]}")
        diffs = []
        changes_and_prev_period = changes_and_prev[(start_date < changes_and_prev["timestamp_curr"]) & (changes_and_prev["timestamp_curr"] < end_date)]
        for _, row in changes_and_prev_period.iterrows():
            curr = {
                "element_id": row["element_id"],
                "edit_type": row["edit_type_curr"],
                "element_type": row["element_type_curr"],
                "version": row["version_curr"],
                "tags": row["tags_curr"],
                "coordinates": row["coordinates_curr"],
                "nodes": row.get("nodes_curr", None),
                "timestamp": row["timestamp_curr"],
                "visible": row["visible_curr"],
            }
            prev = {
                "tags": row["tags_prev"],
                "edit_type": row["edit_type_prev"],
                "coordinates": row["coordinates_prev"],
                "timestamp": row["timestamp_prev"],
                "visible": row["visible_prev"],
                "edit_type": row["edit_type_prev"]
            }
            diff, count = diff_changes(curr, prev, way_handler, missing_way_count)
            diffs.append(diff)
            missing_way_count = count

        diff_df = pd.DataFrame(diffs)
        os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences", exist_ok=True)
        diff_df.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{periods[i]}.csv", index=False)
        diff_df.to_pickle(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{periods[i]}.pickle")

    print("Missing way count: ",missing_way_count)

def analyse_change_diffs(disaster_area, disaster_id,  pre_disaster_days, imm_disaster_days, post_disaster_days):
    #changes_and_prev = pd.read_pickle(f'./Results/ChangeDifferences/disaster{disaster_id}/changes_curr_prev.pickle')
    #previous_change_types = (len(changes_and_prev[changes_and_prev["edit_type_prev"]=="create"]), len(changes_and_prev[changes_and_prev["edit_type_prev"]=="edit"]), len(changes_and_prev[changes_and_prev["edit_type_prev"]=="delete"]))

    # We have 3 rows, 1 for each period, and for each row we have lots of metrics
    # previous edit types
    headers = ["disaster_id", "period", "total_changes", "nodes_changed", "ways_changed", "previous_change_creates", "previous_change_edits", "previous_change_deletes", "tags_created", "avg_num_tags_created", 
                                    "tags_edited","avg_num_tags_edited", "tags_deleted","avg_num_tags_deleted", "most_created_key", "most_created_key_frequency", "most_edited_key", "most_edited_key_frequency","most_deleted_key", "most_deleted_key_frequency", 
                                    "coordinates_changed","median_coordinate_distance_change", "made_visible", "avg_timestamp_between_edits", 
                                "way_nodes_created","avg_num_way_nodes_created", "way_nodes_deleted","avg_num_way_nodes_deleted", "way_geometry_changed"]
    diff_analysis_df = pd.DataFrame(columns=headers)
    
    for period in ["pre", "imm", "post"]:

        diff_df =  pd.read_pickle(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{period}.pickle")

        total_changes = len(diff_df)
        nodes_changed = len(diff_df[diff_df["element_type"] == "node"])

        prev_edit_types = (len(diff_df[diff_df["edit_type_prev"] == "create"]), len(diff_df[diff_df["edit_type_prev"] == "edit"]), len(diff_df[diff_df["edit_type_prev"] == "delete"]))

        diffs_tags_create = diff_df.loc[diff_df["tags_created"].apply(len) > 0, ["tags_created"]]
        tags_created = len(diffs_tags_create)
        diffs_tags_edit = diff_df.loc[diff_df["tags_edited"].apply(len) > 0, ["tags_edited"]]
        tags_edited = len(diffs_tags_edit)
        diffs_tags_delete = diff_df.loc[diff_df["tags_deleted"].apply(len) > 0, ["tags_deleted"]]
        tags_deleted = len(diffs_tags_delete)


        avg_tag_change_nums = (diffs_tags_create["tags_created"].apply(len).mean(), diffs_tags_edit["tags_edited"].apply(len).mean(), diffs_tags_delete["tags_deleted"].apply(len).mean())
       
        all_created_tags = [key for tags in diffs_tags_create["tags_created"] for key in tags]
        all_edited_tags = [key for tags in diffs_tags_edit["tags_edited"] for key in tags]
        all_deleted_tags = [key for tags in diffs_tags_delete["tags_deleted"] for key in tags]

        most_created_key, most_created_key_frequency = Counter(all_created_tags).most_common(1)[0]
        most_edited_key, most_edited_key_frequency = Counter(all_edited_tags).most_common(1)[0]
        most_deleted_key, most_deleted_key_frequency = Counter(all_deleted_tags).most_common(1)[0]

        coordinates = diff_df.loc[diff_df["coordinate_distance_change"] != 0, ["element_type","coordinate_distance_change"]]
        coordinates_changed = len(coordinates)
        avg_coordinate_distance_change = coordinates["coordinate_distance_change"].median()
        #rint(coordinates_changed/total_changes)
       # print(avg_coordinate_distance_change)

        made_visible = len(diff_df[diff_df["made_visible"] == True])
        avg_timestamp_between_edits = diff_df["timestamp_between_edits"].median()
        print(avg_timestamp_between_edits)

        way_diffs = diff_df[diff_df["element_type"] == "way"]
        ways_changed = len(way_diffs)

        way_nodes_created_diffs = way_diffs.loc[way_diffs["way_nodes_created"].apply(len) > 0, ["way_nodes_created"]]
        way_nodes_created = len(way_nodes_created_diffs)
        way_nodes_deleted_diffs  = way_diffs.loc[way_diffs["way_nodes_deleted"].apply(len) > 0, ["way_nodes_deleted"]]
        way_nodes_deleted = len(way_nodes_deleted_diffs)

        avg_way_nodes_created = way_nodes_created_diffs["way_nodes_created"].apply(len).mean()
        avg_way_nodes_deleted = way_nodes_deleted_diffs["way_nodes_deleted"].apply(len).mean()

        way_geometry_changed = len(way_diffs[way_diffs["coordinate_distance_change"] != 0])

        res = [disaster_id, period, total_changes, nodes_changed, ways_changed, prev_edit_types[0], prev_edit_types[1], prev_edit_types[2], tags_created, avg_tag_change_nums[0], tags_edited, avg_tag_change_nums[1], tags_deleted, avg_tag_change_nums[2],  
                                                       most_created_key, most_created_key_frequency, most_edited_key, most_edited_key_frequency, most_deleted_key, most_deleted_key_frequency, 
                                                       coordinates_changed, avg_coordinate_distance_change, made_visible, avg_timestamp_between_edits, way_nodes_created, avg_way_nodes_created, way_nodes_deleted, avg_way_nodes_deleted, way_geometry_changed]
        diff_analysis_df.loc[len(diff_analysis_df)] = res

    diff_analysis_df.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/analysis_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_.csv", index=False)


def analysis_summary(disaster_ids, pre_disaster_days, imm_disaster_days, post_disaster_days):
    headers = ["disaster_id", "period", "total_changes", "nodes_changed", "ways_changed", "previous_change_creates", "previous_change_edits", "previous_change_deletes", "tags_created", "avg_num_tags_created", 
                                    "tags_edited","avg_num_tags_edited", "tags_deleted","avg_num_tags_deleted", "most_created_key", "most_created_key_frequency", "most_edited_key", "most_edited_key_frequency","most_deleted_key", "most_deleted_key_frequency", 
                                    "coordinates_changed","median_coordinate_distance_change", "made_visible", "avg_timestamp_between_edits", 
                                "way_nodes_created","avg_num_way_nodes_created", "way_nodes_deleted","avg_num_way_nodes_deleted", "way_geometry_changed"]
    diff_analysis_df = pd.DataFrame(columns=headers)
   
    for disaster_id in disaster_ids:
        results = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/analysis_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_.csv")
        diff_analysis_df = pd.concat([diff_analysis_df, results], ignore_index=True)

    diff_analysis_df.to_csv(f"./Results/ChangeDifferences/summary/all_disaster_analysis_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_.csv")



# Please make sure to run db_prepare_change_differences.py before running this script, to import missing 
# previous change versions into the db
if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    disaster_ids =  [3,4,5,6]
    sample_size = 1000000
    sample = False
    random_sample = False

    generate_merged = True
    generate_diffs = True

    #periods = [(1095,60,365),(365,60,365)]
    periods = [(1095,60,365),(365,60,365)]
    periods = [(1095,60,365),(365,60,365)]
    print(f"Getting change differences for disasters: {disaster_ids}")
    
    for disaster_id in disaster_ids:
        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
        for period in periods:

            pre_disaster_days, imm_disaster_days, post_disaster_days = period
            if generate_merged:
                print(f"Getting changes for {disaster_area[0]} {disaster_date.year}")
                get_changes_and_previous(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days)

            if generate_diffs:
                print(f"Computing diffs for {disaster_area[0]} {disaster_date.year}")
                compute_changes_diffs(disaster_area[0], disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days)

            print(f"Analysing diffs for {disaster_area[0]} {disaster_date.year}")
            analyse_change_diffs(disaster_area[0], disaster_id,  pre_disaster_days, imm_disaster_days, post_disaster_days)
    
    # Combine into 1 summary analysis
    analysis_summary(disaster_ids, pre_disaster_days, imm_disaster_days, post_disaster_days)