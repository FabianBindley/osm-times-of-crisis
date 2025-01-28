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

    changes = db_utils.get_sample_changes_for_disaster(disaster_id, sample_size, sample, start_date, end_date, "all", random=True)
    changes_df = pd.DataFrame(changes, columns=headers)


    previous_version_query_set = set(
        (row["element_id"], row["disaster_id"], row["version"] - 1, row["element_type"])
        for _, row in changes_df.iterrows()
    )

    previous_versions = db_utils.get_existing_versions(list(previous_version_query_set), "all")
    previous_versions_df = pd.DataFrame(previous_versions, columns=headers)
    previous_versions_df["version"] += 1

    # If a previous version doesn't exist because it's not in the DB, then we con't consider the change 
    merged = pd.merge(changes_df, previous_versions_df, on=["element_id","version"], suffixes=(f'_curr', f'_prev'))

    # Create separate columns for current and previous versions
    merged.rename(columns={"version": "version_curr"}, inplace=True)
    merged["version_prev"] = merged["version_curr"] - 1

    # Select and print only the relevant columns from the merged DataFrame
    pd.set_option("display.max_colwidth", None)
    #print(merged[["element_id", "version_curr", "timestamp_curr", "edit_type_curr","version_prev", "timestamp_prev",  "edit_type_prev",]])
    merged.to_pickle(f'./Results/ChangeDifferences/disaster{disaster_id}/changes_curr_prev.pickle')

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
        "edit_type": curr["edit_type"],
        "element_type": curr["element_type"],
        "version_curr": curr["version"],
        "tags_created": [],
        "tags_edited": [],
        "tags_deleted": [],
        "coordinate_change": None,
        "made_visible": False,
        "timestamp_between_edits": None,
    }
    if curr["element_type"] == "way":
        diff.update({
            "way_nodes_created": [],
            #"way_nodes_moved": [], # This is pretty awkward to do without getting and caching the node coordinates, so we leave for now
            "way_nodes_deleted": [],
            "way_length_change": None, # Same as above
        })


    diff["coordinate_change"] = round(compute_coordinate_distance_change(curr["coordinates"], prev["coordinates"]), 4)
    
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
        if (curr["element_id"],curr["version"]) in way_handler.way_data and (curr["element_id"],curr["version"]-1) in way_handler.way_data:
            curr_way_nodes = way_handler.way_data[(curr["element_id"],curr["version"])]
            prev_way_nodes = way_handler.way_data[(curr["element_id"],curr["version"]-1)]

            if (curr_way_nodes != prev_way_nodes):
                diff['way_nodes_created'] = [node for node in curr_way_nodes if node not in prev_way_nodes]
                diff['way_nodes_deleted'] = [node for node in prev_way_nodes if node not in curr_way_nodes]
                #diff['way_nodes_moved'] = [node for node in curr_way_nodes if node in prev_way_nodes]
        else:
            missing_way_count += 1
    return diff


def compute_changes_diffs(disaster_area, disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days):
    #previous_edit_types = (len(changes_and_prev[changes_and_prev["edit_type_prev"]=="create"]), len(changes_and_prev[changes_and_prev["edit_type_prev"]=="edit"]), len(changes_and_prev[changes_and_prev["edit_type_prev"]=="delete"]))
    changes_and_prev = pd.read_pickle(f'./Results/ChangeDifferences/disaster{disaster_id}/changes_curr_prev.pickle')
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
    # Split this by period pre, imm, post

    for i in range(len(intervals)-1):
        start_date = intervals[i]
        end_date = intervals[i+1]

        diffs = []
        for _, row in changes_and_prev.iterrows():
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
                "coordinates": row["coordinates_prev"],
                "timestamp": row["timestamp_prev"],
                "visible": row["visible_prev"],
            }
            diff = diff_changes(curr, prev, way_handler, missing_way_count)
            diffs.append(diff)

        diff_df = pd.DataFrame(diffs)
        diff_df.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences.csv", index=False)
        diff_df.to_pickle(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences.pickle")

    print("Missing way count: ",missing_way_count)

def analyse_change_diffs(disaster_area, disaster_id):
    pass

# Please make sure to run db_prepare_change_differences.py before running this script, to import missing 
# previous change versions into the db
if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    disaster_ids =  [6]
    sample_size = 200000
    sample = True

    generate_merged = False
    #get_change_differences_all_disasters()

    periods = [(365,30,365)]
    print(f"Getting change differences for disasters: {disaster_ids}")
    for disaster_id in disaster_ids:
        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)

        for period in periods:
            pre_disaster_days, imm_disaster_days, post_disaster_days = period
            if generate_merged:
                print(f"Getting changes for {disaster_area[0]} {disaster_date.year}")
                get_changes_and_previous(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days)

            print(f"Computing diffs for {disaster_area[0]} {disaster_date.year}")
            compute_changes_diffs(disaster_area[0], disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days)

            print(f"Analysing diffs for {disaster_area[0]} {disaster_date.year}")
            analyse_change_diffs(disaster_area[0], disaster_id)
