import osmium
import csv
from datetime import datetime, timezone, timedelta
from shapely.geometry import shape, Point, MultiPolygon, Polygon
import json
"""
A handler that counts the number of creates, modifications, and deletions 
of OSM elements (nodes, ways, and relations) within specified time intervals.

Attributes:
    start_time (datetime): Start of the time period to analyze.
    end_time (datetime): End of the time period to analyze.
    interval (timedelta): Duration of each interval within the time period.
    create_count (int): Counter for creations in the current interval.
    modify_count (int): Counter for modifications in the current interval.
    delete_count (int): Counter for deletions in the current interval.
    results (list): List to store counts for each interval.
"""

class IntervalChanges():
    def __init__(self, start_date):
        self.creates = 0
        self.edits = 0
        self.deletes = 0
        self.total = 0
        self.start_date = start_date
    
    def increment_creates(self):
        self.creates+=1
    
    def increment_edits(self):
        self.edits+=1

    def increment_deletes(self):
        self.deletes+=1 

    def print(self):
        print(f'{datetime.fromtimestamp(self.start_date).strftime("%Y-%m-%d")}: C:{self.creates} E:{self.edits} D:{self.deletes} T:{self.creates + self.edits + self.deletes}')
    
    def get_data(self):
        # Returns data as a dictionary for easy CSV writing
        self.total = self.creates + self.edits + self.deletes
        return {
            "start_date": datetime.fromtimestamp(self.start_date).strftime("%Y-%m-%d"),
            "creates": self.creates,
            "edits": self.edits,
            "deletes": self.deletes,
            "total": self.total
        }

class IntervalEditCounterHandler(osmium.SimpleHandler):

    def __init__(self, start_date, end_date, interval, geojson_path, filtered):
        # For now the interval is daily, from the start time to the end time
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.intervals = {}
        self.filtered = filtered
        self.initialize_intervals()

         # Load GeoJSON and create a MultiPolygon from the geometries
        with open(geojson_path) as f:
            geojson_data = json.load(f)

            # Extract the geometry and create the shape
            geometry = geojson_data['geometry']
            self.area_multipolygon = shape(geometry)

            


    def initialize_intervals(self):
        current = self.start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # Possible intervals, day, week, month

        if self.interval == "day":
            delta = timedelta(days=1)
            while current <= self.end_date:
                self.intervals[current.timestamp()] = IntervalChanges(current.timestamp())
                current += delta

        elif self.interval == "week":
            # Align to the most recent Monday before or on the start date
            current -= timedelta(days=current.weekday())  # Move to Monday
            delta = timedelta(weeks=1)
            while current <= self.end_date:
                self.intervals[current.timestamp()] = IntervalChanges(current.timestamp())
                current += delta

        elif self.interval == "month":
            # Align to the first of the month
            current = current.replace(day=1)
            while current <= self.end_date:
                self.intervals[current.timestamp()] = IntervalChanges(current.timestamp())
                # Move to the first of the next month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)


    def update_interval(self, obj):

        # Determine the appropriate interval based on the object's timestamp
        timestamp = obj.timestamp.astimezone(timezone.utc)
        interval_start = self._get_interval_start(timestamp)
        interval_key = interval_start.timestamp()

        # Fetch or create the interval entry
        interval = self.intervals.get(interval_key)
        if interval:
            if not obj.visible:
                interval.increment_deletes()
            elif obj.version > 1:
                interval.increment_edits()
            else:
                interval.increment_creates()
        else:
            print("Interval did not exist for some reason.")

    def add_to_interval(self, obj):

        # Check that the objects coordinates are inside the geojson multipolygon, 
        if isinstance(obj, osmium.osm.Node):
            if self.point_in_geojson(obj):
                self.update_interval(obj)
            else:
                #print("excluded: ")
                #print(obj)
                pass
        
        # Check that the objects coordinates are inside the geojson multipolygon, 
        if isinstance(obj, osmium.osm.Way):
            for node_ref in obj.nodes:
                if self.point_in_geojson(node_ref):
                    self.update_interval(obj)
                    break

        if isinstance(obj, osmium.osm.Relation):
            self.update_interval(obj)


    def _get_interval_start(self, timestamp):
        """
        Determines the start of the interval based on the specified interval type.
        """
        if self.interval == "day":
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

        elif self.interval == "week":
            # Find the start of the week (previous Monday)
            start_of_week = timestamp - timedelta(days=timestamp.weekday())
            return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        elif self.interval == "month":
            # Set to the first day of the month
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
    
    def point_in_geojson(self, obj):
        if self.filtered:
            try:
                return self.area_multipolygon.contains(Point(obj.lon, obj.lat))
            except:
                return True
        else:
            return True


    def print_intervals(self):
        for _,interval in self.intervals.items():
            interval.print()

    def output_csv(self, file_path):
        # Define the CSV headers
        headers = ["start_date", "creates", "edits", "deletes", "total"]

        create_total, edit_total, delete_total, total_total = 0, 0, 0, 0
        # Write data to CSV file
        with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            # Write each interval's data to the CSV
            for interval in self.intervals.values():
                interval_data = interval.get_data()
                writer.writerow(interval_data)
                create_total += interval_data["creates"]
                edit_total += interval_data["edits"]
                delete_total += interval_data["deletes"]
                total_total += interval_data["total"]
            
            # Write the final output of the total
            writer.writerow({"start_date": "total", "creates": create_total, "edits": edit_total, "deletes": delete_total, "total": total_total})

    def node(self, n):
        if self.start_date <= n.timestamp <= self.end_date:
            self.add_to_interval(n)

    
    def relation(self, r):
        if self.start_date <= r.timestamp <= self.end_date:
            self.add_to_interval(r)
    

    def way(self, w):
        if self.start_date <= w.timestamp <= self.end_date:
            self.add_to_interval(w)



    


