import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil
import concurrent.futures
from BulkImportHandler import BulkImportHandler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))

from db_utils import DB_Utils

def get_missing_changes_for_disaster(disaster_id, sample_size, sample, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    start_date = disaster_date - pre_disaster
    end_date = disaster_date + imm_disaster + post_disaster + timedelta(days=1)

    print(start_date)
    print(end_date)

    changes = db_utils.get_sample_changes_for_disaster(disaster_id, sample_size, sample, start_date, end_date, "prepare", random=False, three_years_pre= False )
    print("changes")
    print(len(changes))
    changes_df = pd.DataFrame(changes, columns=["element_id", "disaster_id", "version", "edit_type", "element_type"])


    previous_versions = set(
        (row["element_id"], row["disaster_id"], row["version"] - 1, row["element_type"])
        for _, row in changes_df.iterrows()
    )
    print(len(previous_versions))

    existing_versions = db_utils.get_existing_versions(list(previous_versions), "prepare", three_years_pre = pre_disaster_days > 370)
    existing_versions_set = set((row[1], disaster_id, row[2], row[3]) for row in existing_versions)

    missing_versions = previous_versions - existing_versions_set
    missing_changes = pd.DataFrame(
        missing_versions, columns=["element_id", "disaster_id", "version","element_type"]
    )



    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}", exist_ok=True)
    missing_changes.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/missing_changes_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.csv", index=False)

def insert_missing_changes(disaster_id, disaster_area, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils):

    missing_changes = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/missing_changes_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.csv",)
    missing_changes_set = set(zip(missing_changes["element_id"], missing_changes["version"]))
    print(len(missing_changes_set))

    # hack to get around the fact that the geojson files and osh files are different and that nodesways failing for some
    if disaster_id <= 6 or disaster_id == 8:
        input_file = f'./Data/{disaster_area}/{disaster_area}NodesWays.osh.pbf'
    else:
        input_file = f'./Data/{disaster_area}/{disaster_area}.osh.pbf'

    
    if disaster_id  == 7:
        geojson_path = f"./Data/California/CaliforniaTop20Boundaries.geojson"
    elif disaster_id in [3,4,5]:
        geojson_path = f"./Data/{disaster_area}/{disaster_area}{disaster_date.year}ManuallyDefined.geojson"
    else:
        geojson_path = f"./Data/{disaster_area}/{disaster_area}ManuallyDefined.geojson"

    # Start and end dates are irrelevant as we know that the object will fall outside of these

    handler = BulkImportHandler(disaster_date, disaster_date, geojson_path, False, disaster_id, disaster_area, 
                                str(disaster_date.year), db_utils.connection, input_file, missing_changes_set, False, True, three_years_pre=False)
    handler.apply_file(input_file)
    handler.flush_inserts()


def process_disaster(disaster_id, period):

    db_utils = DB_Utils()
    db_utils.db_connect()
    print(db_utils)

    pre_disaster_days, imm_disaster_days, post_disaster_days = period
    (_, disaster_country, disaster_area, _, disaster_date, _) = db_utils.get_disaster_with_id(disaster_id)

    print(f"Processing Disaster {disaster_id} - {disaster_area[0]} {disaster_date.year} {period}")

    get_missing_changes_for_disaster(disaster_id, 1000, False, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils)
    insert_missing_changes(disaster_id, disaster_area[0], disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils)

    return f"Disaster {disaster_id} processing completed."


if __name__ == "__main__":

    start_time = datetime.now()
    disaster_ids = range(8,13)
    periods = [(365, 60, 365), (1095, 60, 365)]

    tasks = [(disaster_id, period) for disaster_id in disaster_ids for period in periods]

    print(f"Starting multiprocessing for {len(tasks)} disaster-period combinations...")

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_disaster, disaster_id, period): (disaster_id, period) for disaster_id, period in tasks}
        
        for future in concurrent.futures.as_completed(futures):
            disaster_id, period = futures[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Error processing Disaster {disaster_id}: {e}")

    print(f"All disasters processed in {datetime.now() - start_time}")

