import sys
import os
import numpy as np
from datetime import datetime, timedelta
import csv 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

# Define the period lengths
pre_disaster = timedelta(days=365)
imm_disaster = timedelta(days=28)
# The post disaster is 365 days starting after the imm disaster
post_disaster = timedelta(days=365)

def count_full_periods(disaster_id, disaster_date):
    pre_disaster_start_date = disaster_date - pre_disaster

    imm_disaster_start_date = disaster_date

    post_disaster_start_date = disaster_date + imm_disaster
    post_disaster_end_date = post_disaster_start_date + post_disaster + timedelta(days=1)

    intervals = [pre_disaster_start_date, imm_disaster_start_date, post_disaster_start_date, post_disaster_end_date]

    counts = db_utils.count_changes_in_interval(disaster_id, intervals)

    total_creates = 0
    total_edits = 0
    total_deletes = 0
    total_total = 0
    
    # Save the counts
    if not os.path.exists(f"Results/ChangeCounting/disaster{disaster_id}/data"):
        os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/data")

    headers = ["creates", "edits", "deletes", "total"]
    file_path = f"Results/ChangeCounting/disaster{disaster_id}/data/full_periods_change_count.csv"

    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()        
        
        for creates, edits, deletes, total in counts:

            total_creates += creates
            total_edits += edits
            total_deletes += deletes
            total_total += total

            writer.writerow({"creates": creates, "edits": edits, "deletes": deletes, "total": total})
        
        writer.writerow({"creates": total_creates, "edits": total_edits, "deletes": total_deletes, "total": total_total})

        print("Saved full periods")

def count_by_interval_length(disaster_id, disaster_date, interval_length):

    # Calculate the start and end date range
    start_range = disaster_date - pre_disaster
    end_range = disaster_date + imm_disaster+ post_disaster + timedelta(days=1)

    # Create intervals 
    intervals = []
    current = start_range
    while current < end_range:  # Ensure no overlap at the end
        intervals.append(current)
        current += timedelta(days=interval_length)
    intervals.append(end_range)  # Include the final end date

    counts = db_utils.count_changes_in_interval(disaster_id, intervals)

    delta = timedelta(interval_length)


    print(f"Counting {interval_length}")

    file_path = f"./Results/ChangeCounting/disaster{disaster_id}/data/{str(interval_length)}_change_count.csv"
    headers = ["start_date", "end_date", "creates", "edits", "deletes", "total"]
    
    total_creates = 0
    total_edits = 0
    total_deletes = 0
    total_total = 0
    
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        

        for (creates, edits, deletes, total), (interval) in list(zip(counts, intervals)):

            total_creates += creates
            total_edits += edits
            total_deletes += deletes
            total_total += total

            writer.writerow({"start_date": interval, "end_date": interval+delta, "creates": creates, "edits": edits, "deletes": deletes, "total": total})

        writer.writerow({"start_date": intervals[0], "end_date": intervals[-1]+delta, "creates": total_creates, "edits": total_edits, "deletes": total_deletes,"total": total_total})

        print(f"Saved {interval_length}")






if __name__ == "__main__":

    db_utils = DB_Utils()
    db_utils.db_connect()

    for disaster_id in range(1,7):

        if disaster_id in []:
            continue

        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
        # For each disaster, count the aggregate count in each time period - pre, imm, post, and as before count the number of changes in each period
        # File system, generate 1 folder for each disaster, and output the aggregate total in each period for each type, as well as pretty much the same file we had before
        print(f"{disaster_id} {disaster_area[0]} {disaster_date}")
        # First lets do the total counts for each period
        print("Counting full periods")

        count_full_periods(disaster_id, disaster_date)
        count_by_interval_length(disaster_id, disaster_date, interval_length=1)
        count_by_interval_length(disaster_id, disaster_date, interval_length=7)
        count_by_interval_length(disaster_id, disaster_date, interval_length=30)

