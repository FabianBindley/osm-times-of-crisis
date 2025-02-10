import sys
import ast
import os
from datetime import datetime, timedelta
from shapely import wkb

import matplotlib.pyplot as plt
from shapely.geometry import mapping
from shapely.ops import transform
from PIL import Image
import io
import math
import folium
import pandas as pd
import h3
from collections import Counter
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def changes_for_interval(disaster_id, disaster_date, pre_disaster_days, post_disaster_days):
    pre_disaster = timedelta(pre_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    interval_start_date = disaster_date - pre_disaster
    interval_end_date = disaster_date + post_disaster + timedelta(days=1)
    

    return db_utils.get_changes_in_interval(interval_start_date, interval_end_date, disaster_id)


def save_hex_counts_to_csv(hex_counts, file_path):
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["h3_index", "create_count", "edit_count", "delete_count","total_count"])
        
        # Write each hexagon's data
        for h3_index, counts in hex_counts.items():
            writer.writerow([h3_index, *counts])
    print(f"Hex counts saved to {file_path}")

def generate_counts_for_polygons(changes, disaster_id, disaster_geojson_encoded, resolution, pre_disaster_days, post_disaster_days):
    disaster_multipolygon = wkb.loads(disaster_geojson_encoded)

    hex_counts = {}
    # Convert the multipolygon to a LatLngPoly or LatLngMultiPoly
    polygons = []
    for geom in disaster_multipolygon.geoms:  # Handle each polygon in the MultiPolygon
        geojson_poly = mapping(geom)  # Convert Shapely geometry to GeoJSON
        # Reverse coordinates for the outer ring and holes
        outer = [(lat, lon) for lon, lat in geojson_poly['coordinates'][0]]
        holes = [[(lat, lon) for lon, lat in hole] for hole in geojson_poly['coordinates'][1:]]
        polygons.append(h3.LatLngPoly(outer, *holes))

    # Combine polygons into a LatLngMultiPoly if there are multiple
    if len(polygons) > 1:
        h3_shape = h3.LatLngMultiPoly(*polygons)
    else:
        h3_shape = polygons[0]

    # Get all hexagons that cover the multipolygon
    all_hexagons = h3.h3shape_to_cells(h3_shape, resolution)

    # Ensure all hexagons in the area are included, even with zero counts
    for hex_index in all_hexagons:
        hex_counts[hex_index] = [0,0,0,0]


    # Count the changes in the hexagons
    for change in changes:
        coords = list(wkb.loads(change[4]).coords)[0]
        lon, lat = coords[0], coords[1]

        if lon == 0 and lat == 0:
            continue
        
        # 0 for creates, 1 for edits, 2 for deletes
        # Get the H3 index of the hexagon and increment the count
        h3_index = h3.latlng_to_cell(lat, lon, resolution)

        # This adds the hexagons where changes were not in the area multipolygon. Useful to check that filtering is working
        # if h3_index not in hex_counts:
            #hex_counts[h3_index] = [0,0,0,0]

        if h3_index in hex_counts:

            edit_type = change[2]
            if edit_type == "create":
                hex_counts[h3_index][0] += 1
            elif edit_type == "edit":
                hex_counts[h3_index][1] += 1
            else:
                hex_counts[h3_index][2] += 1
            hex_counts[h3_index][3] += 1

     # Save the counts
    if not os.path.exists(f"Results/ChangeDensityMapping/disaster{disaster_id}/data"):
        os.makedirs(f"Results/ChangeDensityMapping/disaster{disaster_id}/data")

    file_path = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/{pre_disaster_days}_{post_disaster_days}_{resolution}_hex_count.csv"
    save_hex_counts_to_csv(hex_counts, file_path)

def compute_percent_diff(pre, post, to_percent_multiplier):
    divisor = 1 if pre == 0 else pre
    return (post - pre) / divisor * to_percent_multiplier



