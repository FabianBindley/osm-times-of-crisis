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
    California = {
        "place": "California",
        "dates": {"start_date": "2017-08-16", "disaster_date": "2020-08-16", "end_date": "2021-10-16"},
        "file": "California.osh.pbf",
        "disaster_id": 7,
        "filter": False,
        "geojson_path": "Data/California/CaliforniaTop20Boundaries.geojson",
    }
    Texas = {
        "place": "Texas",
        "dates": {"start_date": "2014-08-26", "disaster_date": "2017-08-26", "end_date": "2018-10-26"},
        "file": "Texas.osh.pbf",
        "disaster_id": 8,
        "filter": False,
        "geojson_path": "Data/Texas/TexasManuallyDefined.geojson",
    }
    Sulawesi = {
        "place": "Sulawesi",
        "dates": {"start_date": "2015-09-28", "disaster_date": "2018-09-28", "end_date": "2019-11-28"},
        "file": "Sulawesi.osh.pbf",
        "disaster_id": 9,
        "filter": False,
        "geojson_path": "Data/Sulawesi/SulawesiManuallyDefined.geojson",
    }

    Attica = {
        "place": "Attica",
        "dates": {"start_date": "2015-07-23", "disaster_date": "2018-07-23", "end_date": "2019-09-23"},
        "file": "Attica.osh.pbf",
        "disaster_id": 10,
        "filter": False,
        "geojson_path": "Data/Attica/AtticaManuallyDefined.geojson",
    }

    Izmir = {
        "place": "Izmir",
        "dates": {"start_date": "2017-10-30", "disaster_date": "2020-10-30", "end_date": "2021-12-30"},
        "file": "Izmir.osh.pbf",
        "disaster_id": 11,
        "filter": False,
        "geojson_path": "Data/Izmir/IzmirManuallyDefined.geojson",
    }

    Gaziantep = {
        "place": "Gaziantep",
        "dates": {"start_date": "2020-02-06", "disaster_date": "2023-02-06", "end_date": "2024-04-06"},
        "file": "Gaziantep.osh.pbf",
        "disaster_id": 12,
        "filter": False,
        "geojson_path": "Data/Gaziantep/GaziantepManuallyDefined.geojson",
    }

    Pakistan = {
        "place": "Pakistan",
        "dates": {"start_date": "2019-08-25", "disaster_date": "2022-08-25", "end_date": "2023-10-25"},
        "file": "Pakistan.osh.pbf",
        "disaster_id": 13,
        "filter": False,
        "geojson_path": "Data/Pakistan/PakistanManuallyDefined.geojson",
    }

    Atami = {
        "place": "Atami",
        "dates": {"start_date": "2018-07-03", "disaster_date": "2021-07-03", "end_date": "2022-09-03"},
        "file": "Atami.osh.pbf",
        "disaster_id": 14,
        "filter": False,
        "geojson_path": "Data/Atami/AtamiManuallyDefined.geojson",
    }

    Derna = {
        "place": "Derna",
        "dates": {"start_date": "2020-09-10", "disaster_date": "2023-09-10", "end_date": "2024-11-10"},
        "file": "Derna.osh.pbf",
        "disaster_id": 15,
        "filter": False,
        "geojson_path": "Data/Derna/DernaManuallyDefined.geojson",
    }

    Malawi = {
        "place": "Malawi",
        "dates": {"start_date": "2020-03-12", "disaster_date": "2023-03-12", "end_date": "2024-05-12"},
        "file": "Malawi.osh.pbf",
        "disaster_id": 16,
        "filter": False,
        "geojson_path": "Data/Malawi/MalawiManuallyDefined.geojson",
    }

    Morocco = {
        "place": "Morocco",
        "dates": {"start_date": "2020-09-08", "disaster_date": "2023-09-08", "end_date": "2024-11-08"},
        "file": "Morocco.osh.pbf",
        "disaster_id": 17,
        "filter": False,
        "geojson_path": "Data/Morocco/MoroccoManuallyDefined.geojson",
    }

    Freetown = {
        "place": "Freetown",
        "dates": {"start_date": "2014-08-14", "disaster_date": "2017-08-14", "end_date": "2018-10-14"},
        "file": "Freetown.osh.pbf",
        "disaster_id": 18,
        "filter": False,
        "geojson_path": "Data/Freetown/FreetownManuallyDefined.geojson",
    }

    #places = [EmiliaRomagna, Broxbourne, Haiti2010, Texas]
    places = [EmiliaRomagna, Haiti2010, Haiti2021, Nepal, California, Texas, Sulawesi, 
              Attica, Izmir, Gaziantep, Pakistan, Atami, Derna, Malawi, Morocco, Freetown]
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
