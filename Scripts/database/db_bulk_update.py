from db_utils import DB_Utils
from BulkUpdateHandler import BulkUpdateHandler
from datetime import datetime, timezone

if __name__ == "__main__":
 
    utils = DB_Utils()
    connection = utils.db_connect()
    # Open a cursor to perform database operations
    cursor = connection.cursor()

    places = [{"place":"EmiliaRomagna", "dates":{"start_date": "2022-05-02","end_date":"2024-05-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf", "disaster_id": 2}]
    column_to_update = "uid"

    for place in places:
        place_name = place["place"]
        disaster_id = place["disaster_id"]
        start_date_str = place["dates"]["start_date"]
        end_date_str = place["dates"]["end_date"]
        file = f'./Data/{place_name}/{place["file"]}'
        geojson_path = f"./Data/GeocodedBoundaries/{place_name}-geocode-boundary.geojson"

        # Convert the date string to a datetime object
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        handler = BulkUpdateHandler(start_date, end_date, geojson_path, True, disaster_id, column_to_update)

        start_time = datetime.now()
        print(f"Start time: {start_time}")
        handler.apply_file(file)
        handler.flush_updates()
        handler.print_statistics()
        print(f"Update Time: {round(datetime.now().timestamp()-start_time.timestamp(),2)} seconds")

        # Close cursor and connection
        cursor.close()
        connection.close()
