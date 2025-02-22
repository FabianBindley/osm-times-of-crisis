import sys
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
from contextlib import contextmanager
import numpy as np
import ast
from datetime import datetime, timedelta
import csv 
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
import pandas as pd

import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils



def analyse_most_x_keys_all_disasters(period):
    pre_disaster_days, imm_disaster_days, post_disaster_days = period
    change_differences_df = pd.read_csv(f"./Results/ChangeDifferences/summary/all_disaster_analysis_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_.csv")
    # Drop everything except disaster_id, period, most_created_keys, most_edited_keys, most_deleted_keys and their frequencies
    change_differences_df = change_differences_df[['disaster_id', 'period', 'most_created_key', 'most_created_key_frequency','most_edited_key', 'most_edited_key_frequency', 'most_deleted_key', 'most_deleted_key_frequency']]
    
    # Create a results json
    results = {}
    # Store the most frequently most ... key for each period, pre, imm, post

# Define the periods
    periods = ["pre", "imm", "post"]
    results = {}

    for period in periods:
        period_df = change_differences_df[change_differences_df['period'] == period]

        def get_top_3_keys(key_col, freq_col):
            # Count how many disasters each key appeared as the most frequent
            key_disaster_counts = period_df.groupby(key_col)['disaster_id'].nunique()
            key_total_frequencies = period_df.groupby(key_col)[freq_col].sum()

            # Create a DataFrame with both metrics
            key_ranking_df = pd.DataFrame({
                "disaster_count": key_disaster_counts,
                "total_frequency": key_total_frequencies
            }).reset_index().rename(columns={key_col: "key"})

            # Sort first by disasters count (descending), then by total frequency (descending)
            key_ranking_df = key_ranking_df.sort_values(by=["disaster_count", "total_frequency"], ascending=[False, False])

            # Get the top 3 keys
            top_data = key_ranking_df.head(3).to_dict(orient="records")

            return top_data

        # Store results for this period
        results[period] = {
            "most_created": get_top_3_keys("most_created_key", "most_created_key_frequency"),
            "most_edited": get_top_3_keys("most_edited_key", "most_edited_key_frequency"),
            "most_deleted": get_top_3_keys("most_deleted_key", "most_deleted_key_frequency"),
        }

    # Save as JSON
    json_path = f"./Results/ChangeDifferences/summary/most_x_key_analysis_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Analysis saved to: {json_path}")





if __name__ == "__main__":


    prophet_model_bools = [True, False]
    post_only_bools = [False, True]
    periods = [(365,60,365)]

    disaster_ids_region = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]  
    analyse_most_x_keys_all_disasters(periods[0])