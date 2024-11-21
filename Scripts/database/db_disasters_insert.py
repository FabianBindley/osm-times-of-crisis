import json
from shapely.geometry import shape, Point, MultiPolygon, Polygon
from datetime import datetime
from db_utils import DB_Utils
places = [{"place":"EmiliaRomagna", "dates":{"start_date": "2022-05-02","end_date":"2024-05-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf", "disaster_id": 2}]
    #places = [{"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf", "disaster_id": 1}]
    #places = [{"place":"Haiti", "dates":{"start_date": "2009-01-12","end_date":"2011-01-12"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 3},{"place":"Haiti", "dates":{"start_date": "2020-08-12","end_date":"2022-08-14"},"file":"HaitiNodesWays.osh.pbf", "disaster_id": 4}]

def load_geometry(place):
    geojson_path = f"./Data/GeocodedBoundaries/{place}-geocode-boundary.geojson"
    # Load GeoJSON and create a MultiPolygon from the geometries
    with open(geojson_path) as f:
        geojson_data = json.load(f)

    return shape(geojson_data['geometry'])

if __name__ == "__main__":
    utils = DB_Utils()
    connection = utils.db_connect()
    # Open a cursor to perform database operations
    cursor = connection.cursor()

    disasters = [
        {"id": 1, "country": ["UnitedKingdom"], "area": ["Broxbourne"], "geometry": load_geometry("Broxbourne"), "date": datetime.strptime("2024-08-15", "%Y-%m-%d").timestamp(), "h3_resolution":8},
        {"id": 2, "country": ["Italy"], "area": ["EmiliaRomagna"], "geometry": load_geometry("EmiliaRomagna"), "date": datetime.strptime("2023-05-02", "%Y-%m-%d").timestamp(), "h3_resolution":7},
        {"id": 3, "country": ["Haiti"], "area": ["Haiti"], "geometry": load_geometry("Haiti"), "date": datetime.strptime("2010-01-12", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 4, "country": ["Haiti"], "area": ["Haiti"], "geometry": load_geometry("Haiti"), "date": datetime.strptime("2016-10-09", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 5, "country": ["Haiti"], "area": ["Haiti"], "geometry": load_geometry("Haiti"), "date": datetime.strptime("2021-08-14", "%Y-%m-%d").timestamp(), "h3_resolution":6},
        {"id": 6, "country": ["Nepal"], "area": ["Nepal"], "geometry": load_geometry("Nepal"), "date": datetime.strptime("2015-04-25", "%Y-%m-%d").timestamp(), "h3_resolution":6},

    ]


    utils.insert_disasters(disasters, connection)

     # Close cursor and connection
    cursor.close()
    connection.close()