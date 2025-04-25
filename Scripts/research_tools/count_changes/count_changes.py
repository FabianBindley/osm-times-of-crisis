import sys
import os
import ast
from contextlib import contextmanager
import numpy as np
from datetime import datetime, timedelta
import csv 
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
import pandas as pd
import concurrent.futures
import shutil 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils


def compute_total_number_changes_across_disasters(periods, disaster_ids):
    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define headers for total counts and combined dataset
    headers_total_counts = ["creates", "edits", "deletes", "total"]

    for period in periods:
        total_counts = pd.DataFrame(columns=headers_total_counts, data=np.zeros((4, 4)))  # Only 3 rows (pre, imm, post)
        combined_counts = pd.DataFrame(columns=["disaster_id","disaster_label", "pre", "imm", "post", "total"])

        pre_disaster_days, imm_disaster_days, post_disaster_days = period

        for disaster_id in disaster_ids:
            file_path = f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv"
            
            # Read the CSV and only keep the first three rows (pre, imm, post)
            counts = pd.read_csv(file_path)

            # Append to combined_counts with disaster_id and period
            (_, _, disaster_area, _, disaster_date, _, _) = db_utils.get_disaster_with_id(disaster_id)
            new_row = {"disaster_id": disaster_id, "disaster_label": f"{disaster_area[0]} ({disaster_date.year})", "pre": counts.iloc[0]["total"], "imm": counts.iloc[1]["total"], "post": counts.iloc[2]["total"], "total": counts.iloc[3]["total"]}
            combined_counts = pd.concat([combined_counts, pd.DataFrame([new_row])], ignore_index=True)


            counts = pd.read_csv(file_path)

            # Aggregate counts across disasters
            total_counts += counts[headers_total_counts].values

        # Save total counts summary
        output_file = f"./Results/ChangeCounting/summary/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv"
        total_counts.to_csv(output_file, index=False)

        # Add total row to combined_counts
        total_row = {
            "disaster_id": "—",
            "disaster_label": "Total",
            "pre": combined_counts["pre"].sum(),
            "imm": combined_counts["imm"].sum(),
            "post": combined_counts["post"].sum(),
            "total": combined_counts["total"].sum()
        }
        combined_counts = pd.concat([combined_counts, pd.DataFrame([total_row])], ignore_index=True)


        # Save combined counts with disaster IDs and periods
        combined_output_file = f"./Results/ChangeCounting/summary/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_combined_change_count.csv"
        combined_counts.to_csv(combined_output_file, index=False)

        # Ensure visualisation directory exists and save files there as well
        os.makedirs("visualisation-site/public/ChangeCounting/summary/data", exist_ok=True)
        visualisation_file_path = f"visualisation-site/public/ChangeCounting/summary/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_combined_change_count.csv"
        combined_counts.to_csv(visualisation_file_path, index=False)
    

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

