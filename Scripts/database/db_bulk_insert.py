from db_utils import DB_Utils
from BulkImportHandler import BulkImportHandler
from datetime import datetime, timezone
import concurrent.futures
import time


def process_disaster(place):
    """
    Process a single disaster data using BulkImportHandler.
    """
    utils = DB_Utils()
    connection = utils.db_connect()
    cursor = connection.cursor()

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

    handler = BulkImportHandler(
        start_date,
        end_date,
        geojson_path,
        place["filter"],
        disaster_id,
        place_name,
        str(disaster_date.year),
        connection,
        file,
        set(),
        insert_normal_changes=True,
        insert_missing_changes=False,
        three_years_pre=False
    )

    start_time = datetime.now()
    print(f"Start processing {place_name} (Disaster ID: {disaster_id}) at {start_time}")
    
    handler.apply_file(file)
    handler.flush_inserts()
    handler.print_statistics()

    elapsed_time = round((datetime.now() - start_time).total_seconds(), 2)
    print(f"Finished processing {place_name} (Disaster ID: {disaster_id}) in {elapsed_time} seconds")

    cursor.close()
    connection.close()


if __name__ == "__main__":

    EmiliaRomagna = {
        "place": "EmiliaRomagna",
        "dates": {"start_date": "2020-05-02", "disaster_date": "2023-05-02", "end_date": "2024-07-02"},
        "file": "EmiliaRomagnaNodesWays.osh.pbf",
        "disaster_id": 2,
        "filter": False,
        "geojson_path": "Data/EmiliaRomagna/EmiliaRomagnaManuallyDefined.geojson",
    }
    Broxbourne = {
        "place": "Broxbourne",
        "dates": {"start_date": "2022-06-01", "disaster_date": "2024-05-02", "end_date": "2024-11-30"},
        "file": "BroxbourneNodesWays.osh.pbf",
        "disaster_id": 1,
        "filter": True,
        "geojson_path": "Data/GeocodedBoundaries/Broxbourne-geocode-boundary.geojson",
    }
    Haiti2010 = {
        "place": "Haiti",
        "dates": {"start_date": "2007-01-12", "disaster_date": "2010-01-12", "end_date": "2011-03-12"},
        "file": "HaitiNodesWays.osh.pbf",
        "disaster_id": 3,
        "filter": False,
        "geojson_path": "Data/Haiti/Haiti2010ManuallyDefined.geojson",
    }
    Haiti2016 = {
        "place": "Haiti",
        "dates": {"start_date": "2013-10-09", "disaster_date": "2016-10-09", "end_date": "2017-12-09"},
        "file": "HaitiNodesWays.osh.pbf",
        "disaster_id": 4,
        "filter": False,
        "geojson_path": "Data/GeocodedBoundaries/Haiti-geocode-boundary.geojson",
    }
    Haiti2021 = {
        "place": "Haiti",
        "dates": {"start_date": "2018-08-14", "disaster_date": "2021-08-14", "end_date": "2022-10-14"},
        "file": "HaitiNodesWays.osh.pbf",
        "disaster_id": 5,
        "filter": False,
        "geojson_path": "Data/Haiti/Haiti2021ManuallyDefined.geojson",
    }
    Nepal = {
        "place": "Nepal",
        "dates": {"start_date": "2012-04-25", "disaster_date": "2015-04-25", "end_date": "2016-06-25"},
        "file": "NepalNodesWays.osh.pbf",
        "disaster_id": 6,
        "filter": False,
        "geojson_path": "Data/Nepal/NepalManuallyDefined.geojson",
    }

    places = [EmiliaRomagna, Broxbourne, Haiti2010, Haiti2016, Haiti2021, Nepal]

    # Use multiprocessing to process each disaster in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_disaster, place): place["disaster_id"] for place in places}

        for future in concurrent.futures.as_completed(futures):
            disaster_id = futures[future]
            try:
                result = future.result()
                print(f"Completed Disaster ID: {disaster_id}")
            except Exception as e:
                print(f"Error processing Disaster ID {disaster_id}: {e}")
