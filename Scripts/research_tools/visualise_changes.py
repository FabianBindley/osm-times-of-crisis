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


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_utils import DB_Utils


def get_changes_in_interval(disaster_date, before_after_time_length, disaster_id):
    start_date = disaster_date - timedelta(days=before_after_time_length)
    end_date = disaster_date + timedelta(days=before_after_time_length)

    return db_utils.get_changes_in_interval(start_date, end_date, disaster_id)


def compute_hexagon_counts(multipolygon, changes, resolution):
    
    hex_counts = {}

    # Convert the multipolygon to a LatLngPoly or LatLngMultiPoly
    polygons = []
    for geom in multipolygon.geoms:  # Handle each polygon in the MultiPolygon
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

    # Generate all hexagons that cover the multipolygon
    all_hexagons = h3.h3shape_to_cells(h3_shape, resolution)

    # Ensure all hexagons in the area are included, even with zero counts
    for hex_index in all_hexagons:
        hex_counts[hex_index] = [0,0,0,0]

    # Count hexagons with changes
    for change in changes:
        coords = list(wkb.loads(change[4]).coords)[0]
        lon, lat = coords[0], coords[1]

        if lon == 0 and lat == 0:
            continue
        
        # 0 for creates, 1 for edits, 2 for deletes
        # Get the H3 index of the hexagon and increment the count
        h3_index = h3.latlng_to_cell(lat, lon, resolution)

        # This adds the hexagons where changes were not in the area multipolygon. Useful to check that filtering is working
        if h3_index not in hex_counts:
            hex_counts[h3_index] = [0,0,0,0]

        if h3_index in hex_counts:

            edit_type = change[2]
            if edit_type == "create":
                hex_counts[h3_index][0] += 1
            elif edit_type == "edit":
                hex_counts[h3_index][1] += 1
            else:
                hex_counts[h3_index][2] += 1
            hex_counts[h3_index][3] += 1
    
    return hex_counts

import csv

def save_hex_counts_to_csv(hex_counts, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["h3_index", "create_count", "edit_count", "delete_count","total_count"])
        
        # Write each hexagon's data
        for h3_index, counts in hex_counts.items():
            writer.writerow([h3_index, *counts])
    print(f"Hex counts saved to {file_path}")


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



def plot_multipolygon_on_osm(multipolygon, changes, hexagon_resolution, use_existing):

    centroid = multipolygon.centroid
    # Create a Folium map centered on the provided location
    m = folium.Map(location=(centroid.y, centroid.x), tiles="OpenStreetMap")

    # Convert MultiPolygon to GeoJSON
    geojson = mapping(multipolygon)

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

    file_path = f"./Results/ChangeDensityMapping/data/disaster_{disaster_id}_hexagon_res{hexagon_resolution}.csv"

    # If we don't want to use existing data, or if it doesn't exist, calculate hex count
    if not use_existing or not os.path.exists(file_path):
        # Compute the number of changes in each hexagon and plot them on the map
        hex_counts = compute_hexagon_counts(multipolygon, changes, hexagon_resolution)
        save_hex_counts_to_csv(hex_counts, file_path)
    else:
        hex_counts = load_hex_counts_from_csv(file_path)

    plot_hexagons_on_map(m, hex_counts)

    # Fit the map to the bounding box of the multipolygon
    min_x, min_y, max_x, max_y = multipolygon.bounds
    m.fit_bounds([[min_y, min_x], [max_y, max_x]])

    # Return the map object
    return m

if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    resolutions = {1: 9, 2: 6, 3:6, 4:6, 5:6, 6:6}

    use_db_resolution = False

    for disaster_id in range(5,6):
        start_time = datetime.now()
        # Get the information for the disaster with the given disaster_id
        (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution ) = db_utils.get_disaster_with_id(disaster_id)

        if use_db_resolution:
            resolution = disaster_h3_resolution
        else:
            resolution = resolutions[disaster_id]
        
        print(f"Generating map for {disaster_area} | resolution {resolution}")

        changes = get_changes_in_interval(disaster_date, before_after_time_length=365, disaster_id=disaster_id)

        disaster_multipolygon = wkb.loads(disaster_geojson_encoded)
        m = plot_multipolygon_on_osm(disaster_multipolygon, changes, resolution, use_existing=False)


        m.save(f"./Results/ChangeDensityMapping/charts/disaster_map_{disaster_id}.html")  # Save the map to an HTML file

        """
        img_data = m._to_png(1)
        img = Image.open(io.BytesIO(img_data))
        img.save(f'./Results/ChangeDensityMapping/charts/disaster_map_{disaster_id}.png')
        print(f"Map saved to ./Results/ChangeDensityMapping/charts/disaster_map_{disaster_id}.html")
        """

        print(f"Generating map for id:{disaster_id} took {round(datetime.now().timestamp()-start_time.timestamp(),2)} seconds")

    


    """
    marker_cluster = MarkerCluster()
    for change in changes:
        coords = list(wkb.loads(change[4]).coords)[0]
        lon, lat = coords[0], coords[1]

        if lon != 0 and lat != 0:
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(marker_cluster)

    # Add the marker cluster to the map
    marker_cluster.add_to(m)
    """
