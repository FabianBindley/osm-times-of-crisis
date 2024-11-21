import osmium
from db_utils import DB_Utils
from datetime import datetime, timezone, timedelta
from shapely.geometry import shape, Point, MultiPolygon, Polygon, LineString
import json

class Coordinate:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

class BulkImportHandler(osmium.SimpleHandler):

    def __init__(self, start_date, end_date, geojson_path, geojson_filtered, disaster_id, connection):
        # For now the interval is daily, from the start time to the end time
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.geojson_filtered = geojson_filtered
        self.insert_list = []
        self.db_utils = DB_Utils()
        self.success_count = 0
        self.filtered_count = 0
        self.flush_threshold = 10000
        self.failed_count = 0
        self.location_cache = {}
        self.disaster_id = disaster_id
        self.connection = connection

        # Load GeoJSON and create a MultiPolygon from the geometries
        with open(geojson_path) as f:
            geojson_data = json.load(f)

            # Extract the geometry and create the shape
            geometry = geojson_data['geometry']
            self.area_multipolygon = shape(geometry)


    def compute_way_centroid(self, way):

        coordinates = [(self.location_cache[node.ref].lon, self.location_cache[node.ref].lat) for node in way.nodes if node.ref in self.location_cache]
        if len(coordinates) < 2:
            return Coordinate(0, 0)
        centroid = LineString(coordinates).centroid
        return Coordinate(centroid.x, centroid.y)

    def initiate_insert(self, obj):

        # Check that the objects coordinates are inside the geojson multipolygon, 
        if isinstance(obj, osmium.osm.Node):
            if self.point_in_geojson(obj):
                self.add_tuple(obj, "node")

        
        # Check that the way has a node within the MultiPolygon
        elif isinstance(obj, osmium.osm.Way):
            for node_ref in obj.nodes:
                if not node_ref.ref in self.location_cache:
                    continue
                if self.point_in_geojson(self.location_cache[node_ref.ref]):
                    self.add_tuple(obj, "way")
                    break

    
    def add_tuple(self, obj, obj_type):
        if len(self.insert_list) >= self.flush_threshold:
            self.flush_inserts()
            self.insert_list = []
        
        if not obj.visible:
            edit_type = "delete"
            coordinate = self.location_cache[obj.id] if isinstance(obj, osmium.osm.Node) and obj.id in self.location_cache else None
        elif obj.version == 1:
            edit_type = "create"
            coordinate = Coordinate(obj.location.lon, obj.location.lat) if isinstance(obj, osmium.osm.Node) else self.compute_way_centroid(obj)
        else:
            edit_type = "edit"
            coordinate = Coordinate(obj.location.lon, obj.location.lat) if isinstance(obj, osmium.osm.Node) else self.compute_way_centroid(obj)

        try:
            self.insert_list.append((obj.id, edit_type, obj_type, int(obj.timestamp.timestamp()), self.disaster_id, obj.version, obj.visible, obj.changeset, json.dumps(dict(obj.tags)),
                                  True if "building" in obj.tags else False, True if "highway" in obj.tags else False, 
                                  coordinate.lon if coordinate else 0, coordinate.lat if coordinate else 0, obj.uid))
            
            self.success_count += 1
        except:
            print(f"Failed to add Object {obj.id}")
            self.failed_count += 1       
        

    def flush_inserts(self):
        self.db_utils.insert_data(self.insert_list, self.success_count, self.connection)
        self.location_cache = {}
 

        
    
    def point_in_geojson(self, obj):
        if self.geojson_filtered:
            try:
                if self.area_multipolygon.contains(Point(obj.lon, obj.lat)):
                    return True
                else:
                    self.filtered_count += 1
                    return False
            except:
                return True
        else:
            return True


    def print_statistics(self):
        print(f"Success: {self.success_count} Failed: {self.failed_count} Filtered: {self.filtered_count}")

    def node(self, n):
        # Cache the location in case needed by a delete

        if self.start_date <= n.timestamp <= self.end_date:
            if n.visible:
                self.location_cache[n.id] = Coordinate(n.location.lon, n.location.lat)
        
            self.initiate_insert(n)


    def way(self, w):
        if self.start_date <= w.timestamp <= self.end_date:
            self.initiate_insert(w)




