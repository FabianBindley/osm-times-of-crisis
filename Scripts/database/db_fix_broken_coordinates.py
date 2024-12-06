from db_utils import DB_Utils
from ElementExtractor import ElementExtractor
from datetime import datetime, timezone
from shapely import wkb
import subprocess
import xml.etree.ElementTree as ET
from BulkImportHandler import Coordinate
from shapely.geometry import LineString

input_files = {
    1: "Data/Broxbourne/BroxbourneNodesWays.osh.pbf",
    2: "Data/EmiliaRomagna/EmiliaRomagnaNodesWays.osh.pbf",
    3: "Data/Haiti/HaitiNodesWays.osh.pbf",
    4: "Data/Haiti/HaitiNodesWays.osh.pbf",
    5: "Data/Haiti/HaitiNodesWays.osh.pbf",
    6: "Data/Nepal/NepalNodesWays.osh.pbf"
}

way_nodes = {}
required_nodes = {}

def get_nodes(node_id, node_version, disaster_id):
    command = [
            "osmium",
            "getid",
            input_files[disaster_id],
            f"n{node_id}",
            "--output-format=osm"
        ]


    # Execute the osmium command
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    osm_data = result.stdout

    # Parse the OSM XML output
    root = ET.fromstring(osm_data)

    # Store versions and coordinates
    node_versions = []

    # Iterate through all node elements
    for node in root.findall(".//node"):
        version = int(node.get("version"))
        if version < node_version:
            try:
                lat = float(node.get("lat"))
                lon = float(node.get("lon"))
                timestamp = node.get("timestamp")
                node_versions.append({
                    "version": version,
                    "coordinates": (lon, lat),
                    "timestamp": timestamp
                })
            except (TypeError, ValueError) as e:
                # Handle missing or invalid lat/lon and move to the next node
                print(f"Skipping node due to invalid lat/lon or version: {node.get('id')}, error: {e}")
                continue

    return node_versions

def get_way_node_refs(way_id, version, disaster_id):
    # Construct the osmium command to get the way by ID
        command = [
            "osmium",
            "getid",
            input_files[disaster_id],
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

def compute_way_centroid(way_nodes):

    coordinates = list(map(lambda node: required_nodes[node], filter(lambda node: node in required_nodes, way_nodes)))

    coordinates = []
    for node in way_nodes:
        assert(type(node) is int)
        if required_nodes[node] is not None:
            coordinates.append(required_nodes[node])


    if len(coordinates) < 2:
        return Coordinate(0, 0)
    centroid = LineString(coordinates).centroid
    return Coordinate(centroid.x, centroid.y)


def process_batch(broken_coord_changes):
    way_nodes = {}
    required_nodes = {}

    for broken_coord_change in broken_coord_changes:
        change_id = broken_coord_change[0]
        change_element_id = broken_coord_change[1]
        change_disaster_id = broken_coord_change[2]
        change_coordinates = broken_coord_change[3]
        change_version = broken_coord_change[4]
        change_element_type = broken_coord_change[5]
        change_element_visible = broken_coord_change[6]

        assert(change_coordinates == "0101000020E610000000000000000000000000000000000000")

        # We now go to the change's osmium file - and get the nodes that are related to the way.
        # Create the handler and apply it to the file


        if change_element_type == "node":
            nodes = get_nodes(change_element_id, change_version, change_disaster_id)
            highest_version_node = max(nodes, key=lambda node: node['version'])

            # We can now update the broken coordinate with the highest version of the node 
            utils.update_change_coordinates(change_id, ( highest_version_node["coordinates"][0], highest_version_node["coordinates"][1]))

        elif change_element_type == "way":
            if change_element_visible:
                # Get the way's nodes and their coordinates
                node_ids = list(map(int, get_way_node_refs(change_element_id, change_version, change_disaster_id)))
                way_nodes[change_id] = node_ids
                for node in node_ids:
                    required_nodes[node] = None
            else:
                change_version -=1 
                while change_version >= 0:
                    node_ids = list(map(int, get_way_node_refs(change_element_id, change_version, change_disaster_id)))
                    if len(node_ids) > 0:
                        break
                    change_version -= 1

                way_nodes[change_id] = node_ids
                for node in node_ids:
                    required_nodes[node] = None
                

def split_into_batches(data, batch_size):
    """
    Split a list into smaller batches of a given size.
    """
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

if __name__ == "__main__":
 
    utils = DB_Utils()
    utils.db_connect()

    batch_size = 1000
    disaster_id = 2
    
    #broken_coord_changes = utils.get_broken_coordinates()
    """
    # [(64180249, '0101000020E6100000C27751AAB31B5540CE797C314AAC3B40', True), (64180250, '0101000020E610000000000000000000000000000000000000', False)]
    # First Fix Broken Nodes
    for change in broken_coord_changes:
        id = change[0]
        element_id = change[1]
        diaster_id = change[2]
        coordinates = change[3]
 
        changes_same_element_id = utils.get_changes_same_element_id(element_id, diaster_id)

        if len(changes_same_element_id) > 0:
            for change_same_element_id in changes_same_element_id:

                update_id = change_same_element_id[0]
                update_coordinates = change_same_element_id[1]
                
                if update_coordinates != "0101000020E610000000000000000000000000000000000000" and update_id!=id:
                    coords = list(wkb.loads(update_coordinates).coords)[0]
                    utils.update_change_coordinates(id, ( coords[0], coords[1]))
                    print(f"Updated id: {id} element_id: {element_id}")
                    break

    """
    start_time = datetime.now()
    # Both Ways and Nodes can be broken. Ways cannot be fixed if their nodes are broken so it is essential that they be fixed first. This can be done by running the program twice
    broken_coord_changes = utils.get_broken_coordinates(disaster_id)
    batch_num = 1
    total_batches = (len(broken_coord_changes) + batch_size - 1) // batch_size


    for batch in split_into_batches(broken_coord_changes, batch_size):
        print(f"Processing Batch {batch_num}/{total_batches}")

        elapsed_time = datetime.now().timestamp() - start_time.timestamp()
        process_batch(batch)

        batch_num+=1
        minutes, seconds = divmod(int(elapsed_time), 60)
        print(f"Time Elapsed: {minutes}m {seconds}s")

        average_time_per_batch = elapsed_time / batch_num  

        estimated_time_remaining = average_time_per_batch * (total_batches - batch_num)
        # Convert estimated time remaining to minutes and seconds
        minutes, seconds = divmod(int(estimated_time_remaining), 60)
        print(f"Estimated time remaining: {minutes}m {seconds}s")

    print(way_nodes)
    print(required_nodes)
    # Get all the coordinates for the nodes we're looking at
    handler = ElementExtractor(required_nodes)
    handler.apply_file(input_files[disaster_id])

    for way_change_id, nodes in way_nodes.items():

        # Compute the way centroid
        centroid = compute_way_centroid(nodes)
        # Update the coordinate in the DB
        #print(f"Updating {way_change_id} {centroid.lon} {centroid.lat}")
        utils.update_change_coordinates(way_change_id, (centroid.lon, centroid.lat))






    