import sys
import os
from contextlib import contextmanager
import numpy as np
from datetime import datetime, timedelta
import csv 
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils


def compute_total_number_changes_across_disasters(periods, disaster_ids):
    
    # Load the counts from the full periods file for each disaster, and compoute an aggregate total for pre, imm, post across all disasters
    # Create a df with header headers = ["creates", "edits", "deletes", "total"]
    headers_total_counts = ["creates", "edits", "deletes", "total"]

    for period in periods:
        total_counts = pd.DataFrame(columns=headers_total_counts, data=np.zeros((4, 4)))
        pre_disaster_days ,imm_disaster_days, post_disaster_days = period
        for disaster_id in disaster_ids:
            file_path = f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv"
            counts = pd.read_csv(file_path)
            for i in range(4):
                total_counts.iloc[i] += counts.iloc[i]

        total_counts.to_csv(f"./Results/ChangeCounting/summary/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv", index=False)
    

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

def count_full_periods(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    pre_disaster_start_date = disaster_date - pre_disaster

    imm_disaster_start_date = disaster_date

    post_disaster_start_date = disaster_date + imm_disaster
    post_disaster_end_date = post_disaster_start_date + post_disaster + timedelta(days=1)

    intervals = [pre_disaster_start_date, imm_disaster_start_date, post_disaster_start_date, post_disaster_end_date]

    if pre_disaster_days > 370:
        counts = db_utils.count_changes_in_interval_3_years_pre(disaster_id, intervals)
    else:
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

def count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):
    pre_disaster = timedelta(pre_disaster_days)
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

    if pre_disaster_days > 370:
        counts = db_utils.count_changes_in_interval_3_years_pre(disaster_id, intervals)
    else:
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


def generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model, interval_length):
    prophet_model_pre_disaster_days = 365*3
    # Generate the actual change counts for the given pre imm post lengths
    count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length)
    print(f"count by interval length for {disaster_id}")
    if prophet_model:
        # Generate the counts used to train the prophet models
        count_by_interval_length(disaster_id, disaster_date, prophet_model_pre_disaster_days, 0, 0, interval_length)
        # Generate the counts using changes_additional_pre - to have 3 years of training data rather than being restricted to 1

        # Train the prophet models for the given interval length and days
        models, caps = train_forecast_prophet(disaster_id, prophet_model_pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length)
        evaluate_prophet_model_forecasts(models, disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length, caps)


def train_forecast_prophet(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):

    # Load the counts we just saved - in general we will go for pre_disaster_days = 365*3 as we have 3 years of data to train on
    counts = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{0}_{0}_{str(interval_length)}_change_count.csv")
    # Offset the training away from the disaster by a set number of days, to reduce likelihood that changes in run up to disaster skew model

    disaster_day_offset = 58
    pre_disaster_counts = counts.iloc[:(pre_disaster_days - disaster_day_offset)// interval_length]
    pre_disaster_counts_df = pre_disaster_counts.rename(columns={"start_date": "ds"})

    # Covid period exclusion - we don't want variations as a result of covid to affect our training
    # Exclude COVID spike period (March 2020 - June 2020)
    covid_start = '2020-01-01'
    covid_end = '2020-06-30'

    # Filter out major spikes that affect prophet training
    pre_disaster_counts_df = pre_disaster_counts_df[
        ~((covid_start <= pre_disaster_counts_df['ds']) & (pre_disaster_counts_df['ds'] <= covid_end))
    ]

    # Exclude shocks
    if disaster_id == 4:   
        pre_disaster_counts_df = pre_disaster_counts_df[
            ~(('2019-05-01' <= pre_disaster_counts_df['ds']) & (pre_disaster_counts_df['ds'] <= '2019-07-01'))
        ]

    if disaster_id == 5:   
        pre_disaster_counts_df = pre_disaster_counts_df[
            ~(('2019-01-01' <= pre_disaster_counts_df['ds']) & (pre_disaster_counts_df['ds'] <= '2019-05-01'))
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

def evaluate_prophet_model_forecasts(models,  disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length, caps):

    counts_df = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count.csv")[:-1]
    pre_imm_post_start_dates = counts_df["start_date"]
    pre_imm_post_future = pd.DataFrame({"ds": pre_imm_post_start_dates})

    # Add floor and cap columns to the future dataframe
    pre_imm_post_future_creates = pre_imm_post_future.copy()
    #pre_imm_post_future_creates["floor"] = 0  
    #pre_imm_post_future_creates["cap"] = caps["creates"]

    pre_imm_post_future_edits = pre_imm_post_future.copy()
    #pre_imm_post_future_edits["floor"] = 0  
    #pre_imm_post_future_edits["cap"] = caps["edits"]

    pre_imm_post_future_deletes = pre_imm_post_future.copy()
    #pre_imm_post_future_deletes["floor"] = 0  
    #pre_imm_post_future_deletes["cap"] = caps["deletes"]  

    pre_imm_post_future_total = pre_imm_post_future.copy()
    #pre_imm_post_future_total["floor"] = 0  
    #pre_imm_post_future_total["cap"] = caps["total"]

    model_creates, model_edits, model_deletes, model_total = models



    model_creates_prediction = model_creates.predict(pre_imm_post_future_creates)
    model_edits_prediction = model_edits.predict(pre_imm_post_future_edits)
    model_deletes_prediction = model_deletes.predict(pre_imm_post_future_deletes)
    model_total_prediction = model_total.predict(pre_imm_post_future_total)

    model_edits_prediction["yhat"] = model_edits_prediction["yhat"].clip(lower=0)
    model_creates_prediction["yhat"] = model_creates_prediction["yhat"].clip(lower=0)
    model_deletes_prediction["yhat"] = model_deletes_prediction["yhat"].clip(lower=0)
    model_total_prediction["yhat"] = model_total_prediction["yhat"].clip(lower=0)
    #print(model_deletes_prediction["yhat"])


    predictions_df = pd.DataFrame({"start_date":pre_imm_post_future['ds'],"creates": model_creates_prediction["yhat"], "edits": model_edits_prediction["yhat"], "deletes": model_deletes_prediction["yhat"], "total": model_total_prediction["yhat"]})
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
    print(predictions_with_errors_df)

    # Save the DataFrame with MAE and MAPE values
    predictions_with_errors_df.to_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_prophet_predictions_errors.csv", index=False)

if __name__ == "__main__":

    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define the period lengths
    periods = [(365, 30, 365), (180, 30, 365), (365, 60, 335), ]
    periods = [(1095, 30, 365),  (365, 60, 335), ]
    #periods = [(1095, 30, 365)]
    periods = [(180, 30, 365), (1095, 30, 365),(365, 30, 365),(365, 60, 335)]
    prophet_model_bools = [True, False]

    
    
    for disaster_id in [2,3,4,5,6]:
        for prophet_model in prophet_model_bools: # Currently unused
            for period in periods:

                if disaster_id in []:
                    continue

                (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
                # For each disaster, count the aggregate count in each time period - pre, imm, post, and as before count the number of changes in each period
                # File system, generate 1 folder for each disaster, and output the aggregate total in each period for each type, as well as pretty much the same file we had before
                print(f"{disaster_id} {disaster_area[0]} {disaster_date}")
                # First lets do the total counts for each period

                pre_disaster_days = period[0]
                imm_disaster_days = period[1]
                post_disaster_days = period[2]

                count_full_periods(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days)
                generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model, interval_length=1)
                generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days,  prophet_model, interval_length=7)
                generate_count_by_interval_length(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, prophet_model, interval_length=30)
    
    
    compute_total_number_changes_across_disasters(periods, disaster_ids=range(2,7))
