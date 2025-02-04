import sys
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

def load_hex_counts_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f"Hex Count File does not exist: {file_path}")
        return {}

    hex_counts = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            h3_index = row["h3_index"]
            counts = [int(row["create_count"]), int(row["edit_count"]), int(row["delete_count"]), int(row["total_count"])]
            hex_counts[h3_index] = counts
    print(f"Hex counts loaded from {file_path}")
    return hex_counts

def plot_hexagons_on_map(m, hex_counts):


    min_opacity = 0.2
    max_opacity = 0.8


    # Determine the minimum and maximum counts
    min_count = 0
    max_count = max(count[3] for count in hex_counts.values())

    # Avoid division by zero if all counts are the same
    count_range = max_count - min_count if max_count > min_count else 1

    for hex_index, count in hex_counts.items():
        create_count = count[0]
        edit_count = count[1]
        delete_count = count[2]
        total_count = count[3]

        # Apply square root scaling
        sqrt_scaled_count = math.sqrt(total_count)

        # Apply log scale to total_count
        log_scaled_count = math.log(total_count + 1)  # Add 1 to avoid log(0)

        # Linear normalized scale
        normalized_opacity = (total_count - min_count) / count_range
        # Sqrt normalized scale
        #normalized_opacity = sqrt_scaled_count / math.sqrt(max_count + 1)
        # Log normalized scale
        #normalized_opacity = (log_scaled_count - math.log(min_count + 1)) / (math.log(max_count + 1) - math.log(min_count + 1))

        # Scale opacity to the desired range
        fill_opacity =  (normalized_opacity * (max_opacity - min_opacity))

        # Get the hexagon boundary for the H3 index
        hex_boundary = h3.cell_to_boundary(hex_index)  # Get (lat, lon) tuples

        # Format boundary for Folium (Folium expects a list of lists)
        formatted_boundary = [(lat, lon) for lat, lon in hex_boundary]

        # Add hexagon to the map
        folium.Polygon(
            locations=formatted_boundary,  # Hexagon vertices
            color="black",
            weight=0.5,
            fill=True,
            fill_color="red",
            fill_opacity=fill_opacity,  # Use calculated opacity
            popup=folium.Popup(f"C: {create_count}  E: {edit_count} D: {delete_count} T: {total_count}",  min_width=150, max_width=150)  # Popup showing change count
        ).add_to(m)


def generate_map(disaster_id, disaster_geojson_encoded, resolution, pre_disaster_days, post_disaster_days):
    disaster_multipolygon = wkb.loads(disaster_geojson_encoded)

    centroid = disaster_multipolygon.centroid
    # Create a Folium map centered on the provided location
    m = folium.Map(location=(centroid.y, centroid.x), tiles="OpenStreetMap")

    # Convert MultiPolygon to GeoJSON
    geojson = mapping(disaster_multipolygon)

    # Add the MultiPolygon as a layer
    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "red",
            "weight": 1,
            "fillOpacity": 0.05,
        },
    ).add_to(m)

    # Add the hexagons
    file_path = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/{pre_disaster_days}_{post_disaster_days}_{resolution}_hex_count.csv"
    hex_counts = load_hex_counts_from_csv(file_path)

    plot_hexagons_on_map(m, hex_counts)

    # Fit the map to the bounding box of the multipolygon
    min_x, min_y, max_x, max_y = disaster_multipolygon.bounds
    m.fit_bounds([[min_y, min_x], [max_y, max_x]])

    # Save the charts
    if not os.path.exists(f"Results/ChangeDensityMapping/disaster{disaster_id}/charts"):
        os.makedirs(f"Results/ChangeDensityMapping/disaster{disaster_id}/charts")

    m.save(f"Results/ChangeDensityMapping/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_{resolution}_count_changes.html")
    print(f"Results/ChangeDensityMapping/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_{resolution}_count_changes.html")
    # Save the charts
    if not os.path.exists(f"visualisation-site/public/ChangeDensityMapping/disaster{disaster_id}/charts"):
        os.makedirs(f"visualisation-site/public/ChangeDensityMapping/disaster{disaster_id}/charts")
    
    m.save(f"visualisation-site/public/ChangeDensityMapping/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_{resolution}_count_changes.html")

if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define the periods before and after the disaster we want to count for. Pre-disaster can be negative to only count after disaster
    disaster_days = [(365,365), (365,0),(180,365), (0,30), (0,60)]
    disaster_days = [(365,365)]
    
    resolutions = [6,7,8]
    for disaster_day_tuple in disaster_days:
        for disaster_id in range(2,7):
            for resolution in resolutions:

                (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution ) = db_utils.get_disaster_with_id(disaster_id)
                print(f"Generating map for {disaster_area[0]} {disaster_date.year} | resolution {resolution}")
                generate_map(disaster_id, disaster_geojson_encoded, resolution, disaster_day_tuple[0], disaster_day_tuple[1])
