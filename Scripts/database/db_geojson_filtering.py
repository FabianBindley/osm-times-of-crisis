from db_utils import DB_Utils
from datetime import datetime

def validate_coordinates(disaster_id):

    # Get the information for the disaster with the given disaster_id
    (_, disaster_country, disaster_area, disaster_geojson, disaster_date, h3_resolution, _ ) = utils.get_disaster_with_id(disaster_id)
    print(f"Verifying changes for {disaster_id} {disaster_area}")
    valid, total = utils.verify_changes_geojson(disaster_id)

    print(f"Total changes: {total}, valid: {valid}")

def remove_invalid(disaster_id):
    removed = utils.remove_invalid(disaster_id)
    print(f"Removed {removed} changes outside defined geojson")
    return removed

# In this script, for each change we check if it is in its disaster's geojson boundary, and if it is we set it's geojson verified field to be t
# changes that are not verified can then be deleted
if __name__ == "__main__":
    utils = DB_Utils()
    utils.db_connect()
    total_removed = 0

    for disaster_id in [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]:
        validate_coordinates(disaster_id)
        total_removed += remove_invalid(disaster_id)

    open(f"./Results/BulkImportDetection/total_removed_geojson_filtering.txt", "w").write(str(total_removed))

