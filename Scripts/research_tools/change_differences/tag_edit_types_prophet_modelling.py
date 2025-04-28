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


@contextmanager
def suppress_stdout_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def train_forecast_prophet_tags(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length, disaster_date):

    tag_changes_df = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv")
 
    tag_changes_df["start_date"] = pd.to_datetime(tag_changes_df["start_date"])
    tag_changes_df["num_tag_total"] = tag_changes_df["num_tag_creates"] + tag_changes_df["num_tag_edits"] + tag_changes_df["num_tag_deletes"]


    pre_disaster_df = tag_changes_df[tag_changes_df["start_date"] < (disaster_date - timedelta(days=58))]

    covid_start = '2020-01-01'
    covid_end = '2020-06-30'

    # Filter out major spikes that affect prophet training
    # Dont filter out for California wildfires and Izmir
    pre_disaster_df = pre_disaster_df.rename(columns={"start_date": "ds"})

    if disaster_id not in [7, 11]:
        pre_disaster_df = pre_disaster_df[
            ~((covid_start <= pre_disaster_df['ds']) & (pre_disaster_df['ds'] <= covid_end))
        ]


    tag_creates_df = pre_disaster_df[["ds", "num_tag_creates"]].rename(columns={"num_tag_creates": "y"})
    tag_edits_df = pre_disaster_df[["ds", "num_tag_edits"]].rename(columns={"num_tag_edits": "y"})
    tag_deletes_df = pre_disaster_df[["ds", "num_tag_deletes"]].rename(columns={"num_tag_deletes": "y"})
    tag_total_df = pre_disaster_df[["ds", "num_tag_total"]].rename(columns={"num_tag_total": "y"})

    with suppress_stdout_stderr():
        model_creates = Prophet()
        model_creates.fit(tag_creates_df)

        model_edits = Prophet()
        model_edits.fit(tag_edits_df)

        model_deletes = Prophet()
        model_deletes.fit(tag_deletes_df)

        model_total = Prophet()
        model_total.fit(tag_total_df)

    # Save models
    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/models", exist_ok=True)

    with open(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/models/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_tag_creates_model.json", 'w') as fout:
        fout.write(model_to_json(model_creates)) 

    with open(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/models/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_tag_edits_model.json", 'w') as fout:
        fout.write(model_to_json(model_edits)) 

    with open(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/models/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_tag_deletes_model.json", 'w') as fout:
        fout.write(model_to_json(model_deletes)) 

    with open(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/models/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_tag_total_model.json", 'w') as fout:
        fout.write(model_to_json(model_total)) 

    return (model_creates, model_edits, model_deletes, model_total)

def evaluate_prophet_model_forecast_tags(models, disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):

    tag_changes_df = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv")

    # Ensure start_date is correctly formatted
    tag_changes_df["start_date"] = pd.to_datetime(tag_changes_df["start_date"])

    # Focus only on **post-disaster predictions**
    post_disaster_start = disaster_date + timedelta(days=imm_disaster_days)
    r
    tag_changes_df = tag_changes_df[tag_changes_df["start_date"] >= post_disaster_start].reset_index(drop=True)

    # Create future dataframe for Prophet predictions
    future_dates = tag_changes_df[["start_date"]].rename(columns={"start_date": "ds"})

    # Unpack trained Prophet models
    model_creates, model_edits, model_deletes, model_total = models


    # Generate predictions
    pred_creates = model_creates.predict(future_dates)
    pred_edits = model_edits.predict(future_dates)
    pred_deletes = model_deletes.predict(future_dates)
    pred_total = model_total.predict(future_dates)

     # Ensure predictions have valid yhat values
    pred_creates["yhat"] = pred_creates["yhat"].clip(lower=0)
    pred_edits["yhat"] = pred_edits["yhat"].clip(lower=0)
    pred_deletes["yhat"] = pred_deletes["yhat"].clip(lower=0)
    pred_total["yhat"] = pred_total["yhat"].clip(lower=0)

    # Extract predicted values
    predictions_df = pd.DataFrame({
        "start_date": future_dates["ds"],
        "num_tag_creates": pred_creates["yhat"],
        "num_tag_edits": pred_edits["yhat"],
        "num_tag_deletes": pred_deletes["yhat"],
        "num_tag_total": pred_total["yhat"]
    })
    
    pred_file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_prophet_predictions.csv"
    predictions_df.to_csv(pred_file_path, index=False)


    # Compute evaluation metrics (MAE & MAPE)
    mae = {}
    mape = {}

    for column in ["num_tag_creates", "num_tag_edits", "num_tag_deletes", "num_tag_total"]:
        mae[column] = np.mean(np.abs(predictions_df[column] - tag_changes_df[column]))
        mape[column] = np.mean(np.abs((predictions_df[column] - tag_changes_df[column]) / tag_changes_df[column].replace(0, 1))) * 100

    mae_row = pd.DataFrame(mae, index=["mae"])
    mape_row = pd.DataFrame(mape, index=["mape"])
    predictions_with_errors_df = pd.concat([mae_row, mape_row], ignore_index=False)

    # Save the DataFrame with MAE and MAPE values
    error_file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_prophet_predictions_errors.csv"
    predictions_with_errors_df.to_csv(error_file_path, index=False)



def generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only,  plot_edit_types, interval_length):

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

        # Compute counts
        num_tag_creates = changes["tags_created"].apply(len).sum()
        num_tag_edits = changes["tags_edited"].apply(len).sum()
        num_tag_deletes = changes["tags_deleted"].apply(len).sum()
        num_tag_total = num_tag_creates + num_tag_edits + num_tag_deletes

        # Store values
        intervals_df.loc[i, "num_tag_creates"] = num_tag_creates
        intervals_df.loc[i, "num_tag_edits"] = num_tag_edits
        intervals_df.loc[i, "num_tag_deletes"] = num_tag_deletes
        intervals_df.loc[i, "num_tag_total"] = num_tag_total 

    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data", exist_ok=True)
    file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv"
    intervals_df.to_csv(file_path, index=False)

    print(f"Saved: {file_path}")


    # Generate prophet models
    if prophet_model:
        prophet_model_pre_disaster_days = 365*3
    
        models = train_forecast_prophet_tags(disaster_id, prophet_model_pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length, disaster_date)
        evaluate_prophet_model_forecast_tags(models, disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length)



def plot_tag_changes(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model, post_only, interval_length, plot_edit_types):

    tag_changes_df = pd.read_csv(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_intervals.csv")

    time_period = "day" if interval_length == 1 else "week" if interval_length == 7 else "month"

    # Load actual tag change data
    tag_changes_df["start_date"] = pd.to_datetime(tag_changes_df["start_date"])

    # Define time range for plotting
    if post_only:
        before = disaster_date
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)
    else:
        before = disaster_date - timedelta(days=pre_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    # Filter data for the time range
    tag_changes_df = tag_changes_df[(before <= tag_changes_df["start_date"]) & (tag_changes_df["start_date"] < after)]

    # Load Prophet predictions if enabled
    if prophet_model:
        pred_file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_prophet_predictions.csv"
        pred_errors_file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{interval_length}_prophet_predictions_errors.csv"

        predictions_df = pd.read_csv(pred_file_path)
        predictions_df["start_date"] = pd.to_datetime(predictions_df["start_date"])

        errors_df = pd.read_csv(pred_errors_file_path)

        # Filter predictions for the same time range
        predictions_df = predictions_df[(before <= predictions_df["start_date"]) & (predictions_df["start_date"] < after)]


    # Plot setup
    plt.figure(figsize=(12, 8))

    # Plot actual tag changes
    color_map = {"creates": "blue", "edits": "orange", "deletes": "green", "total": "red"}
    
    for change_type in plot_edit_types:
        plt.plot(tag_changes_df["start_date"], tag_changes_df[f"num_tag_{change_type}"], 
                 label=f"{change_type.capitalize()}", linestyle="-", marker=".", color=color_map[change_type])


    # Plot Prophet predictions if enabled
    if prophet_model:
        for change_type in plot_edit_types:
  
            mae = errors_df.iloc[0][f"num_tag_{change_type}"]
            mape = errors_df.iloc[1][f"num_tag_{change_type}"]

            mae = int(mae) if not np.isinf(mae) else "N/A"
            mape = round(mape, 1) if not np.isinf(mape) else "N/A"

            plt.plot(predictions_df["start_date"], predictions_df[f"num_tag_{change_type}"], 
                     label=f"{change_type.capitalize()} Prediction (MAE: {mae}, MAPE: {mape}%)",
                     linestyle="--", color=color_map[change_type])
            
        # Select data based on time_period
    if interval_length == 1:
        title = "Daily tag changes"
    elif interval_length == 7:
        title = "Weekly tag changes"
    elif interval_length == 30:
        title = "Monthly tag changes"
    else:
        raise ValueError("Invalid time_period. Choose from 'day', 'week', or 'month'.")

    # Formatting
    plt.title(f'{title} in {disaster_area[0]}, {disaster_country[0]} | {disaster_date.year}')
    plt.xlabel("Date")
    plt.ylabel("Tag Changes Count")
    plt.axvline(x=disaster_date, color="purple", linestyle="--", linewidth=1, label="Disaster Date")
    plt.axvline(x=disaster_date + timedelta(days=imm_disaster_days), color="firebrick", linestyle="--", linewidth=1, label="Post Disaster Start")

    plt.legend()
    plt.grid(which='major', color='black', linestyle='-', linewidth=0.5)
    plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    plt.minorticks_on()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=90 if pre_disaster_days > 365 else 45)

    plt.rcParams.update({
        'font.size': 16,         # Bigger base font
        'axes.titlesize': 18,    # Title font size
        'axes.labelsize': 16,    # Axes label size
        'xtick.labelsize': 15,   # X-axis tick label size
        'ytick.labelsize': 15,   # Y-axis tick label size
        'legend.fontsize': 12.5,   # Legend font size
        'figure.titlesize': 25,  # Overall figure title size
    })

   
    plt.legend()
    plt.tight_layout()
    # Save the plot
    os.makedirs(f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/charts", exist_ok=True)
    file_path = f"./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{time_period}_tag_changes{'_prophet_forecast' if prophet_model else ''}{'' if len(plot_edit_types) == 4 else '_'+'_'.join(plot_edit_types)}{'_post_only' if post_only else ''}.png"

    plt.savefig(file_path, dpi=300)
    print(f"Saved plot: {file_path}")

    # Copy to visualization site
    os.makedirs(f"visualisation-site/public/ChangeDifferences/disaster{disaster_id}/tag_changes/charts", exist_ok=True)
    shutil.copyfile(file_path, f"visualisation-site/public/ChangeDifferences/disaster{disaster_id}/tag_changes/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{time_period}_tag_changes{'_prophet_forecast' if prophet_model else ''}{'' if len(plot_edit_types) == 4 else '_'+'_'.join(plot_edit_types)}{'_post_only' if post_only else ''}.png")

    # Close figure to free memory
    plt.close()



def plot_tag_changes_all_disasters(disaster_ids, prophet_model, post_only, period, interval_length, columns, disaster_ids_type, plot_edit_types):
    time_period = "day" if interval_length == 1 else "week" if interval_length == 7 else "month"

    num_disasters = len(disaster_ids)
    rows = math.ceil(num_disasters / columns)

    # Create a figure grid for all disasters
    fig, axes = plt.subplots(rows, columns, figsize=(columns * 12, rows * 7))

    for idx, disaster_id in enumerate(disaster_ids):
        row, col = divmod(idx, columns)
        ax = axes[row, col] if rows > 1 else axes[col]
        
        # Construct the file path dynamically
        file_path = f'./Results/ChangeDifferences/disaster{disaster_id}/tag_changes/charts/{period[0]}_{period[1]}_{period[2]}_{time_period}_tag_changes{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_" + "_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png'

        if os.path.exists(file_path):
            img = mpimg.imread(file_path)  # Load the image
            ax.imshow(img)
            ax.axis("off")  # Disable axes
            del img

    # Remove any extra/unused axes if the grid is larger than the number of disasters
    for idx in range(num_disasters, rows * columns):
        fig.delaxes(axes.flatten()[idx])

    # Remove padding for a tight layout
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

    # Save the final combined figure
    os.makedirs(f"./Results/ChangeDifferences/combined/tag_changes/charts/", exist_ok=True)
    output_path = f'./Results/ChangeDifferences/combined/tag_changes/charts/{period[0]}_{period[1]}_{period[2]}_{time_period}_tag_changes{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_" + "_".join(plot_edit_types)}{"_post_only" if post_only else ""}_grid_{disaster_ids_type}.png'
    plt.savefig(output_path, dpi=200, bbox_inches="tight", pad_inches=0)

    print(f"Saved: {output_path}")

    # Copy to visualization site
    os.makedirs(f"visualisation-site/public/ChangeDifferences/combined/tag_changes/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/ChangeDifferences/combined/tag_changes/charts/{period[0]}_{period[1]}_{period[2]}_{time_period}_tag_changes{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_" + "_".join(plot_edit_types)}{"_post_only" if post_only else ""}_grid_{disaster_ids_type}.png'
    shutil.copyfile(output_path, visualisation_file_path)

    print(f"Saved: {visualisation_file_path}")

    plt.close()


def compute_specific(disaster_id, periods, prophet_model_bools,  post_only_bools, plot_edit_types_list):
    db_utils = DB_Utils()
    db_utils.db_connect()
    for post_only in post_only_bools:
        for prophet_model in prophet_model_bools:
            for plot_edit_types in plot_edit_types_list:
                for period in periods:
                    pre_disaster_days, imm_disaster_days, post_disaster_days = period

                    (_, disaster_country, disaster_area, _, disaster_date, _, _) = db_utils.get_disaster_with_id(disaster_id)
                    generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, plot_edit_types, interval_length=1)
                    generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, plot_edit_types, interval_length=7)
                    generate_average_by_interval_length(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model,  post_only, plot_edit_types, interval_length=30)

def generate_specific_plot(disaster_id, periods, prophet_model_bools,  post_only_bools, plot_edit_types_list):
    db_utils = DB_Utils()
    db_utils.db_connect()
    for post_only in post_only_bools:
        for prophet_model in prophet_model_bools:
            for plot_edit_types in plot_edit_types_list:
                for period in periods:
                    pre_disaster_days, imm_disaster_days, post_disaster_days = period

                    (_, disaster_country, disaster_area, _, disaster_date, _, _) = db_utils.get_disaster_with_id(disaster_id)
                    plot_tag_changes(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, interval_length=1, plot_edit_types=plot_edit_types)
                    plot_tag_changes(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, interval_length=7, plot_edit_types=plot_edit_types)
                    plot_tag_changes(disaster_id, disaster_area, disaster_country, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model,  post_only, interval_length=30, plot_edit_types=plot_edit_types)

def process_combined_disaster_plots(disaster_ids, plot_edit_types_list, period, prophet_model_bools, post_only_bools, interval_lengths, columns, disaster_ids_type):
    for plot_edit_types in plot_edit_types_list:
        for post_only in post_only_bools:
            for prophet_model in prophet_model_bools:
                for interval_length in interval_lengths:
                    plot_tag_changes_all_disasters(
                        disaster_ids, 
                        prophet_model, 
                        post_only, 
                        period, 
                        interval_length, 
                        columns, 
                        disaster_ids_type, 
                        plot_edit_types
                    )



# Ensure that you have already run analyse_change_differences for the specified disaster and period
if __name__ == "__main__":


    prophet_model_bools = [True, False]
    post_only_bools = [False, True]
    periods = [(1095,60,365),(365,60,365)]
    interval_lengths = [1,7,30]
    
    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = range(2,19)
        disaster_ids = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]
        print("Disaster IDs defined:", disaster_ids)

    compute_specific_bool = False
    generate_specific_plot_bool = True
    generate_combined = True

    #disaster_ids = [2]

    plot_edit_types_list = [["creates", "edits", "deletes", "total"],["creates"],["edits"],["deletes"],["total"]]
    #plot_edit_types_list = [["creates", "edits", "deletes", "total"],]

    plot_edit_types_list = [["creates", "edits", "deletes", "total"]]
    periods = [(365,60,365)]
    interval_lengths = [7]

    if compute_specific_bool: 

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Submit tasks for each disaster_id
            futures = {
                executor.submit(
                    compute_specific, 
                    disaster_id, 
                    periods, 
                    prophet_model_bools, 
                    post_only_bools, 
                    plot_edit_types_list,
                ): disaster_id for disaster_id in disaster_ids
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                disaster_id = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    print(f"Error processing disaster_id {disaster_id}: {e}")

    if generate_specific_plot_bool: 

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Submit tasks for each disaster_id
            futures = {
                executor.submit(
                    generate_specific_plot, 
                    disaster_id, 
                    periods, 
                    prophet_model_bools, 
                    post_only_bools, 
                    plot_edit_types_list,
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
        disaster_ids_region = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]  # Geographic region
        disaster_ids_disaster = [3,6,11,5,12,17,8,9,13,2,15,16,10,7,18,14]  # Disaster type
        

        disaster_ids_types = ["type", "region"]  # "region", "type"

        for disaster_ids_type in disaster_ids_types:
            disaster_ids = disaster_ids_region if disaster_ids_type == "region" else disaster_ids_disaster

            # Use ProcessPoolExecutor for multiprocessing
            with concurrent.futures.ProcessPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        process_combined_disaster_plots, 
                        disaster_ids, 
                        plot_edit_types_list, 
                        period, 
                        prophet_model_bools, 
                        post_only_bools, 
                        interval_lengths, 
                        columns=4,
                        disaster_ids_type=disaster_ids_type
                    ): period for period in periods
                }

                # Collect results as tasks complete
                for future in concurrent.futures.as_completed(futures):
                    period = futures[future]
                    try:
                        result = future.result()
                        print(f"Successfully processed period {period}: {result}")
                    except Exception as e:
                        print(f"Plotting failed for period {period}: {e}")


