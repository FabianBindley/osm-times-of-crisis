import json
from shapely.geometry import shape, Point, MultiPolygon, Polygon
from datetime import datetime
from db_utils import DB_Utils
places = [{"place":"EmiliaRomagna", "dates":{"start_date": "2022-05-02","end_date":"2024-05-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf", "disaster_id": 2}]
    #places = [{"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf", "disaster_id": 1}]
    #places = [{"place":"Haiti", "dates":{"start_date": "2009-01-12","end_date":"2011-01-12"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 3},{"place":"Haiti", "dates":{"start_date": "2020-08-12","end_date":"2022-08-14"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 4}]

def load_geometry_from_path(path):
    with open(path) as f:
        geojson_data = json.load(f)

    return shape(geojson_data["features"][0]['geometry'])

def load_geometry_manually_defined(place, year):
    if place != "Haiti":
        suffix = place
    else:
        suffix = place+year
    geojson_path = f"./Data/{place}/{suffix}ManuallyDefined.geojson"
    # Load GeoJSON and create a MultiPolygon from the geometries
    with open(geojson_path) as f:
        geojson_data = json.load(f)
    return shape(geojson_data["features"][0]['geometry'])

if __name__ == "__main__":
    utils = DB_Utils()
    connection = utils.db_connect()
    # Open a cursor to perform database operations
    cursor = connection.cursor()

    disasters = [
        {"id": 1, "country": ["UnitedKingdom"], "area": ["Broxbourne"], "geometry": load_geometry_manually_defined("Broxbourne", "2024"), "date": datetime.strptime("2024-08-15", "%Y-%m-%d").timestamp(), "h3_resolution":8},
        {"id": 2, "country": ["Italy"], "area": ["EmiliaRomagna"], "geometry": load_geometry_manually_defined("EmiliaRomagna","2023"), "date": datetime.strptime("2023-05-02", "%Y-%m-%d").timestamp(), "h3_resolution":7},
        {"id": 3, "country": ["Haiti"], "area": ["Haiti"], "geometry": load_geometry_manually_defined("Haiti", "2010"), "date": datetime.strptime("2010-01-12", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 4, "country": ["Haiti"], "area": ["Haiti"], "geometry": load_geometry_manually_defined("Haiti", "2016"), "date": datetime.strptime("2016-10-09", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 5, "country": ["Haiti"], "area": ["Haiti"], "geometry": load_geometry_manually_defined("Haiti", "2021"), "date": datetime.strptime("2021-08-14", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 6, "country": ["Nepal"], "area": ["Nepal"], "geometry": load_geometry_manually_defined("Nepal", "2015"), "date": datetime.strptime("2015-04-25", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 7, "country": ["UnitedStates"], "area": ["California"], "geometry": load_geometry_from_path("Data/California/CaliforniaTop20Boundaries.geojson"), "date": datetime.strptime("2020-08-16", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 8, "country": ["UnitedStates"], "area": ["Texas"], "geometry": load_geometry_manually_defined("Texas", "2017"), "date": datetime.strptime("2017-08-26", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 9, "country": ["Indonesia"], "area": ["Sulawesi"], "geometry": load_geometry_manually_defined("Sulawesi", "2018"), "date": datetime.strptime("2018-09-28", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 10, "country": ["Greece"], "area": ["Attica"], "geometry": load_geometry_manually_defined("Attica", "2018"), "date": datetime.strptime("2018-07-23", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 11, "country": ["Turkey"], "area": ["Izmir"], "geometry": load_geometry_manually_defined("Izmir", "2020"), "date": datetime.strptime("2020-10-30", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 12, "country": ["Turkey"], "area": ["Gaziantep"], "geometry": load_geometry_manually_defined("Gaziantep", "2023"), "date": datetime.strptime("2023-02-06", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 13, "country": ["Pakistan"], "area": ["Pakistan"], "geometry": load_geometry_manually_defined("Pakistan", "2022"), "date": datetime.strptime("2022-08-25", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 14, "country": ["Japan"], "area": ["Atami"], "geometry": load_geometry_manually_defined("Atami", "2021"), "date": datetime.strptime("2021-07-03", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 15, "country": ["Libya"], "area": ["Derna"], "geometry": load_geometry_manually_defined("Derna", "2023"), "date": datetime.strptime("2023-09-10", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 16, "country": ["Malawi"], "area": ["Malawi"], "geometry": load_geometry_manually_defined("Malawi", "2023"), "date": datetime.strptime("2023-03-12", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 17, "country": ["Morocco"], "area": ["Morocco"], "geometry": load_geometry_manually_defined("Morocco", "2023"), "date": datetime.strptime("2023-09-08", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 18, "country": ["SierraLeone"], "area": ["Freetown"], "geometry": load_geometry_manually_defined("Freetown", "2017"), "date": datetime.strptime("2017-08-14", "%Y-%m-%d").timestamp(), "h3_resolution":6},


    ]

    utils.delete_disasters()
    print("Deleted disasters")
    utils.insert_disasters(disasters, connection)

     # Close cursor and connection
    cursor.close()
    connection.close()