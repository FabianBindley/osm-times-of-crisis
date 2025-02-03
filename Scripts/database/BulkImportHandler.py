import osmium
from db_utils import DB_Utils
from datetime import datetime, timezone, timedelta
from shapely.geometry import shape, Point, MultiPolygon, Polygon, LineString
import json
import subprocess
import xml.etree.ElementTree as ET

class Coordinate:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

class BulkImportHandler(osmium.SimpleHandler):

    def __init__(self, start_date, end_date, geojson_path, geojson_filtered, disaster_id, place, year, connection, input_file, missing_changes_set, insert_normal_changes, insert_missing_changes, three_years_pre):
        # For now the interval is daily, from the start time to the end time
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.geojson_filtered = geojson_filtered
        self.insert_list = []
        self.db_utils = DB_Utils()
        self.success_count = 0
        self.filtered_count = 0
        self.flush_threshold = 20000
        self.failed_count = 0
        self.location_cache = {}
        self.disaster_id = disaster_id
        self.connection = connection
        self.input_file = input_file
        # Import missing previous changes is useful for the analysis where we compare the difference between existing and previous changes
        self.missing_changes_set = missing_changes_set 
        self.insert_normal_changes = insert_normal_changes
        self.insert_missing_changes = insert_missing_changes
        self.three_years_pre = three_years_pre


        # Load GeoJSON and create a MultiPolygon from the geometries
        if "ManuallyDefined" in geojson_path:
            self.area_multipolygon = self.load_geometry_manually_defined(place, year)
        else:
            self.area_multipolygon = self.load_geometry_geocded(place)

    def load_geometry_geocded(self, place):
        geojson_path = f"./Data/GeocodedBoundaries/{place}-geocode-boundary.geojson"
        # Load GeoJSON and create a MultiPolygon from the geometries
        with open(geojson_path) as f:
            geojson_data = json.load(f)

        return shape(geojson_data['geometry'])

    def load_geometry_manually_defined(self, place, year):
        if place != "Haiti":
            suffix = place
        else:
            suffix = place+year
        geojson_path = f"./Data/{place}/{suffix}ManuallyDefined.geojson"
        # Load GeoJSON and create a MultiPolygon from the geometries
        with open(geojson_path) as f:
            geojson_data = json.load(f)
     
        return shape(geojson_data["features"][0]['geometry'])

    def get_way_previous_version_coordinate(self, obj):
        element_id = obj.id
        previous_version = obj.version
        previous_version -= 1
        node_ids = []

        # Look back at previous versions of the way and get its nodes
        while previous_version >= 0:
            node_ids = list(map(int, self.get_way_node_refs(element_id, previous_version)))
            if len(node_ids) > 0:
                break
            change_version -= 1

        if len(node_ids) == 0:
            return Coordinate(0,0)
        
        # Get the node coordinates from the location cache

        coordinates = [(coord.lon, coord.lat) for coord in filter(None, map(lambda node_id: self.location_cache.get(node_id, None), node_ids))]
        centroid = LineString(coordinates).centroid
        return Coordinate(centroid.x, centroid.y)
        

    def get_way_node_refs(self, way_id, version):
    # Construct the osmium command to get the way by ID
        command = [
            "osmium",
            "getid",
            self.input_file,
            f"w{way_id}",
            "--output-format=osm"
        ]

        # Execute the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        osm_data = result.stdout

        # Parse the OSM XML output
        root = ET.fromstring(osm_data)

        # Find the way element with the specific version
        for way in root.findall(".//way"):
            if int(way.get("version", 0)) == version:
                # Extract all node references
                node_refs = [nd.get("ref") for nd in way.findall(".//nd")]
                return node_refs

        # If no matching version is found, return an empty list
        return []


    def compute_way_centroid(self, way):

        coordinates = [(self.location_cache[node.ref].lon, self.location_cache[node.ref].lat) for node in way.nodes if node.ref in self.location_cache]
        if len(coordinates) < 2:
            return Coordinate(0, 0)
        centroid = LineString(coordinates).centroid
        return Coordinate(centroid.x, centroid.y)



    def initiate_insert(self, obj):

        # Check that the objects coordinates are inside the geojson multipolygon, 
        if isinstance(obj, osmium.osm.Node):
            #if self.point_in_geojson(obj):
            self.add_tuple(obj, "node")

        
        # Check that the way has a node within the MultiPolygon
        elif isinstance(obj, osmium.osm.Way):
            self.add_tuple(obj, "way")
            """
            found_node = False
            for node_ref in obj.nodes:

                if node_ref.ref in self.location_cache:
                    
                    found_node = True
                    if self.point_in_geojson(self.location_cache[node_ref.ref]):
                        self.add_tuple(obj, "way")
                        break
            
            # If we didn't find a node in the location cache, add the node for now and we will update its coordinates and filter it out later.
            if not found_node:
                self.add_tuple(obj, "way")
            """
    
    def add_tuple(self, obj, obj_type):
        if len(self.insert_list) >= self.flush_threshold:
            self.flush_inserts()
            self.insert_list = []
        
        if not obj.visible:
            edit_type = "delete"
            if isinstance(obj, osmium.osm.Node) and obj.id in self.location_cache:
                coordinate = self.location_cache[obj.id]
            else:
                #coordinate = self.get_way_previous_version_coordinate(obj)
                coordinate = None

        elif obj.version == 1:
            edit_type = "create"
            coordinate = Coordinate(obj.location.lon, obj.location.lat) if isinstance(obj, osmium.osm.Node) else self.compute_way_centroid(obj)
        else:
            edit_type = "edit"
            coordinate = Coordinate(obj.location.lon, obj.location.lat) if isinstance(obj, osmium.osm.Node) else self.compute_way_centroid(obj)

        try:
            self.insert_list.append((obj.id, edit_type, obj_type, int(obj.timestamp.timestamp()), self.disaster_id, obj.version, obj.visible, obj.changeset, json.dumps(dict(obj.tags)),
                                  True if "building" in obj.tags else False, True if "highway" in obj.tags else False, 
                                  coordinate.lon if coordinate else 0, coordinate.lat if coordinate else 0, obj.uid, False))
            
            self.success_count += 1
        except:
            print(f"Failed to add Object {obj.id}")
            self.failed_count += 1       
        

    def flush_inserts(self):
        # Dont insert into changes if 3 years pre, but always insert into 3 years pre
        self.db_utils.insert_data(self.insert_list, self.success_count, self.connection, self.three_years_pre)
        if not self.three_years_pre:
            self.db_utils.insert_data(self.insert_list, self.success_count, self.connection, True)
 
        
    
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
        # Cache the node in case needed
        if n.visible:
            self.location_cache[n.id] = Coordinate(n.location.lon, n.location.lat)
            
        if self.insert_normal_changes:
            # Add the node if it is within the designated time
            if self.start_date <= n.timestamp <= self.end_date:        
                self.initiate_insert(n)

        if self.insert_missing_changes:
            # Check if the node is in the missing previous changes set
            if (n.id,n.version) in self.missing_changes_set:
                self.initiate_insert(n)


    def way(self, w):
        if self.insert_normal_changes:
            # Add the way if it is within the designated time
            if self.start_date <= w.timestamp <= self.end_date:
                self.initiate_insert(w)

        if self.insert_missing_changes:
            # Check if the way is in the missing previous changes set
            if (w.id,w.version) in self.missing_changes_set:
                self.initiate_insert(w)



