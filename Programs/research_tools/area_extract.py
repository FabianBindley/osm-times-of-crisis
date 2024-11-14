import sys
import os

# Add the parent directory of research_tools to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from osmium_tools.OsmiumExtract import OsmiumExtract


history_file = "./Data/Haiti/haiti-and-domrep-internal.osh.pbf"
output_file = "./Data/Haiti/haiti.osh.pbf"
geojson_file= "./Data/GeocodedBoundaries/Haiti-geocode-boundary.geojson"



# Initialize the handler
handler = OsmiumExtract()

# Apply the handler to the extract.osm file
handler.run_extract(history_file, output_file, geojson_file, True)

