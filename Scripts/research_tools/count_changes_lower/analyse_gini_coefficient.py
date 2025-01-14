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
from generate_maps_count_changes import load_hex_counts_from_csv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils




# To analyse the gini coefficient - the changes per hexagon for the selected disasters must already have been completed
if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define the periods before and after the disaster we want to count for. Pre-disaster can be negative to only count after disaster
    disaster_days = [(365,365)]

    resolutions = [6,7,8]
    for disaster_day_tuple in disaster_days:
        for disaster_id in range(6,7):
            for resolution in resolutions:

                (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution ) = db_utils.get_disaster_with_id(disaster_id)
                
                print(f"Generating cougini coefficients for {disaster_area[0]} {disaster_date.year} | resolution {resolution}")
                hex_counts = load_hex_counts_from_csv(f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/{disaster_day_tuple[0]}_{disaster_day_tuple[1]}_{resolution}_hex_count.csv")
                
