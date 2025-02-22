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
import shutil
import concurrent.futures
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def generate_intervals(pre_disaster, imm_disaster, post_disaster, disaster_date, interval_length):

    start_range = disaster_date - timedelta(days=1095)
    end_range = disaster_date + imm_disaster+ post_disaster + timedelta(days=1)


    intervals = []
    current = start_range
    while current < end_range:  
        next_interval = current + timedelta(days=interval_length)
        intervals.append({'start_date': current, 'end_date': min(next_interval, end_range)})  
        current = next_interval


    cutoff_start = disaster_date - pre_disaster  
    intervals = [t for t in intervals if t['start_date'] >= cutoff_start]

    return pd.DataFrame(intervals)



def train_forecast_prophet(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):

     # Load the averages we just saved - in general we will go for pre_disaster_days = 365*3 as we have 3 years of data to train on
    interval_averages_df = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv")
    # Offset the training away from the disaster by a set number of days, to reduce likelihood that changes in run up to disaster skew model
    disaster_day_offset = 58
    pre_disaster_avgs = interval_averages_df.iloc[:(pre_disaster_days - disaster_day_offset)// interval_length]
    pre_disaster_average_timestamps_df = pre_disaster_avgs.rename(columns={"start_date": "ds", "avg_days_between_edits": "y"}).drop(columns=['end_date'], inplace=False)

    # Potentially filter out whatever occurs during major spikes eg covid or maybe we keep?
    #with suppress_stdout_stderr():

    model_timestamps_between_changes = Prophet()
    model_timestamps_between_changes.fit(pre_disaster_average_timestamps_df)
    with open(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_timestamp_between_changes_prophet_model.json", 'w') as fout:
        fout.write(model_to_json(model_timestamps_between_changes)) 

    return model_timestamps_between_changes

def evaluate_prophet_model_forecast(model, disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length,):
    interval_averages_df = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv")
    interval_averages_df = interval_averages_df.dropna(how="all")
    # Ensure start_date is correctly formatted
    interval_averages_df["start_date"] = pd.to_datetime(interval_averages_df["start_date"], errors="coerce")

    interval_averages_df = interval_averages_df[interval_averages_df["start_date"] >= disaster_date].reset_index(drop=True)

    pre_imm_post_future = interval_averages_df[["start_date"]].dropna().rename(columns={"start_date": "ds"}) 
    pre_imm_post_future = pre_imm_post_future[pre_imm_post_future["ds"] >= disaster_date]


    model_days_prediction = model.predict(pre_imm_post_future)
    
    model_days_prediction_df = pd.DataFrame({"start_date":pre_imm_post_future['ds'],"avg_days_between_edits": model_days_prediction["yhat"]})
    file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_avg_days_between_edits_prophet_predictions.csv"
    model_days_prediction_df.to_csv(file_path, index=False)

    # Compute the mean average error and mean average percentage error 
    # TODO This should only be computed for the post disaster period
    mae = np.mean(np.abs(model_days_prediction_df["avg_days_between_edits"] - interval_averages_df["avg_days_between_edits"]))
    mape = np.mean(np.abs((model_days_prediction_df["avg_days_between_edits"] - interval_averages_df["avg_days_between_edits"]) / interval_averages_df["avg_days_between_edits"].replace(0, 1))) * 100
    predictions_with_errors_df = pd.DataFrame([{"mae": mae, "mape": mape}])

    # Save the DataFrame with MAE and MAPE values
    predictions_with_errors_df.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_avg_days_between_edits_prophet_predictions_errors.csv", index=False)


def generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, interval_length):

    diff_pre =  pd.read_pickle(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_pre.pickle")
    diff_imm =  pd.read_pickle(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_imm.pickle")
    diff_post =  pd.read_pickle(f"./Results/ChangeDifferences/disaster{disaster_id}/change_differences/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_post.pickle")
    
    diff = pd.concat([diff_pre, diff_imm, diff_post], ignore_index=True)

    
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    # Calculate the start and end date range

    # Create intervals 
    intervals_df = generate_intervals(pre_disaster, imm_disaster, post_disaster, disaster_date, interval_length)

    for i in range(len(intervals_df) - 1):
        interval = intervals_df.iloc[i]
        start = interval["start_date"]
        end = interval["end_date"]

        changes = diff[(start <= diff["timestamp_curr"]) & (diff["timestamp_curr"] <= end)]

        if not changes.empty:
            median_value = (changes["timestamp_between_edits"].dt.total_seconds() / 86400).median()  # Convert seconds to days
        else:
            median_value = 0  # Handle empty intervals

        # Store the median value as days
        intervals_df.loc[i, "avg_days_between_edits"] = median_value

    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data", exist_ok=True)
    intervals_df.to_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv")

    # Generate prophet models
    if prophet_model:
        prophet_model_pre_disaster_days = 365*3
        model = train_forecast_prophet(disaster_id, prophet_model_pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length)
        evaluate_prophet_model_forecast(model, disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length)



    plot_average_time_between_edits(intervals_df, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, disaster_date, interval_length, disaster_id, disaster_area, disaster_country)

def plot_average_time_between_edits(intervals_df, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model, post_only, disaster_date, interval_length, disaster_id, disaster_area, disaster_country):
    # Define the time period for the plot
    time_period = "day" if interval_length == 1 else "week" if interval_length == 7 else "month"


    if post_only:
        #before = disaster_date + timedelta(days=imm_disaster_days)
        before = disaster_date 
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)
    else:
        before = disaster_date - timedelta(days=pre_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    if prophet_model:
         
        file_path = f'./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_avg_days_between_edits_prophet_predictions'
        predictions = pd.read_csv(file_path+".csv")
        errors = pd.read_csv(f"{file_path}_errors.csv")

        """
        if post_only:
            before_prophet = disaster_date + timedelta(days=imm_disaster_days)
        else:
            before_prophet = disaster_date
        """
        before_prophet = disaster_date
        predictions['start_date'] = pd.to_datetime(predictions['start_date'])
        predictions = predictions[(before_prophet < pd.to_datetime(predictions['start_date'])) & (pd.to_datetime(predictions['start_date']) < after)]


    intervals_df = intervals_df[(before < pd.to_datetime(intervals_df['start_date'])) & (pd.to_datetime(intervals_df['start_date']) < after)]   

    # Plot the data
    plt.figure(figsize=(12, 7))
    plt.plot(intervals_df["start_date"], intervals_df["avg_days_between_edits"], label="Median Number of Days Between Changes", marker='o', linestyle='-', color='red')

    if prophet_model:
        mae = int(errors.iloc[0]["mae"])
        mape = round(errors.iloc[0]["mape"],1) if not np.isinf(errors.iloc[0]["mape"]) else "N/A"
        plt.plot(predictions['start_date'], predictions['avg_days_between_edits'], label=f'Prophet Prediction (MAE: {mae}, MAPE: {mape}%)', linestyle='--', color='red')

    # Add labels and title
    plt.title(f"Median days between changes ({time_period.capitalize()}) {disaster_area[0]}, {disaster_country[0]} | {disaster_date.year}")
    plt.xlabel("Date")
    plt.ylabel("Median Days Between changes")
    plt.axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    plt.axvline(x=disaster_date+timedelta(imm_disaster_days), color='firebrick', linestyle='--', linewidth=1, label='Post Disaster Period Start')
    plt.grid(which='major', linestyle='--', linewidth=0.5)
    plt.grid(which='minor', linestyle=':', linewidth=0.5)
    plt.minorticks_on()

    # Format the x-axis
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    if post_only:
        post_disaster_data = intervals_df[intervals_df['start_date'] >= disaster_date + timedelta(days=imm_disaster_days)]

        # Collect max values only for the plotted types
        max_post_values = [
            post_disaster_data['avg_days_between_edits'].max()
        ]

        if prophet_model:
            post_disaster_predictions = predictions[predictions['start_date'] >= disaster_date + timedelta(days=imm_disaster_days)]
            max_post_values.append(post_disaster_predictions['avg_days_between_edits'].max())
    
        # Ensure we have valid data to scale
        if max_post_values and not all(np.isnan(max_post_values)):  
            y_max = 1.2 * max([v for v in max_post_values if not np.isnan(v)])  
            plt.ylim(0, y_max)

    plt.legend()

    # Save the plot
    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/charts", exist_ok=True)
    file_path =  f'./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_avg_days_between_edits{"_prophet_forecast" if prophet_model else ""}{"_post_only" if post_only else ""}.png'
    plt.savefig(file_path, dpi=300)
    print(f"Plot saved: {file_path}")

    os.makedirs(f"visualisation-site/public/ChangeDifferences/disaster{disaster_id}/days_between_edits/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/ChangeDifferences/disaster{disaster_id}/days_between_edits/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_avg_days_between_edits{"_prophet_forecast" if prophet_model else ""}{"_post_only" if post_only else ""}.png'
    shutil.copyfile(file_path, visualisation_file_path)
    # Close the plot to free memory
    plt.close()

def plot_average_time_between_edits_all_disasters(disaster_ids, prophet_model, post_only, period, interval_length, columns, disaster_ids_type):

    num_disasters = len(disaster_ids)
    rows = math.ceil(num_disasters / columns)

    # Adjust the figure size to fit tightly without space
    fig, axes = plt.subplots(rows, columns, figsize=(columns * 12, rows * 7))


    # Iterate through disasters
    for idx, disaster_id in enumerate(disaster_ids):
        row, col = divmod(idx, columns)
        ax = axes[row, col] if rows > 1 else axes[col]

        file_path = f'./Results/ChangeDifferences/disaster{disaster_id}/days_between_edits/charts/{period[0]}_{period[1]}_{period[2]}_{interval_length}_avg_days_between_edits{"_prophet_forecast" if prophet_model else ""}{"_post_only" if post_only else ""}.png'

        if os.path.exists(file_path):
            img = mpimg.imread(file_path)  # Load the image
            ax.imshow(img)
            ax.axis('off')  # Disable axes
            del img

    # Remove any extra/unused axes if the grid is larger than the number of disasters
    for idx in range(num_disasters, rows * columns):
        fig.delaxes(axes.flatten()[idx])

    # Eliminate all padding between subplots
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)


    # Save the final combined figure
    os.makedirs(f"./Results/ChangeDifferences/combined/days_between_edits/charts/", exist_ok=True)
    output_path = f'./Results/ChangeDifferences/combined/days_between_edits/charts/{period[0]}_{period[1]}_{period[2]}_{interval_length}_avg_days_between_edits{"_prophet_forecast" if prophet_model else ""}{"_post_only" if post_only else ""}_grid_{disaster_ids_type}.png'
    plt.savefig(output_path, dpi=200, bbox_inches='tight', pad_inches=0)

    print(f"Saved: {output_path}")

    os.makedirs(f"visualisation-site/public/ChangeDifferences/combined/days_between_edits/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/ChangeDifferences/combined/days_between_edits/charts/{period[0]}_{period[1]}_{period[2]}_{interval_length}_avg_days_between_edits{"_prophet_forecast" if prophet_model else ""}{"_post_only" if post_only else ""}_grid_{disaster_ids_type}.png'
    shutil.copyfile(output_path, visualisation_file_path)

    print(f"Saved: {visualisation_file_path}")

    plt.close()

def process_disaster(disaster_id, periods, prophet_model_bools,  post_only_bools):
    db_utils = DB_Utils()
    db_utils.db_connect()
    for post_only in post_only_bools:
        for prophet_model in prophet_model_bools:
            for period in periods:
                pre_disaster_days, imm_disaster_days, post_disaster_days = period

                (_, disaster_country, disaster_area, _, disaster_date, _, _ ) = db_utils.get_disaster_with_id(disaster_id)
                generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, interval_length=1)
                generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, interval_length=7)
                generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model,  post_only, interval_length=30)

def process_time_between_edits_all_disasters(period, disaster_ids, prophet_model_bools, post_only_bools, interval_lengths, disaster_ids_type):
    for post_only in post_only_bools:
        for prophet_model in prophet_model_bools:
            for interval_length in interval_lengths:
                plot_average_time_between_edits_all_disasters(disaster_ids, prophet_model, post_only, period, interval_length, columns=4, disaster_ids_type=disaster_ids_type)


# Ensure that you have already run analyse_change_differences for the specified disaster and period
if __name__ == "__main__":


    prophet_model_bools = [True, False]
    post_only_bools = [ True, False]
    periods = [(1095,60,365), (365,60,365)]
    interval_lengths = [1,7,30]
    
    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = range(2,19)
        disaster_ids = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]
        print("Disaster IDs defined:", disaster_ids)

    generate_specific = False
    generate_combined = True

    if generate_specific: 

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Submit tasks for each disaster_id
            futures = {
                executor.submit(
                    process_disaster, 
                    disaster_id, 
                    periods, 
                    prophet_model_bools, 
                    post_only_bools, 
                ): disaster_id for disaster_id in disaster_ids
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                disaster_id = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    print(f"Error processing disaster_id {disaster_id}: {e}")

    
    if generate_combined:
        disaster_ids_region =   [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17] # Geographic region
        disaster_ids_disaster = [3,6,11,5,12,17,8,9,13,2,15,16,10,7,18,14] # Disaster Type

        disaster_ids_types = ["type","region"] # "region", "type"

        for disaster_ids_type in disaster_ids_types:

            if disaster_ids_type == "region":
                disaster_ids = disaster_ids_region
            else:
                disaster_ids = disaster_ids_disaster

            with concurrent.futures.ProcessPoolExecutor() as executor:
                # Submit tasks for each disaster_id
                futures = {
                    executor.submit(
                        process_time_between_edits_all_disasters, 
                        period, 
                        disaster_ids, 
                        prophet_model_bools, 
                        post_only_bools, 
                        interval_lengths,
                        disaster_ids_type,
                    ): (period, prophet_model_bool) for period in periods for prophet_model_bool in prophet_model_bools
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(futures):
                    disaster_id = futures[future]
                    try:
                        result = future.result()
                        print(result)
                    except Exception as e:
                        print(f"Error processing disaster_id {disaster_id}: {e}")

