import osmium
from db_utils import DB_Utils
from datetime import datetime, timezone, timedelta
from shapely.geometry import shape, Point, MultiPolygon, Polygon
import json

class BulkUpdateHandler(osmium.SimpleHandler):

    def __init__(self, start_date, end_date, geojson_path, geojson_filtered, disaster_id,  column_to_update):
        # For now the interval is daily, from the start time to the end time
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.geojson_filtered = geojson_filtered
        self.update_list = []
        self.db_utils = DB_Utils()
        self.success_count = 0
        self.filtered_count = 0
        self.flush_threshold = 10000
        self.failed_count = 0
        self.location_cache = {}
        self.disaster_id = disaster_id
        self.column_to_update = column_to_update

        # Load GeoJSON and create a MultiPolygon from the geometries
        with open(geojson_path) as f:
            geojson_data = json.load(f)

            # Extract the geometry and create the shape
            geometry = geojson_data['geometry']
            self.area_multipolygon = shape(geometry)

    def add_tuple(self, obj):
        if len(self.update_list) >= self.flush_threshold:
            self.flush_updates()
            self.update_list = []
        
        self.update_list.append((getattr(obj, self.column_to_update), obj.id, obj.version))
        

    def flush_updates(self):
        self.success_count += self.db_utils.update_data(self.update_list,  self.column_to_update)

    def print_statistics(self):
        print(f"Success: {self.success_count}")


    def node(self, n):
        if self.start_date <= n.timestamp <= self.end_date:
            self.add_tuple(n)


    def way(self, w):
        if self.start_date <= w.timestamp <= self.end_date:
            self.add_tuple(w)




