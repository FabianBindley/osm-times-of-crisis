from osmium_tools.BuildingCounterHandler import BuildingCounterHandler

file = "./Data/EmiliaRomagna/EmiliaRomagna-2024-06-11.osm"
#file = "./Data/Broxbourne/Broxbourne-2024-06-11.osm"
# Initialize the handler
handler = BuildingCounterHandler()
print("here")

# Apply the handler to the extract.osm file
handler.apply_file(file)
print("applied")

# Output the result
print("Number of buildings:", handler.building_count)
