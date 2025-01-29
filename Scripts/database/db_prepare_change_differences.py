import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil
from BulkImportHandler import BulkImportHandler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))

from db_utils import DB_Utils

def get_missing_changes_for_disaster(disaster_id, sample_size, sample, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    start_date = disaster_date - pre_disaster
    end_date = disaster_date + imm_disaster + post_disaster + timedelta(days=1)


    changes = db_utils.get_sample_changes_for_disaster(disaster_id, sample_size, sample, start_date, end_date, "prepare", random=False)
    changes_df = pd.DataFrame(changes, columns=["element_id", "disaster_id", "version", "edit_type", "element_type"])


    previous_versions = set(
        (row["element_id"], row["disaster_id"], row["version"] - 1, row["element_type"])
        for _, row in changes_df.iterrows()
    )

    existing_versions = db_utils.get_existing_versions(list(previous_versions), "prepare")
    existing_versions_set = set((row[1], disaster_id, row[2], row[3]) for row in existing_versions)

    missing_versions = previous_versions - existing_versions_set
    missing_changes = pd.DataFrame(
        missing_versions, columns=["element_id", "disaster_id", "version","element_type"]
    )

    print(missing_changes)


    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}", exist_ok=True)
    missing_changes.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/missing_changes.csv", index=False)

def insert_missing_changes(disaster_id, disaster_area, disaster_date):

    missing_changes = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/missing_changes.csv")
    missing_changes_set = set(zip(missing_changes["element_id"], missing_changes["version"]))
    print(len(missing_changes_set))

    input_file = f'./Data/{disaster_area}/{disaster_area}NodesWays.osh.pbf'

    
    # Start and end dates are irrelevant as we know that the object will fall outside of these

    handler = BulkImportHandler(disaster_date, disaster_date, f"./Data/{disaster_area}/{disaster_area}{disaster_date.year}ManuallyDefined.geojson", False, disaster_id, disaster_area, str(disaster_date.year), db_utils.connection, input_file, missing_changes_set, False, True)
    handler.apply_file(input_file)
    handler.flush_inserts()


if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    disaster_ids =  [2,3,4,5,6]
    sample_size = 1000
    sample = False


    #get_change_differences_all_disasters()

    print(f"Getting change differences for disasters: {disaster_ids}")
    for disaster_id in disaster_ids:
        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
        print(f"Inserting missing changes for {disaster_area} {disaster_date.year}")
        get_missing_changes_for_disaster(disaster_id, sample_size, sample, disaster_date, 365, 30, 365)
        insert_missing_changes(disaster_id, disaster_area[0], disaster_date)