def count_full_periods(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    pre_disaster_start_date = disaster_date - pre_disaster

    imm_disaster_start_date = disaster_date

    post_disaster_start_date = disaster_date + imm_disaster
    post_disaster_end_date = post_disaster_start_date + post_disaster + timedelta(days=1)

    intervals = [pre_disaster_start_date, imm_disaster_start_date, post_disaster_start_date, post_disaster_end_date]

    # All changes are now added to changes anyway no need to distinguish
    #if pre_disaster_days > 370:
      #  counts = db_utils.count_changes_in_interval_3_years_pre(disaster_id, intervals)
    #else:
    counts = db_utils.count_changes_in_interval(disaster_id, intervals)

    total_creates = 0
    total_edits = 0
    total_deletes = 0
    total_total = 0
    
    # Save the counts
    if not os.path.exists(f"Results/ChangeCounting/disaster{disaster_id}/data"):
        os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/data")

    headers = ["creates", "edits", "deletes", "total"]
    file_path = f"Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv"

    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()        
        for creates, edits, deletes, total in counts:

            total_creates += creates
            total_edits += edits
            total_deletes += deletes
            total_total += total

            writer.writerow({"creates": creates, "edits": edits, "deletes": deletes, "total": total})
        
        writer.writerow({"creates": total_creates, "edits": total_edits, "deletes": total_deletes, "total": total_total})

        print("Saved full periods")

def count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils, interval_length):
    pre_disaster = timedelta(days=1095) # Always use 1095 days before, then chop off the intervals we dont need
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    # Calculate the start and end date range
    start_range = disaster_date - pre_disaster
    end_range = disaster_date + imm_disaster+ post_disaster + timedelta(days=1)

    # Create intervals 
    intervals = []
    current = start_range
    while current < end_range:  # Ensure no overlap at the end
        intervals.append(current)
        current += timedelta(days=interval_length)
    intervals.append(end_range)  # Include the final end date
    

    cutoff_start = disaster_date - timedelta(days=pre_disaster_days)  # Only keep `pre_disaster_days`
    intervals = [t for t in intervals if t >= cutoff_start]

    #if pre_disaster_days > 370:
        #counts = db_utils.count_changes_in_interval_3_years_pre(disaster_id, intervals)
    #else:
    counts = db_utils.count_changes_in_interval(disaster_id, intervals)

    delta = timedelta(interval_length)


    file_path = f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count.csv"
    headers = ["start_date", "end_date", "creates", "edits", "deletes", "total"]
    
    total_creates = 0
    total_edits = 0
    total_deletes = 0
    total_total = 0
    
    with open(file_path, mode="w", newline='', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        

        for (creates, edits, deletes, total), (interval) in list(zip(counts, intervals)):

            total_creates += creates
            total_edits += edits
            total_deletes += deletes
            total_total += total

            writer.writerow({"start_date": interval, "end_date": interval+delta, "creates": creates, "edits": edits, "deletes": deletes, "total": total})

        writer.writerow({"start_date": intervals[0], "end_date": intervals[-1]+delta, "creates": total_creates, "edits": total_edits, "deletes": total_deletes,"total": total_total})


def generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model, db_utils, interval_length):
    prophet_model_pre_disaster_days = 365*3
    # Generate the actual change counts for the given pre imm post lengths
    count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils, interval_length)
    print(f"count by interval length {interval_length} for {disaster_id}")
    if prophet_model:
        # Generate the counts used to train the prophet models
        count_by_interval_length(disaster_id, disaster_date, prophet_model_pre_disaster_days, 0, 0, db_utils, interval_length)
        # Generate the counts using changes_additional_pre - to have 3 years of training data rather than being restricted to 1

        # Train the prophet models for the given interval length and days
        models, caps = train_forecast_prophet(disaster_id, prophet_model_pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length)
        evaluate_prophet_model_forecasts(models, disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length, disaster_date, caps)


