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

def all_disasters_compute_correlation_metrics(specified_keys):

    pre_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_100_keys/pre.csv")
    imm_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_100_keys/imm.csv")
    post_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_100_keys/post.csv")

    pre_imm = periods_compute_correlation_metrics("pre","imm", pre_data, imm_data,  specified_keys)
    pre_post = periods_compute_correlation_metrics("pre","post", pre_data, post_data, specified_keys)
    imm_post = periods_compute_correlation_metrics("imm","post", imm_data, post_data, specified_keys)

    headers = ["period1","period2","kendall_rank_correlation", "kendall_p_value","cosine_similarity","pearson_correlation","pearson_p_value"]
    file_path = f"./Results/TagInvestigation/summary/key_correlation_rank_analysis.csv"

    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(pre_imm)
        writer.writerow(pre_post)
        writer.writerow(imm_post)

    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/key_correlation_rank_analysis.csv"
    shutil.copyfile(file_path, visualisation_file_path)
    

def specific_disaster_compute_correlation_metrics(disaster_id, specified_keys):

    pre_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_pre.csv")
    imm_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_imm.csv")
    post_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_post.csv")

    pre_imm = periods_compute_correlation_metrics("pre","imm", pre_data, imm_data,  specified_keys)
    pre_post = periods_compute_correlation_metrics("pre","post", pre_data, post_data, specified_keys)
    imm_post = periods_compute_correlation_metrics("imm","post", imm_data, post_data, specified_keys)

    headers = ["period1","period2","kendall_rank_correlation", "kendall_p_value","cosine_similarity","pearson_correlation","pearson_p_value"]
    file_path = f"./Results/TagInvestigation/disaster{disaster_id}/key_correlation_rank_analysis.csv"

    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerow(pre_imm)
        writer.writerow(pre_post)
        writer.writerow(imm_post)

    visualisation_file_path = f"visualisation-site/public/TagInvestigation/disaster{disaster_id}/key_correlation_rank_analysis.csv"
    shutil.copyfile(file_path, visualisation_file_path)

def periods_compute_correlation_metrics(period1, period2, period1_data, period2_data, specified_keys):

    period1_filtered = period1_data[period1_data['key'].isin(specified_keys)].copy()
    period2_filtered = period2_data[period2_data['key'].isin(specified_keys)].copy()

    period1_filtered['rank'] = period1_filtered['count'].rank(ascending=False, method='min')
    period2_filtered['rank'] = period2_filtered['count'].rank(ascending=False, method='min')

    merged= pd.merge(period1_filtered, period2_filtered, on='key', suffixes=(f'_{period1}', f'_{period2}'))

    period1_ranks = merged[f'rank_{period1}'].values
    period2_ranks = merged[f'rank_{period2}'].values
    period1_counts = merged[f'count_{period1}'].values
    period2_counts = merged[f'count_{period2}'].values


    kendall_corr, kendall_p = kendalltau(period1_ranks, period2_ranks)
    cosine_sim = cosine_similarity([period1_counts], [period2_counts])[0][0]
    pearson_corr, pearson_p = pearsonr(period1_counts, period2_counts)

    results = {
        "period1": period1,
        "period2": period2,
        "kendall_rank_correlation": round(kendall_corr,4),
        "kendall_p_value": round(kendall_p,7),
        "cosine_similarity": round(cosine_sim,4),
        "pearson_correlation": round(pearson_corr,4),
        "pearson_p_value": pearson_p,
    }
    print(results)
    return results

# Please emsure initial tag key investigation has been run first, as the csvs generated are necessary
if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    specified_keys = ["building","highway","source","name","surface","amenity","landuse","waterway","natural"]
    disaster_ids =  range(2,19)

    print("Getting all disaster correlation metrics")
    all_disasters_compute_correlation_metrics(specified_keys)
    
    for disaster_id in disaster_ids:
        (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
        print(f"Generating correlation metrics for {disaster_area[0]} {disaster_date.year}")
        specific_disaster_compute_correlation_metrics(disaster_id, specified_keys)
    