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
        period1_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_4000_key_values/{period1}.csv")
        period2_data = pd.read_csv(f"./Results/TagInvestigation/summary/top_n_tag_key_values/top_4000_key_values/{period2}.csv")

    else:
        period1_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{period1}.csv")
        period2_data = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{period2}.csv")


    period1_data = period1_data[period1_data["key"].isin(specified_keys)]
    period2_data = period2_data[period2_data["key"].isin(specified_keys)]

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

    print(period1_data)
    print(period2_data)

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

    print(results)
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



    merged = pd.merge(period1_data, period2_data, on=["key", "value"], suffixes=(f'_{period1}', f'_{period2}'))

    period1_ranks = merged[f'rank_{period1}'].values
    period2_ranks = merged[f'rank_{period2}'].values
    period1_counts = merged[f'count_{period1}'].values
    period2_counts = merged[f'count_{period2}'].values


    kendall_corr, kendall_p = kendalltau(period1_ranks, period2_ranks)

    if len(period1_counts) > 1 and len(period2_counts) > 1:
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



def compute_kendall_rank_statistics(periods, disaster_ids, specified_keys):
    all_correlations = []

    # Load and combine the correlation data for each period and disaster
    for period in periods:
        period1, period2 = period

        # For "all" disaster case, assign disaster_id as "all"
        all_disaster_df = pd.read_csv(f"./Results/TagInvestigation/summary/key_value_correlation_rank_analysis/{period1}_{period2}.csv")
        all_disasters_correlations = all_disaster_df[all_disaster_df['key'].isin(specified_keys)]
        all_disasters_correlations['disaster_id'] = 'all'  # Explicitly add the 'disaster_id' column
        all_disasters_correlations['period1'] = period1
        all_disasters_correlations['period2'] = period2
        all_correlations.append(all_disasters_correlations)
        
        # Then, for each disaster, get the individual disaster correlation data
        for disaster_id in disaster_ids:
            disaster_df = pd.read_csv(
                f"./Results/TagInvestigation/disaster{disaster_id}/key_value_correlation_rank_analysis/{period1}_{period2}.csv"
            )
            disaster_correlations = disaster_df[disaster_df['key'].isin(specified_keys)]
            disaster_correlations['disaster_id'] = disaster_id  # Add disaster_id to track which disaster the data belongs to
            disaster_correlations['period1'] = period1
            disaster_correlations['period2'] = period2
            all_correlations.append(disaster_correlations)

    # Combine all correlation data into one DataFrame
    all_correlations_df = pd.concat(all_correlations, ignore_index=True)

    # Now, generate summary statistics for each key and each period for all disasters and the "all" disaster
    summary_stats = []

    for period in periods:
        period1, period2 = period

        # Filter the data for this period (both "all" disaster and individual disasters)
        period_data = all_correlations_df[
            (all_correlations_df['period1'] == period1) & (all_correlations_df['period2'] == period2)
        ]

        for key in specified_keys:
            key_data = period_data[period_data['key'] == key]

            # Compute the statistics for Kendall Rank Correlation
            summary = {
                "period1": period1,
                "period2": period2,
                "key": key,
                "kendall_min": round(key_data["kendall_rank_correlation"].min(), 3),
                "kendall_max": round(key_data["kendall_rank_correlation"].max(), 3),
                "kendall_range": round(key_data["kendall_rank_correlation"].max() - key_data["kendall_rank_correlation"].min(), 3),
                "kendall_q1": round(key_data["kendall_rank_correlation"].quantile(0.25), 3),
                "kendall_median": round(key_data["kendall_rank_correlation"].median(), 3),
                "kendall_q3": round(key_data["kendall_rank_correlation"].quantile(0.75), 3),
                "kendall_iqr": round(key_data["kendall_rank_correlation"].quantile(0.75) - key_data["kendall_rank_correlation"].quantile(0.25), 3),
            }
            summary_stats.append(summary)

    # Convert the list of summary stats to a DataFrame for better visualization
    summary_df = pd.DataFrame(summary_stats)

    # Add summary row for each key across all periods
    summary_rows = []
    for key in specified_keys:
        key_data = period_data[period_data['key'] == key]
        # Compute the summary statistics for Kendall Rank Correlation
        summary = {
            "period1": "All",
            "period2": "All",
            "key": key,
            "kendall_min": round(key_data["kendall_rank_correlation"].min(), 3),
            "kendall_max": round(key_data["kendall_rank_correlation"].max(), 3),
            "kendall_range": round(key_data["kendall_rank_correlation"].max() - key_data["kendall_rank_correlation"].min(), 3),
            "kendall_q1": round(key_data["kendall_rank_correlation"].quantile(0.25), 3),
            "kendall_median": round(key_data["kendall_rank_correlation"].median(), 3),
            "kendall_q3": round(key_data["kendall_rank_correlation"].quantile(0.75), 3),
            "kendall_iqr": round(key_data["kendall_rank_correlation"].quantile(0.75) - key_data["kendall_rank_correlation"].quantile(0.25), 3),
        }
        summary_rows.append(summary)

    # Create a DataFrame for the summary rows and append to the original DataFrame
    summary_df_all = pd.DataFrame(summary_rows)
    summary_df = pd.concat([summary_df, summary_df_all], ignore_index=True)

    summary_df.sort_values(by=["key"], inplace=True)

    # Save to CSV
    summary_df.to_csv(f"./Results/TagInvestigation/summary/kendall_rank_statistics_summary.csv", index=False)
    print(f"Saved: ./Results/TagInvestigation/summary/kendall_rank_statistics_summary.csv")

    print(summary_df)
    return summary_df

       


# Please emsure tag value investigation has been run first, as the csvs generated are necessary
if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Get the values for the specified keys
    specified_keys = ["building","highway","source","name","surface","amenity","landuse","waterway","natural","leisure","emergency"]

    specified_keys = ["building","highway","amenity","leisure"]
    periods = [("pre","imm"), ("pre","post"), ("imm","post")]
    periods = [("pre","imm"),("pre","post"), ("imm","post")]

    disaster_ids =  range(2,19)
    top_n = 12

    generate_kendall_correlations = False
    compute_statistics = True

    if generate_kendall_correlations:
        for period in periods:
            print(period)
            print("Getting all disaster correlation metrics")
            compute_key_value_correlation_metrics(top_n, specified_keys, period, "all")
            
            for disaster_id in disaster_ids:
                    (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
                    print(f"Generating correlation metrics for {disaster_area[0]} {disaster_date.year}")
                    compute_key_value_correlation_metrics(top_n, specified_keys, period, disaster_id)

    # Generate summary table - for each key, get the relevant average, range, standard deviation, min max, quartiles etc
    if compute_statistics:
        compute_kendall_rank_statistics(periods, disaster_ids, specified_keys)

        