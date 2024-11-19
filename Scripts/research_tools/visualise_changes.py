import sys
import os
from datetime import datetime
from shapely import wkb

import matplotlib.pyplot as plt
from shapely.geometry import mapping
from shapely.ops import transform
from PIL import Image
import io

import folium


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_utils import DB_Utils


def plot_multipolygon_on_osm(multipolygon, map_center):
    # Create a Folium map centered on the provided location
    m = folium.Map(location=map_center, tiles="OpenStreetMap")

    # Convert MultiPolygon to GeoJSON
    geojson = mapping(multipolygon)

    # Add the MultiPolygon as a layer
    folium.GeoJson(
        geojson,
        style_function=lambda x: {
            "fillColor": "blue",
            "color": "red",
            "weight": 1,
            "fillOpacity": 0.1,
        },
    ).add_to(m)

    min_x, min_y, max_x, max_y = multipolygon.bounds
    m.fit_bounds([[min_y, min_x], [max_y, max_x]])

    # Return the map object
    return m

if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    for disaster_id in range(1,7):
        # Get the information for the disaster with the given disaster_id
        (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date ) = db_utils.get_disaster_with_id(disaster_id)
        print(disaster_country, disaster_area, disaster_date)

        disaster_multipolygon = wkb.loads(disaster_geojson_encoded)
        centroid = disaster_multipolygon.centroid

        m = plot_multipolygon_on_osm(disaster_multipolygon, (centroid.y, centroid.x))
        m.save(f"./Results/ChangeDensityMapping/disaster_map_{disaster_id}.html")  # Save the map to an HTML file

        img_data = m._to_png(1)
        img = Image.open(io.BytesIO(img_data))
        img.save(f'./Results/ChangeDensityMapping/disaster_map_{disaster_id}.png')


        print(f"Map saved to ./Results/ChangeDensityMapping/disaster_map_{disaster_id}.html")




    


