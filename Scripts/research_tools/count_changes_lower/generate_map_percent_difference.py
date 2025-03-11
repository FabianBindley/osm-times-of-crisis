import sys
import os
import ast
from datetime import datetime, timedelta
from shapely import wkb

from shapely.geometry import mapping
from shapely.ops import transform
import math
import folium

import h3
from collections import Counter
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def load_percent_differences_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f"Percent Difference File does not exist: {file_path}")
        return {}

    percent_differences = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            h3_index = row["h3_index"]
            percent_difference_row = [float(row["creates_percent_difference"]), float(row["edits_percent_difference"]), float(row["deletes_percent_difference"]), float(row["total_percent_difference"])]
            percent_differences[h3_index] = percent_difference_row

    print(f"Percent Differences loaded from {file_path}")
    return percent_differences



def plot_hexagons_on_map(m, percent_differences):
    min_opacity = 0.01
    max_opacity = 0.75
    sigmoid_scale = 0.01  # Smaller values compress outliers more; adjust as needed

    # Helper function to apply sigmoid scaling
    def sigmoid(value, scale):
        return 1 / (1 + math.exp(-scale * value))

    for hex_index, percent_difference in percent_differences.items():
        creates_percent_difference = percent_difference[0]
        edits_percent_difference = percent_difference[1]
        deletes_percent_difference = percent_difference[2]
        total_percent_difference = percent_difference[3]

        # Apply sigmoid scaling to the total percent difference. Scale so that in range [-1, 1]
        scaled_value = sigmoid(total_percent_difference, sigmoid_scale) * 2 -1 

        if scaled_value > 0:
            fill_colour = "red"
        else:
            fill_colour = "green"
        # Normalize scaled value to the opacity range
        fill_opacity = min_opacity + (abs(scaled_value) * (max_opacity - min_opacity))

        # Get the hexagon boundary for the H3 index
        hex_boundary = h3.cell_to_boundary(hex_index)

        # Format boundary for Folium (Folium expects a list of lists)
        formatted_boundary = [(lat, lon) for lat, lon in hex_boundary]

        # Add hexagon to the map
        folium.Polygon(
            locations=formatted_boundary,
            color="black",
            weight=0.5,
            fill=True,
            fill_color=fill_colour,
            fill_opacity=fill_opacity,
            popup=folium.Popup(
                f"C: {creates_percent_difference}%  E: {edits_percent_difference}%  D: {deletes_percent_difference}%  T: {total_percent_difference}%",
                min_width=150, max_width=150,
            ),
        ).add_to(m)



def generate_map(disaster_id, disaster_geojson_encoded, resolution, pre_disaster_days, imm_disaster_days, post_disaster_days, disaster_period_tuple):
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
            "fillOpacity": 0.03,
        },
    ).add_to(m)

    # Add the hexagons
    file_path = f"Results/ChangeDensityMapping/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{resolution}_{disaster_period_tuple[0]}_{disaster_period_tuple[1]}_percent_difference.csv"
    percent_differences = load_percent_differences_from_csv(file_path)

    plot_hexagons_on_map(m, percent_differences)

    # Fit the map to the bounding box of the multipolygon
    min_x, min_y, max_x, max_y = disaster_multipolygon.bounds
    m.fit_bounds([[min_y, min_x], [max_y, max_x]])

    # Save the charts
    if not os.path.exists(f"Results/ChangeDensityMapping/disaster{disaster_id}/charts"):
        os.makedirs(f"Results/ChangeDensityMapping/disaster{disaster_id}/charts")

    save_file_path = f"Results/ChangeDensityMapping/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{resolution}_{disaster_period_tuple[0]}_{disaster_period_tuple[1]}_percent_difference.html"
    m.save(save_file_path)
    print(f"Generated map: {save_file_path}")

    # Save the charts
    if not os.path.exists(f"visualisation-site/public/ChangeDensityMapping/disaster{disaster_id}/charts"):
        os.makedirs(f"visualisation-site/public/ChangeDensityMapping/disaster{disaster_id}/charts")
    
    m.save(f"visualisation-site/public/ChangeDensityMapping/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{resolution}_{disaster_period_tuple[0]}_{disaster_period_tuple[1]}_percent_difference.html")
    


if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define the periods before and after the disaster we want to count for. Pre-disaster can be negative to only count after disaster
    disaster_days = [(365,60,365)]
    disaster_periods = [("pre","imm"),("pre","post")]
    
    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = range(13,14)
        disaster_ids = [6,7,8,9,10]
        print("Disaster IDs defined:", disaster_ids)

    resolutions = [6,7,8,9]

    for disaster_day_tuple in disaster_days:
        for disaster_period_tuple in disaster_periods:
            for disaster_id in disaster_ids:
                for resolution in resolutions:

                    if resolution == 9 and disaster_id not in [ 10, 14, 15, 18]:
                        continue

                    (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution,_ ) = db_utils.get_disaster_with_id(disaster_id)
                    print(f"Generating map for {disaster_area[0]} {disaster_date.year} | resolution {resolution}")
                    generate_map(disaster_id, disaster_geojson_encoded, resolution, disaster_day_tuple[0], disaster_day_tuple[1], disaster_day_tuple[2], disaster_period_tuple)
