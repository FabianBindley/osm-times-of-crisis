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

if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define the periods before and after the disaster we want to count for. Pre-disaster can be negative to only count after disaster
    disaster_days = [(365,365), (365,0),(180,365), (0,30), (0,60)]
    disaster_days = [(365,365)]
    #disaster_days = [(0,30), (0,60)]

    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = range(13,19)
        print("Disaster IDs defined:", disaster_ids)
    
    resolutions = [6,7,8,9]
    #resolutions = [7]
    for disaster_day_tuple in disaster_days:
        for disaster_id in disaster_ids:
            for resolution in resolutions:
                if resolution == 9 and disaster_id not in [10,14,15,18]:
                    continue

                (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution ) = db_utils.get_disaster_with_id(disaster_id)
                print(f"Generating counts for {disaster_area[0]} {disaster_date.year} | resolution {resolution}")
                changes = changes_for_interval(disaster_id, disaster_date, disaster_day_tuple[0], disaster_day_tuple[1])
                
                generate_counts_for_polygons(changes, disaster_id, disaster_geojson_encoded, resolution, disaster_day_tuple[0], disaster_day_tuple[1])
