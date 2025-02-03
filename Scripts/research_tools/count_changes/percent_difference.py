import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import csv 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

# Take the existing counts we've computed, both overall and by interval
# And compute the percentage difference compared to the means from the pre-disaster period

def percentage_difference_full_period(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric, period_length):
    print(f"Computing Full Period")
    # Load datasets
    if average_metric == "mean":
        data = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv')
        pre_disaster_changes_per_day = data.iloc[0] / pre_disaster_days
        imm_disaster_changes_per_day = data.iloc[1] / imm_disaster_days
        post_disaster_changes_per_day = data.iloc[2] / post_disaster_days

    else:
        data = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{period_length}_change_count.csv')
        data = data.drop(['start_date','end_date'], axis=1)


        pre_disaster = data.iloc[:pre_disaster_days // period_length]
        imm_disaster = data.iloc[pre_disaster_days // period_length]
        post_disaster = data.iloc[pre_disaster_days // period_length + 1:-1]

        # Some months have no changes in some places
        pre_disaster[pre_disaster == 0] = 1

        pre_disaster_changes_per_day = pre_disaster.median() / period_length
        imm_disaster_changes_per_day = imm_disaster / period_length
        post_disaster_changes_per_day = post_disaster.median() / period_length


    imm_disaster_diff = (imm_disaster_changes_per_day - pre_disaster_changes_per_day) / pre_disaster_changes_per_day * 100
    post_disaster_diff = (post_disaster_changes_per_day - pre_disaster_changes_per_day) / pre_disaster_changes_per_day  * 100


    headers = ["creates", "edits", "deletes", "total"]
    changes_per_day_file_path = f"Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_per_day_{average_metric}.csv"
    with open(changes_per_day_file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()        
        writer.writerow({"creates": pre_disaster_changes_per_day["creates"], "edits": pre_disaster_changes_per_day["edits"], "deletes": pre_disaster_changes_per_day["deletes"], "total": pre_disaster_changes_per_day["total"]})
        writer.writerow({"creates": imm_disaster_changes_per_day["creates"], "edits": imm_disaster_changes_per_day["edits"], "deletes": imm_disaster_changes_per_day["deletes"], "total": imm_disaster_changes_per_day["total"]})
        writer.writerow({"creates": post_disaster_changes_per_day["creates"], "edits": post_disaster_changes_per_day["edits"], "deletes": post_disaster_changes_per_day["deletes"], "total": post_disaster_changes_per_day["total"]})

    percent_difference_file_path = f"Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_percent_difference_{average_metric}.csv"
    with open(percent_difference_file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()        
        writer.writerow({"creates": imm_disaster_diff["creates"], "edits": imm_disaster_diff["edits"], "deletes": imm_disaster_diff["deletes"], "total": imm_disaster_diff["total"]})
        writer.writerow({"creates": post_disaster_diff["creates"], "edits": post_disaster_diff["edits"], "deletes": post_disaster_diff["deletes"], "total": post_disaster_diff["total"]})


def percentage_difference_time_series(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric, interval_length):

    print(f"Computing Time series {interval_length}")
    data_time_series = pd.read_csv(f'Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_change_count.csv')[:-1]
    data_changes_per_day = pd.read_csv(f"Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_per_day_{average_metric}.csv")
    

    to_percent_multiplier = 100

    pre_disaster_changes_per_day = data_changes_per_day.iloc[0] * interval_length # Multiply by interval length to account for longer period
    percentage_diff_rows = []
    for index, row in data_time_series.iterrows():
        percentage_diff = {
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "creates": ((row["creates"] - pre_disaster_changes_per_day["creates"]) / pre_disaster_changes_per_day["creates"]) * to_percent_multiplier,
            "edits": ((row["edits"] - pre_disaster_changes_per_day["edits"]) / pre_disaster_changes_per_day["edits"]) * to_percent_multiplier,
            "deletes": ((row["deletes"] - pre_disaster_changes_per_day["deletes"]) / pre_disaster_changes_per_day["deletes"]) * to_percent_multiplier,
            "total": ((row["total"] - pre_disaster_changes_per_day["total"]) / pre_disaster_changes_per_day["total"]) * to_percent_multiplier,
        }
        percentage_diff_rows.append(percentage_diff)

    percent_difference_time_series_file_path = f"Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_percent_difference_time_series_{average_metric}.csv"
    headers = ["start_date", "end_date", "creates", "edits", "deletes", "total"]
    with open(percent_difference_time_series_file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(percentage_diff_rows)


if __name__ == "__main__":

    db_utils = DB_Utils()
    db_utils.db_connect()

    
    periods = [(365, 30, 365), (365, 60, 365), (1095,60,365)]
    #periods = [(365, 30, 365)]
    average_metric = "median" # mean or median

    for disaster_id in range(2,7):

        for period in periods:
            pre_disaster_days, imm_disaster_days, post_disaster_days = period
            (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
            # For each disaster, count the aggregate count in each time period - pre, imm, post, and as before count the number of changes in each period
            # File system, generate 1 folder for each disaster, and output the aggregate total in each period for each type, as well as pretty much the same file we had before
            print(f"{disaster_id} {disaster_area[0]} {disaster_date}")
            # First lets do the total counts for each period
            percentage_difference_full_period(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric, 30)

            percentage_difference_time_series(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric, interval_length=1)
            percentage_difference_time_series(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric, interval_length=7)
            percentage_difference_time_series(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric, interval_length=30)


