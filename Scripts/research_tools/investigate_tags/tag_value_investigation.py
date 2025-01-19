import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))

from db_utils import DB_Utils


def get_key_value_counts(keys):
    total_changes_keys = pd.read_csv("./Results/TagInvestigation/summary/unique_tag_keys_count_all.csv").iloc[:50]
    total_changes_keys_filtered = total_changes_keys[total_changes_keys['key'].isin(keys)]

    tag_values = db_utils.get_tag_key_value_usage(keys)

    file_path = f"./Results/TagInvestigation/summary/unique_tag_key_values_count_all.csv"
    headers = ["key","value","count", "percent_of_total_changes_for_key"]
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for res in tag_values:
            key=res[0]
            value=res[1]
            count=res[2]
            total_changes_count = total_changes_keys_filtered[total_changes_keys_filtered['key']==key]['count'].values[0]
            writer.writerow({"key": key, "value":value, "count": count, "percent_of_total_changes_for_key": round(count/total_changes_count * 100, 4)})

    os.makedirs(f"visualisation-site/public/TagInvestigation/summary/", exist_ok=True)
    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/tag_key_values_count_all.csv"
    shutil.copyfile(file_path, visualisation_file_path)

    # Count unique tag values and total occurrences
    unique_tag_value_counts = {}
    for res in tag_values:
        key = res[0]
        value = res[1]
        count= res[2]
        if key not in unique_tag_value_counts:
            unique_tag_value_counts[key] = [set(), 0] 
        unique_tag_value_counts[key][0].add(value)  
        unique_tag_value_counts[key][1] += count     

    file_path = "./Results/TagInvestigation/summary/tag_key_values_count.csv"

     # Write unique value counts to a new file
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["key", "count", "unique_value_count"])
        writer.writeheader()
        for key in keys:
            unique_values  = unique_tag_value_counts[key][0]
            count = unique_tag_value_counts[key][1]
            writer.writerow({"key": key, "count": count, "unique_value_count": len(unique_values)})

    # Copy both files to the visualization site directory
    shutil.copyfile(file_path, "visualisation-site/public/TagInvestigation/summary/tag_key_values_count.csv")

def get_top_n_values_for_keys_all_periods(n):

    # For all Periods:
    tag_key_values = pd.read_csv("./Results/TagInvestigation/summary/unique_tag_key_values_count_all.csv")

    # Group by 'key' and get the top N values for each group
    top_n_key_values = (
        tag_key_values.groupby("key")
        .apply(lambda x: x.nlargest(n, "count"))
    )

    # Save the result to a CSV file
    os.makedirs("./Results/TagInvestigation/summary/top_n_tag_key_values/all_periods", exist_ok=True)
    file_path = f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_{n}_tag_key_values.csv"
    top_n_key_values.to_csv(file_path, index=False)

    # Optionally copy the result to the visualization directory
    os.makedirs("visualisation-site/public/TagInvestigation/summary/top_n_tag_key_values/all_periods", exist_ok=True)
    shutil.copyfile(file_path, f"visualisation-site/public/TagInvestigation/summary/top_n_tag_key_values/top_{n}_tag_key_values.csv")

def get_top_n_values_for_keys_period(keys, n, period, disaster_ids):

    all_key_values = {}


    for disaster_id in disaster_ids:
        file_path = f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{period}.csv"
        with open(file_path, mode="r", newline='', encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                if row["key"] in keys:
                    key_value = (row["key"], row["value"])  # Use key-value as a tuple
                    if key_value in all_key_values:
                        all_key_values[key_value] += int(row["count"])
                    else:
                        all_key_values[key_value] = int(row["count"])


    grouped_key_values = {}
    for (key, value), count in all_key_values.items():
        if key not in grouped_key_values:
            grouped_key_values[key] = []
        grouped_key_values[key].append((value, count))


    top_n_key_values = []
    for key, values in grouped_key_values.items():
        # Sort values by count in descending order and take the top N
        top_values = sorted(values, key=lambda x: x[1], reverse=True)[:n]
        total_count_for_key = sum(v[1] for v in values)  # Total count for key
        for value, count in top_values:
            top_n_key_values.append({
                "key": key,
                "value": value,
                "count": count,
                "percent_of_total_changes_for_key": round(count / total_count_for_key * 100, 4)
            })


    os.makedirs(f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_{n}_key_values/", exist_ok=True)
    file_path = f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_{n}_key_values/{period}.csv"
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["key", "value", "count", "percent_of_total_changes_for_key"])
        writer.writeheader()
        for row in top_n_key_values:
            writer.writerow(row)


    os.makedirs(f"visualisation-site/public/TagInvestigation/summary/top_n_tag_key_values/top_{n}_key_values/", exist_ok=True)
    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/top_n_tag_key_values/top_{n}_key_values/{period}.csv"
    shutil.copyfile(file_path, visualisation_file_path)



def get_tag_key_value_usage_for_disaster(keys, disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    pre_disaster_start_date = disaster_date - pre_disaster

    imm_disaster_start_date = disaster_date

    post_disaster_start_date = disaster_date + imm_disaster
    post_disaster_end_date = post_disaster_start_date + post_disaster + timedelta(days=1)

    intervals = [pre_disaster_start_date, imm_disaster_start_date, post_disaster_start_date, post_disaster_end_date]



    tag_key_value_intervals = db_utils.get_tag_key_value_usage_for_disaster(keys, disaster_id, intervals)


    headers = ["key","value","count", "percent_of_total_changes_for_key"]
    for tag_key_values, interval, row_index in list(zip(tag_key_value_intervals, ["pre","imm","post"], [0,1,2])):

        unique_tag_value_counts = {}
        for res in tag_key_values:
            key = res[0]
            value = res[1]
            count= res[2]
            if key not in unique_tag_value_counts:
                unique_tag_value_counts[key] = [set(), 0] 
            unique_tag_value_counts[key][0].add(value)  
            unique_tag_value_counts[key][1] += count     

        file_path = f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{interval}.csv"
        with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()

            for res in tag_key_values:
                key=res[0]
                value=res[1]
                count=res[2]
                writer.writerow({"key": key, "value":value, "count": count, "percent_of_total_changes_for_key": round(count/unique_tag_value_counts[key][1] * 100, 4)})

        visualisation_file_path = f"visualisation-site/public/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{interval}.csv"
        shutil.copyfile(file_path, visualisation_file_path)
        

    
# Please emsure initial tag key investigation has been run first, as the csv generated by get_tag_keys() is necessary
if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    print("Getting key value counts")
    specified_keys = ["building","highway","name","surface","amenity","landuse","waterway","natural"]
    get_key_value_counts(specified_keys)

    nums = [10, 25, 100]
    disaster_ids =  [1,2,3,4,5,6]

    for n in nums:
        get_top_n_values_for_keys_all_periods(n)
        pass

    print("Getting tag key,value pairs for individual disasters")
    for disaster_id in disaster_ids:
        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
        print(f"{disaster_country[0]} {disaster_date.year}")
        get_tag_key_value_usage_for_disaster(specified_keys, disaster_id, disaster_date, 365, 30, 365)


    print("Getting top n tag key values for periods")
    for period in ["pre","imm","post"]:
        for n in nums:
            get_top_n_values_for_keys_period(specified_keys, n, period, disaster_ids)