def generate_percentage_difference_for_polygons(disaster_id, disaster_geojson_encoded, resolution, pre_disaster_days, post_disaster_days):
    
    # First, need to either load in the existing CSV files or create them
    file_path_pre = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/{pre_disaster_days}_0_{resolution}_hex_count.csv"
    file_path_post = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/0_{post_disaster_days}_{resolution}_hex_count.csv"
    print(file_path_pre)
    print(file_path_post)
    if not os.path.exists(file_path_pre):
        print(f"Generating {pre_disaster_days} 0")
        changes = changes_for_interval(disaster_id, disaster_date, pre_disaster_days, 0)
        generate_counts_for_polygons(changes, disaster_id, disaster_geojson_encoded, resolution, pre_disaster_days, 0)

    if not os.path.exists(file_path_post):
        print(f"Generating 0 {post_disaster_days}")
        changes = changes_for_interval(disaster_id, disaster_date, 0, post_disaster_days)
        generate_counts_for_polygons(changes, disaster_id, disaster_geojson_encoded, resolution, 0, post_disaster_days)

    print(f"Got files for {pre_disaster_days} {post_disaster_days}")
    
    # For each hexagon, compute the pre_disaster_changes_per_day, then use to compute the post_disaster_changes_per_day -
    data_pre = pd.read_csv(file_path_pre)
    data_post = pd.read_csv(file_path_post)

    to_percent_multiplier = 100

    # Calculate changes per day for pre-disaster period
    data_pre["creates_per_day"] = data_pre["create_count"] / pre_disaster_days
    data_pre["edits_per_day"] = data_pre["edit_count"] / pre_disaster_days
    data_pre["deletes_per_day"] = data_pre["delete_count"] / pre_disaster_days
    data_pre["total_per_day"] = data_pre["total_count"] / pre_disaster_days

    data_post["creates_per_day"] = data_post["create_count"] / pre_disaster_days
    data_post["edits_per_day"] = data_post["edit_count"] / pre_disaster_days
    data_post["deletes_per_day"] = data_post["delete_count"] / pre_disaster_days
    data_post["total_per_day"] = data_post["total_count"] / pre_disaster_days

    counter = 0
    percent_difference_changes_per_day = []
    for _, post_row in data_post.iterrows():
        hex_id = post_row["h3_index"]
        pre_row = data_pre[data_pre["h3_index"] == hex_id].iloc[0]

        creates = compute_percent_diff(pre_row["creates_per_day"], post_row["creates_per_day"], to_percent_multiplier)
        edits = compute_percent_diff(pre_row["edits_per_day"], post_row["edits_per_day"], to_percent_multiplier)
        deletes = compute_percent_diff(pre_row["deletes_per_day"], post_row["deletes_per_day"], to_percent_multiplier)
        total = compute_percent_diff(pre_row["total_per_day"], post_row["total_per_day"], to_percent_multiplier)

        percent_diff = {
            "h3_index": hex_id,
            "creates_percent_difference": round(creates,2),
            "edits_percent_difference": round(edits, 2),
            "deletes_percent_difference": round(deletes, 2),
            "total_percent_difference": round(total, 2)
        }

        percent_difference_changes_per_day.append(percent_diff)

    # Write the results to CSV
    percent_difference_changes_per_day_file_path = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/{pre_disaster_days}_{post_disaster_days}_{resolution}_percent_difference.csv"
    headers = ["h3_index", "creates_percent_difference", "edits_percent_difference", "deletes_percent_difference","total_percent_difference"]
    with open(percent_difference_changes_per_day_file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(percent_difference_changes_per_day)


if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()


    resolutions = [6,7,8,9]
    #resolutions = [7]

    # Define the periods before and after the disaster we want to count for. Pre-disaster can be negative to only count after disaster
    disaster_days = [(365,60,365)]
    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = range(13,14)
        print("Disaster IDs defined:", disaster_ids)

    for disaster_day_tuple in disaster_days:
        for disaster_id in disaster_ids:
            for resolution in resolutions:

                if resolution == 9 and disaster_id not in [ 10, 14, 15, 18]:
                    continue

                (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution ) = db_utils.get_disaster_with_id(disaster_id)
                print(f"Generating counts for {disaster_area[0]} {disaster_date.year} | resolution {resolution}")

                generate_percentage_difference_for_polygons(disaster_id, disaster_geojson_encoded, resolution, disaster_day_tuple[0], disaster_day_tuple[2])
