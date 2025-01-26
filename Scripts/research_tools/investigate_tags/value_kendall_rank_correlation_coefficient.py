import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil

from scipy.stats import kendalltau, pearsonr
from sklearn.metrics.pairwise import cosine_similarity

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))

from db_utils import DB_Utils

def compute_key_value_correlation_metrics(top_n, specified_keys, period, disaster_id):

         # Print the filtered data for debugging (optional)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)


    period1, period2 = period
    if disaster_id =="all":
        period1_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_100_key_values/{period1}.csv")
        period2_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_100_key_values/{period2}.csv")

    else:
        period1_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{period1}.csv")
        period2_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{period2}.csv")


    period1_data = period1_data[period1_data["key"].isin(specified_keys)]
    period2_data = period2_data[period2_data["key"].isin(specified_keys)]

    # TODO: This needs updating as it just takes the top 10 for each key, but we need to ensure that the same values are being used.
    #  Could do top 10 from first period, or union of both top 10 - either way needs to be consistent

    # Sort and take the top 10 for each key
    period1_data = (
        period1_data.sort_values(by="count", ascending=False)
                    .groupby("key")
                    .head(top_n)
    )
    period2_data = (
        period2_data.sort_values(by="count", ascending=False)
                    .groupby("key")
                    .head(top_n)
    )

     # For each key - compute the kendall correlation coefficient
    results = []
    for key in specified_keys:
        period1_key_value_data = period1_data[period1_data['key'] == key].copy()
        period2_key_value_data = period2_data[period2_data['key'] == key].copy()

        results.append(periods_compute_correlation_metrics(period1, period2, period1_key_value_data, period2_key_value_data, key))

        headers = ["period1","period2","key","kendall_rank_correlation", "kendall_p_value","cosine_similarity","pearson_correlation","pearson_p_value"]

        if disaster_id == "all":
            os.makedirs(f"./Results/TagInvestigation/summary/key_value_correlation_rank_analysis/", exist_ok=True)
            file_path = f"./Results/TagInvestigation/summary/key_value_correlation_rank_analysis/{period1}_{period2}.csv"
        else:
            os.makedirs(f"./Results/TagInvestigation/disaster{disaster_id}/key_value_correlation_rank_analysis/", exist_ok=True)
            file_path = f"./Results/TagInvestigation/disaster{disaster_id}/key_value_correlation_rank_analysis/{period1}_{period2}.csv"


    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        for result in results:
            writer.writerow(result)

    if disaster_id == "all":
        os.makedirs(f"visualisation-site/public/TagInvestigation/summary/key_value_correlation_rank_analysis/", exist_ok=True)
        visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/key_value_correlation_rank_analysis/{period1}_{period2}.csv"
    else:
        os.makedirs(f"visualisation-site/public/TagInvestigation/disaster{disaster_id}/key_value_correlation_rank_analysis/", exist_ok=True)
        visualisation_file_path = f"visualisation-site/public/TagInvestigation/disaster{disaster_id}/key_value_correlation_rank_analysis/{period1}_{period2}.csv"
    shutil.copyfile(file_path, visualisation_file_path)


def periods_compute_correlation_metrics(period1, period2, period1_data, period2_data, key):


    period1_data['rank'] = period1_data['count'].rank(ascending=False, method='min')
    period2_data['rank'] = period2_data['count'].rank(ascending=False, method='min')


    merged= pd.merge(period1_data, period2_data, on='value', suffixes=(f'_{period1}', f'_{period2}'))

    period1_ranks = merged[f'rank_{period1}'].values
    period2_ranks = merged[f'rank_{period2}'].values
    period1_counts = merged[f'count_{period1}'].values
    period2_counts = merged[f'count_{period2}'].values


    kendall_corr, kendall_p = kendalltau(period1_ranks, period2_ranks)

    if len(period1_counts) > 0 and len(period2_counts) > 0:
        cosine_sim = cosine_similarity([period1_counts], [period2_counts])[0][0]
        pearson_corr, pearson_p = pearsonr(period1_counts, period2_counts)
    else:
        cosine_sim = 0
        pearson_corr, pearson_p = 0, 0

    results = {
        "period1": period1,
        "period2": period2,
        "key": key,
        "kendall_rank_correlation": round(kendall_corr,4),
        "kendall_p_value": round(kendall_p,7),
        "cosine_similarity": round(cosine_sim,4),
        "pearson_correlation": round(pearson_corr,4),
        "pearson_p_value": pearson_p,
    } 
    return results


# Please emsure tag value investigation has been run first, as the csvs generated are necessary
if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Get the values for the specified keys
    specified_keys = ["building","highway","surface","amenity","landuse","waterway","natural"]
    periods = [("pre","imm"), ("pre","post"), ("imm","post")]
    disaster_ids =  [2,3,4,5,6]
    top_n = 10

    
    for period in periods:
        print(period)
        print("Getting all disaster correlation metrics")
        compute_key_value_correlation_metrics(top_n, specified_keys, period, "all")
        
        for disaster_id in disaster_ids:
            (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
            print(f"Generating correlation metrics for {disaster_area[0]} {disaster_date.year}")
            compute_key_value_correlation_metrics(top_n, specified_keys, period, disaster_id)
        