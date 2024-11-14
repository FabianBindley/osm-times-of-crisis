from IntervalEditCounterHandler import IntervalEditCounterHandler
from datetime import datetime, timezone

# Count the number of creates, edits and deletes per period for an extracted area
# Inputs: Start Timestamp, End Timestamp, interval
#places = [{"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"Broxbourne.osh.pbf"},{"place":"EmiliaRomagna", "dates":{"start_date": "2023-02-01","end_date":"2023-07-30"}, "file":"EmiliaRomagnaNodesWays.osh.pbf"}]
places = [{"place":"EmiliaRomagna", "dates":{"start_date": "2022-05-02","end_date":"2024-05-02"},"file":"EmiliaRomagnaNodesWays.osh.pbf"}]
places = [{"place":"Haiti", "dates":{"start_date": "2015-10-04","end_date":"2017-10-04"},"file":"HaitiNodesWays.osh.pbf"}]
#places = [{"place":"UnitedKingdom", "dates":{"start_date": "2004-08-09","end_date":"2024-11-12"},"file":"UnitedKingdomNodesWays.osh.pbf"}]
#places = [{"place": "Broxbourne", "dates":{"start_date": "2024-06-01","end_date":"2024-10-30"}, "file":"BroxbourneNodesWays.osh.pbf"}]
#places = [{"place":"Haiti", "dates":{"start_date": "2009-01-12","end_date":"2011-01-12"},"file":"HaitiNodesWays.osh.pbf"},{"place":"Haiti", "dates":{"start_date": "2020-08-12","end_date":"2022-08-14"},"file":"HaitiNodesWays.osh.pbf"}]
intervals = ["day","week","month"]
filtered = False

for place in places:
    place_name = place["place"]
    start_date_str = place["dates"]["start_date"]
    end_date_str = place["dates"]["end_date"]
    file = f'./Data/{place_name}/{place["file"]}'
    geojson_path = f"./Data/GeocodedBoundaries/{place_name}-geocode-boundary.geojson"

    # Convert the date string to a datetime object
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    for interval in intervals:
        current_time = datetime.now()
        print(F'{current_time.strftime("%H:%M:%S")} | Computing {place_name} {interval}')
        interval_handler = IntervalEditCounterHandler(start_date, end_date, interval, geojson_path, filtered)
        interval_handler.apply_file(file)
        interval_handler.print_intervals()
        output_file = f'Results/EditCounting/{place_name}/count-{place_name}-{interval}-{start_date_str}-{end_date_str}{"-filtered" if filtered else ""}.csv'
        print(f"Output: {output_file}")
        interval_handler.output_csv(output_file)

   
