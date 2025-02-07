import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil
import ast

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def get_key_counts(pre_disaster_days, imm_disaster_days, post_diaster_days):
    tag_keys = db_utils.get_tag_key_usage()
    total_changes = db_utils.get_total_changes(pre_disaster_days, imm_disaster_days, post_diaster_days)

    file_path = f"./Results/TagInvestigation/summary/unique_tag_keys_count_all.csv"
    headers = ["key","count", "percent_of_total_changes"]
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for res in tag_keys:
            writer.writerow({"key": res[0], "count": res[1], "percent_of_total_changes": round(res[1]/total_changes * 100, 4)})

    os.makedirs(f"visualisation-site/public/TagInvestigation/summary/", exist_ok=True)
    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/unique_tag_keys_count_all.csv"
    shutil.copyfile(file_path, visualisation_file_path)
            
def get_tag_key_usage_for_disaster(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    pre_disaster_start_date = disaster_date - pre_disaster

    imm_disaster_start_date = disaster_date

    post_disaster_start_date = disaster_date + imm_disaster
    post_disaster_end_date = post_disaster_start_date + post_disaster + timedelta(days=1)

    intervals = [pre_disaster_start_date, imm_disaster_start_date, post_disaster_start_date, post_disaster_end_date]

    # This needs to be broken into an array of 3 dicts
    tag_keys_intervals = [
    {row[0]: row[1] for row in period} 
    for period in db_utils.get_tag_key_usage_for_disaster(disaster_id, intervals)]


    full_periods_change_count = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv")[:-1]

    os.makedirs(f"./Results/TagInvestigation/disaster{disaster_id}", exist_ok=True)
    os.makedirs(f"visualisation-site/public/TagInvestigation/disaster{disaster_id}", exist_ok=True)
    headers = ["key","count","percent_of_total_changes","percent_difference_from_pre", "percent_difference_from_pre_day"]

    for tag_keys, interval, days, row_index in list(zip(tag_keys_intervals, ["pre","imm","post"], [pre_disaster_days, imm_disaster_days, post_disaster_days], [0,1,2])):
        file_path = f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_{interval}.csv"
        with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            for key,count in tag_keys.items():
                pre_disaster_count = tag_keys_intervals[0][key] if key in tag_keys_intervals[0] else 1
                pre_disaster_count_day = pre_disaster_count/pre_disaster_days
                count_day = count/days
                writer.writerow({"key": key, "count": count, "percent_of_total_changes": round(count/full_periods_change_count.iloc[row_index]["total"] * 100, 4),  "percent_difference_from_pre": round((count-pre_disaster_count)/pre_disaster_count * 100, 4), "percent_difference_from_pre_day": round((count_day-pre_disaster_count_day)/pre_disaster_count_day * 100, 4)})

        visualisation_file_path = f"visualisation-site/public/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_{interval}.csv"
        shutil.copyfile(file_path, visualisation_file_path)

def top_n_tag_keys_for_period(n, period, disaster_ids, pre_disaster_days, imm_disaster_days, post_disaster_days):
    print(datetime.now())
    all_keys = {}
    for disaster_id in disaster_ids:
        file_path = f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_{period}.csv"
        with open(file_path, mode="r", newline='', encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["key"] in all_keys:
                    all_keys[row["key"]] += int(row["count"])
                else:
                    all_keys[row["key"]] = int(row["count"])

    all_keys = sorted(all_keys.items(), key=lambda x: x[1], reverse=True)[:n]

    os.makedirs(f"./Results/TagInvestigation/summary/top_{n}_keys/", exist_ok=True)
    full_periods_change_count = pd.read_csv(f"./Results/ChangeCounting/summary/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv")

    pre_disaster_counts = {}
    for disaster_id in disaster_ids:
        pre_disaster_counts[disaster_id] = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_pre.csv")
    

    file_path = f"./Results/TagInvestigation/summary/top_{n}_keys/{period}.csv"
    headers = ["key","count","percent_of_total_changes", "percent_difference_from_pre", "percent_difference_from_pre_day"]
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        row_index = 0 if period == "pre" else 1 if period == "imm" else 2
        for tuple in all_keys:
            key=tuple[0]
            count=tuple[1]
            if period == "pre":
                pre_disaster_count = count
                days = pre_disaster_days

            else:
                pre_disaster_count = 0
                for disaster_id in disaster_ids:
                    pre_disaster_key_row = pre_disaster_counts[disaster_id][pre_disaster_counts[disaster_id]["key"] == key]
                    pre_disaster_count += pre_disaster_key_row["count"].values[0] if len(pre_disaster_key_row) == 1 else 1

                days = imm_disaster_days if period == "imm" else post_disaster_days
            
            pre_disaster_count_day = pre_disaster_count/pre_disaster_days
            count_day = count/days

            writer.writerow({"key": key, "count": count, "percent_of_total_changes": round(count/full_periods_change_count.iloc[row_index]["total"]  * 100, 4),  "percent_difference_from_pre": round((count-pre_disaster_count)/pre_disaster_count * 100, 4), "percent_difference_from_pre_day": round((count_day-pre_disaster_count_day)/pre_disaster_count_day * 100, 4)})

    os.makedirs(f"visualisation-site/public/TagInvestigation/summary/top_{n}_keys/", exist_ok=True)
    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/top_{n}_keys/{period}.csv"
    shutil.copyfile(file_path, visualisation_file_path)
    print(datetime.now())
    
if __name__ == "__main__":

    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()
    
    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = range(2,19)
        print("Disaster IDs defined:", disaster_ids)

    print("Getting key counts")
    get_key_counts(pre_disaster_days=365, imm_disaster_days=30, post_diaster_days=365)

    print("Getting tag usage for disasters")
    for disaster_id in disaster_ids:
        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
        print(f"Generating key metrics for {disaster_area[0]} {disaster_date.year}")
        get_tag_key_usage_for_disaster(disaster_id, disaster_date, 365, 60, 365)

    nums = [10, 25, 100, 4000]
    
    print("Getting top n tag keys for periods")
    for period in ["pre","imm","post"]:
        for n in nums:
            top_n_tag_keys_for_period(n, period, disaster_ids, 365, 60, 365)
