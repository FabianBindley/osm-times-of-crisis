import sys
import os
import numpy as np
from datetime import datetime, timedelta
import csv 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_utils import DB_Utils


def generate_intervals(disaster_date, interval_width, before_after_time_length):
    # Calculate the start and end date range
    start_range = disaster_date - timedelta(days=before_after_time_length)
    end_range = disaster_date + timedelta(days=before_after_time_length)
    
    # Create intervals using NumPy arange
    date_range = np.arange(
        start_range, 
        end_range + timedelta(days=1),  # Include the end date
        timedelta(days=interval_width)  # Step size as timedelta
    )
    
    # Convert NumPy datetime64 array to Python datetime objects
    return [date.item() for date in date_range]


def save_counts(counts, intervals):
    delta = intervals[1] - intervals[0]

    if delta == timedelta(days=1):
        interval = "day"

    elif delta == timedelta(days=7):
        interval = "week"

    elif delta == timedelta(days=30):
        interval = "month"

    file_path = f"./Results/ChangeCounting/data/change_count_{disaster_id}_{interval}.csv"
    headers = ["start_date", "end_date", "creates", "edits", "deletes", "total"]
    create_total, edit_total, delete_total, total_total = 0, 0, 0, 0
    
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        

        for (creates, edits, deletes, total), (interval) in list(zip(counts, intervals)):
            create_total += creates
            edit_total += edits
            delete_total += deletes
            total_total += total

            writer.writerow({"start_date": interval, "end_date": interval+delta, "creates": creates, "edits": edits, "deletes": deletes, "total": total})

        writer.writerow({"start_date": intervals[0], "end_date": intervals[-1]+delta, "creates": create_total, "edits": edit_total, "deletes": delete_total,"total": total_total})
        


if __name__ == "__main__":

    db_utils = DB_Utils()
    db_utils.db_connect()

    for disaster_id in range(1,2):
        start_time = datetime.now()
        # Get the information for the disaster with the given disaster_id
        (_, disaster_country, disaster_area, disaster_geojson, disaster_date ) = db_utils.get_disaster_with_id(disaster_id)
        print(f"Generating counts for {disaster_area[0]}")
        # Generate the intervals for the disaster 
        intervals = generate_intervals(disaster_date, interval_width=7, before_after_time_length=365)

        counts = db_utils.count_changes_in_interval(disaster_id, intervals)
        print(f"Query count for {disaster_area[0]} took {round(datetime.now().timestamp()-start_time.timestamp(),2)} seconds")
    
        save_counts(counts, intervals)


    


