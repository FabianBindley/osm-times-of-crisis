from db_utils import DB_Utils
from BulkImportHandler import BulkImportHandler
from datetime import datetime, timezone
import time
import cProfile
import pstats

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    utils = DB_Utils()
    connection = utils.db_connect()
    # Open a cursor to perform database operations
    cursor = connection.cursor()

    EmiliaRomagna = {"place":"EmiliaRomagna", "dates":{"start_date": "2020-05-02","disaster_date":"2023-05-02","end_date":"2024-06-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf", "disaster_id": 2, "filter": False, "geojson_path": f"Data/EmiliaRomagna/EmiliaRomagnaManuallyDefined.geojson"}
    Broxbourne = {"place": "Broxbourne", "dates":{"start_date": "2022-06-01","disaster_date":"2024-05-02","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf", "disaster_id": 1, "filter": True, "geojson_path": f"Data/GeocodedBoundaries/Broxbourne-geocode-boundary.geojson"}
    Haiti2010 = {"place":"Haiti", "dates":{"start_date": "2007-01-12","disaster_date":"2010-01-12","end_date":"2011-02-12"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 3, "filter": False, "geojson_path" : f"Data/Haiti/Haiti2010ManuallyDefined.geojson"}
    Haiti2016 = {"place":"Haiti", "dates":{"start_date": "2013-10-09","disaster_date":"2016-10-09","end_date":"2017-11-09"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 4, "filter": False, "geojson_path" : f"Data/GeocodedBoundaries/Haiti-geocode-boundary.geojson"}
    Haiti2021 = {"place":"Haiti", "dates":{"start_date": "2018-08-14","disaster_date":"2021-08-14","end_date":"2022-09-14"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 5, "filter": False, "geojson_path" : f"Data/Haiti/Haiti2021ManuallyDefined.geojson"}
    Nepal = {"place":"Nepal", "dates":{"start_date": "2012-04-25","disaster_date":"2015-04-25","end_date":"2016-05-25"},"file":"NepalNodesWays.osh.pbf", "disaster_id": 6, "filter": False, "geojson_path" : f"Data/Nepal/NepalManuallyDefined.geojson"}

    places = [EmiliaRomagna,Broxbourne,Haiti2010,Haiti2016,Haiti2021,Nepal]
    #places = [Haiti2021, Nepal]
    for place in places:
        place_name = place["place"]
        disaster_id = place["disaster_id"]
        start_date_str = place["dates"]["start_date"]
        disaster_date_str = place["dates"]["disaster_date"]
        end_date_str = place["dates"]["end_date"]
        geojson_path = place["geojson_path"]
        file = f'./Data/{place_name}/{place["file"]}'
        geojson_path = place["geojson_path"]

        # Convert the date string to a datetime object
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        disaster_date = datetime.strptime(disaster_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # missing changes = 

        handler = BulkImportHandler(start_date, end_date, geojson_path, place["filter"], disaster_id, place_name, str(disaster_date.year), connection, file, set(), insert_normal_changes=True, insert_missing_changes=False)

        start_time = datetime.now()
        print(f"Start time: {start_time} id: {disaster_id}")
        handler.apply_file(file)
        handler.flush_inserts()
        handler.print_statistics()
        print(f"Insert Time: {round(datetime.now().timestamp()-start_time.timestamp(),2)} seconds")

    # Close cursor and connection
    cursor.close()
    connection.close()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative').print_stats(20)