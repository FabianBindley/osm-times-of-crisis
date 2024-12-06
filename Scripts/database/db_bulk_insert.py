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

    EmiliaRomagna = {"place":"EmiliaRomagna", "dates":{"start_date": "2022-05-02","end_date":"2024-06-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf", "disaster_id": 2, "filter": False}
    Broxbourne = {"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf", "disaster_id": 1, "filter": True}
    Haiti2010 = {"place":"Haiti", "dates":{"start_date": "2009-01-12","end_date":"2011-02-12"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 3, "filter": False}
    Haiti2016 = {"place":"Haiti", "dates":{"start_date": "2015-10-09","end_date":"2017-11-09"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 4, "filter": False}
    Haiti2021 = {"place":"Haiti", "dates":{"start_date": "2020-08-14","end_date":"2022-09-14"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 5, "filter": False}
    Nepal = {"place":"Nepal", "dates":{"start_date": "2014-04-25","end_date":"2016-05-25"},"file":"NepalNodesWays.osh.pbf", "disaster_id": 6, "filter": False}

    #places = [{"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf", "disaster_id": 1, "filter": True}, {"place":"Haiti", "dates":{"start_date": "2009-01-12","end_date":"2011-01-12"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 3, "filter": False}, {"place":"Haiti", "dates":{"start_date": "2015-10-09","end_date":"2017-10-09"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 4, "filter": False}]
    #places = [Broxbourne, EmiliaRomagna, Haiti2016]
    places = [Haiti2021, Nepal]
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

        handler = BulkImportHandler(start_date, end_date, geojson_path, place["filter"], disaster_id, connection, file)

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