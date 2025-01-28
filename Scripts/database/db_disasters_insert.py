import json
from shapely.geometry import shape, Point, MultiPolygon, Polygon
from datetime import datetime
from db_utils import DB_Utils
places = [{"place":"EmiliaRomagna", "dates":{"start_date": "2022-05-02","end_date":"2024-05-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf", "disaster_id": 2}]
    #places = [{"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf", "disaster_id": 1}]
    #places = [{"place":"Haiti", "dates":{"start_date": "2009-01-12","end_date":"2011-01-12"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 3},{"place":"Haiti", "dates":{"start_date": "2020-08-12","end_date":"2022-08-14"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 4}]

def load_geometry_geocded(place):
    geojson_path = f"./Data/GeocodedBoundaries/{place}-geocode-boundary.geojson"
    # Load GeoJSON and create a MultiPolygon from the geometries
    with open(geojson_path) as f:
        geojson_data = json.load(f)

    return shape(geojson_data['geometry'])

def load_geometry_manually_defined(place, year):
    if place != "Haiti":
        suffix = place
    else:
        suffix = place+year
    geojson_path = f"./Data/{place}/{suffix}ManuallyDefined.geojson"
    # Load GeoJSON and create a MultiPolygon from the geometries
    with open(geojson_path) as f:
        geojson_data = json.load(f)
    print(geojson_data)
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

    ]

    utils.delete_disasters()
    print("Deleted disasters")
    utils.insert_disasters(disasters, connection)

     # Close cursor and connection
    cursor.close()
    connection.close()