def train_forecast_prophet(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):

    # Load the counts we just saved - in general we will go for pre_disaster_days = 365*3 as we have 3 years of data to train on
    counts = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{0}_{0}_{str(interval_length)}_change_count.csv")
    # Offset the training away from the disaster by a set number of days, to reduce likelihood that changes in run up to disaster skew model

    disaster_day_offset = 60
    pre_disaster_counts = counts.iloc[:(pre_disaster_days - disaster_day_offset)// interval_length]
    pre_disaster_counts_df = pre_disaster_counts.rename(columns={"start_date": "ds"})

    # Covid period exclusion - we don't want variations as a result of covid to affect our training
    # Exclude COVID spike period (March 2020 - June 2020)
    covid_start = '2020-01-01'
    covid_end = '2020-06-30'

    # Filter out major spikes that affect prophet training
    # Dont filter out for California wildfires
    if disaster_id not in [7, 11]:
        pre_disaster_counts_df = pre_disaster_counts_df[
            ~((covid_start <= pre_disaster_counts_df['ds']) & (pre_disaster_counts_df['ds'] <= covid_end))
        ]


    # Create a pd dataframe with the start_date renamed to ds and the total renamed to y
    pre_disaster_counts_creates = pre_disaster_counts_df[["ds", "creates"]].rename(columns={"creates": "y"})
    #pre_disaster_counts_creates["floor"] = 0
    #pre_disaster_counts_creates["cap"] = pre_disaster_counts_creates["y"].quantile(0.9) + 1

    pre_disaster_counts_edits = pre_disaster_counts_df[["ds", "edits"]].rename(columns={"edits": "y"})
    #pre_disaster_counts_edits["floor"] = 0
    #pre_disaster_counts_edits["cap"] = pre_disaster_counts_edits["y"].quantile(0.9) + 1

    pre_disaster_counts_deletes = pre_disaster_counts_df[["ds", "deletes"]].rename(columns={"deletes": "y"})
    #pre_disaster_counts_deletes["floor"] = 0
    #pre_disaster_counts_deletes["cap"] = pre_disaster_counts_deletes["y"].quantile(0.9) + 1


    pre_disaster_counts_total = pre_disaster_counts_df[["ds", "total"]].rename(columns={"total": "y"})
    #pre_disaster_counts_total["floor"] = 0
    #pre_disaster_counts_total["cap"] = pre_disaster_counts_total["y"].quantile(0.9) + 1


    caps = {"creates": pre_disaster_counts_creates["y"].quantile(0.9) + 1 , "edits": pre_disaster_counts_edits["y"].quantile(0.9) + 1, "deletes": pre_disaster_counts_deletes["y"].quantile(0.9) + 1 , "total": pre_disaster_counts_total["y"].quantile(0.9) + 1}


    # Perform the prophet time series analysis
    with suppress_stdout_stderr():

        # Think about the seasonality we want, maybe weekly/monthly?
        model_creates = Prophet()
        model_creates.fit(pre_disaster_counts_creates)
        with open(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_create_prophet_model.json", 'w') as fout:
            fout.write(model_to_json(model_creates)) 

        model_edits= Prophet()
        model_edits.fit(pre_disaster_counts_edits)
        with open(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_create_prophet_model.json", 'w') as fout:
            fout.write(model_to_json(model_edits)) 

        #model_deletes= Prophet(growth="logistic")
        model_deletes= Prophet()
        model_deletes.fit(pre_disaster_counts_deletes)
        with open(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_edit_prophet_model.json", 'w') as fout:
            fout.write(model_to_json(model_deletes)) 

        model_total= Prophet()
        model_total.fit(pre_disaster_counts_total)
        with open(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_total_prophet_model.json", 'w') as fout:
            fout.write(model_to_json(model_total)) 
    
    print("Trained Prophet models")

    return (model_creates, model_edits, model_deletes, model_total), caps

def evaluate_prophet_model_forecasts(models, disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length, disaster_date, caps):
    # Load the actual change counts
    counts_df = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count.csv")
    
    # Drop last row if it's empty
    counts_df = counts_df.dropna(how="all")

    # Ensure start_date is correctly formatted
    counts_df["start_date"] = pd.to_datetime(counts_df["start_date"], errors="coerce")

    # Ensure valid timestamps
    counts_df = counts_df[counts_df["start_date"] >= disaster_date].reset_index(drop=True)

    pre_imm_post_future = counts_df[["start_date"]].dropna().rename(columns={"start_date": "ds"}) 
    pre_imm_post_future = pre_imm_post_future[pre_imm_post_future["ds"] >= disaster_date]
    
    print("Future dates being used for prediction:", pre_imm_post_future)

    # Add floor and cap columns to the future dataframe
    pre_imm_post_future_creates = pre_imm_post_future.copy()
    pre_imm_post_future_creates["cap"] = caps["creates"]

    pre_imm_post_future_edits = pre_imm_post_future.copy()
    pre_imm_post_future_edits["cap"] = caps["edits"]

    pre_imm_post_future_deletes = pre_imm_post_future.copy()
    pre_imm_post_future_deletes["cap"] = caps["deletes"]

    pre_imm_post_future_total = pre_imm_post_future.copy()
    pre_imm_post_future_total["cap"] = caps["total"]

    # Unpack models
    model_creates, model_edits, model_deletes, model_total = models

    # Make forecasts
    model_creates_prediction = model_creates.predict(pre_imm_post_future_creates)
    model_edits_prediction = model_edits.predict(pre_imm_post_future_edits)
    model_deletes_prediction = model_deletes.predict(pre_imm_post_future_deletes)
    model_total_prediction = model_total.predict(pre_imm_post_future_total)

    # Ensure predictions have valid yhat values
    model_edits_prediction["yhat"] = model_edits_prediction["yhat"].clip(lower=0)
    model_creates_prediction["yhat"] = model_creates_prediction["yhat"].clip(lower=0)
    model_deletes_prediction["yhat"] = model_deletes_prediction["yhat"].clip(lower=0)
    model_total_prediction["yhat"] = model_total_prediction["yhat"].clip(lower=0)

    # Save predictions with correct timestamps
    predictions_df = pd.DataFrame({
        "start_date": pre_imm_post_future['ds'],  # Make sure we use actual dates
        "creates": model_creates_prediction["yhat"],
        "edits": model_edits_prediction["yhat"],
        "deletes": model_deletes_prediction["yhat"],
        "total": model_total_prediction["yhat"]
    })
    
    file_path = f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_prophet_predictions.csv"
    predictions_df.to_csv(file_path, index=False)

    # Compute the mean average error and mean average percentage error
    mae = {}
    mape = {}
    for column in ["creates", "edits", "deletes", "total"]:
        mae[column] = np.mean(np.abs(predictions_df[column] - counts_df[column]))
        mape[column] = np.mean(np.abs((predictions_df[column] - counts_df[column]) / counts_df[column].replace(0, 1))) * 100

    mae_row = pd.DataFrame(mae, index=["mae"])
    mape_row = pd.DataFrame(mape, index=["mape"])
    predictions_with_errors_df = pd.concat([mae_row, mape_row], ignore_index=False)

    # Save the DataFrame with MAE and MAPE values
    predictions_with_errors_df.to_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_prophet_predictions_errors.csv", index=False)


def process_disaster(disaster_id, periods, prophet_model_bools):
    db_utils = DB_Utils()
    db_utils.db_connect()

    for prophet_model in prophet_model_bools: # Currently unused
        for period in periods:

            (_, disaster_country, disaster_area, _, disaster_date, _, _ ) = db_utils.get_disaster_with_id(disaster_id)

            # For each disaster, count the aggregate count in each time period - pre, imm, post, and as before count the number of changes in each period
            # File system, generate 1 folder for each disaster, and output the aggregate total in each period for each type, as well as pretty much the same file we had before
            print(f"{disaster_id} {disaster_area[0]} {disaster_date}")
            # First lets do the total counts for each period

            print(period)
            pre_disaster_days = period[0]
            imm_disaster_days = period[1]
            post_disaster_days = period[2]

            #count_full_periods(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, db_utils)
            generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model, db_utils, interval_length=1)
            generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model, db_utils, interval_length=7)
            generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model, db_utils, interval_length=30)


if __name__ == "__main__":

    # Define the period lengths
    periods = [(365, 30, 365), (180, 30, 365), (365, 60, 335), ]
    periods = [(1095, 30, 365),  (365, 60, 335), (1095, 60, 365),(180,60,365),]
    #periods = [(365,60,365),(1095, 30, 365)]
    periods = [(1095, 60, 365), (365,60,365)]
    prophet_model_bools = [True, False]
    post_only_bools = [True, False]

    process_disasters = False

    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]
        print("Disaster IDs defined:", disaster_ids)

    if process_disasters:
        # Use ProcessPoolExecutor to parallelize the disaster_id loop
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Submit tasks for each disaster_id
            futures = {
                executor.submit(
                    process_disaster, 
                    disaster_id, 
                    periods, 
                    prophet_model_bools, 
                ): (disaster_id, period) for period in periods for disaster_id in disaster_ids 
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                disaster_id, period = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    print(f"Error processing disaster_id {disaster_id}: {e}")

    
    compute_total_number_changes_across_disasters(periods, disaster_ids=[3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17])

