import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils



def plot_counts(disaster_id, disaster_country, disaster_area, disaster_date, prophet_model, pre_disaster_days, imm_disaster_days, post_disaster_days):
    print(f"Ploting {pre_disaster_days} {post_disaster_days}")
    # Load datasets
    try:
        data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_1_change_count.csv')[:-1]
        data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_7_change_count.csv')[:-1]
        data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_30_change_count.csv')[:-1]
    except FileNotFoundError:
        data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_1_change_count.csv')[:-1]
        data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_7_change_count.csv')[:-1]
        data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_30_change_count.csv')[:-1]

    # Ensure `start_date` is parsed as datetime
    data_day['start_date'] = pd.to_datetime(data_day['start_date'])
    data_week['start_date'] = pd.to_datetime(data_week['start_date'])
    data_month['start_date'] = pd.to_datetime(data_month['start_date'])


    before = disaster_date - timedelta(days=pre_disaster_days)
    after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    data_day = data_day[(before < data_day['start_date']) & (data_day['start_date'] < after)]
    data_week = data_week[(before < data_week['start_date']) & (data_week['start_date'] < after)]
    data_month = data_month[(before < data_month['start_date']) & (data_month['start_date'] < after)]

    # retrieve the prophet models


    # Create subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

    # Plot data for 'day'
    axes[0].plot(data_day['start_date'], data_day['creates'], label='Creates', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['edits'], label='Edits', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['total'], label='Total', marker='.', linestyle='-')
    axes[0].set_title(f'Daily Changes in {disaster_country}, {disaster_area}')
    axes[0].set_ylabel('Count')
    axes[0].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[0].legend()
    axes[0].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[0].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[0].minorticks_on()

    # plot the day prophet model

    # Plot data for 'week'
    axes[1].plot(data_week['start_date'], data_week['creates'], label='Creates', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['edits'], label='Edits', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['total'], label='Total', marker='.', linestyle='-')
    axes[1].set_title(f'Weekly Changes in {disaster_country}, {disaster_area}')
    axes[1].set_ylabel('Count')
    axes[1].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[1].legend()
    axes[1].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[1].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[1].minorticks_on()

    # plot the week prophet model

    # Plot data for 'month'
    axes[2].plot(data_month['start_date'], data_month['creates'], label='Creates', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['edits'], label='Edits', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['total'], label='Total', marker='.', linestyle='-')
    axes[2].set_title(f'Monthly Changes in {disaster_country}, {disaster_area}')
    axes[2].set_xlabel('Date')
    axes[2].set_ylabel('Count')
    axes[2].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[2].legend()
    axes[2].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[2].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[2].minorticks_on()

    # plot the month prophet model

    # Format x-axis with rotated datetime labels
    for ax in axes:
        ax.tick_params(labelbottom=True)  # Ensure all subplots display x-axis labels
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Set monthly ticks
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format as YYYY-MM
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    if not os.path.exists(f"Results/ChangeCounting/disaster{disaster_id}/charts"):
        os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/charts")

    plt.savefig(f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_counts.png', dpi=350)

    plt.close()


def plot_counts_specific(disaster_id, disaster_country, disaster_area, disaster_date, prophet_model, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):
    time_period = "day" if interval_length == 1 else "week" if interval_length == 7 else "month"
    print(f"Plotting {time_period} data for {pre_disaster_days}, {post_disaster_days}")

    # Load datasets
    try:
        data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_1_change_count.csv').iloc[:-1]
        data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_7_change_count.csv').iloc[:-1]
        data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_30_change_count.csv').iloc[:-1]


    except FileNotFoundError:
        print("Using default")
        data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_1_change_count.csv').iloc[:-1]
        data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_7_change_count.csv').iloc[:-1]
        data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_30_change_count.csv').iloc[:-1]


    # Ensure `start_date` is parsed as datetime
    data_day['start_date'] = pd.to_datetime(data_day['start_date'])
    data_week['start_date'] = pd.to_datetime(data_week['start_date'])
    data_month['start_date'] = pd.to_datetime(data_month['start_date'])

    before = disaster_date - timedelta(days=pre_disaster_days) - timedelta(seconds=1)
    after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    # Filter datasets
    data_day = data_day[(before < data_day['start_date']) & (data_day['start_date'] < after)]
    data_week = data_week[(before < data_week['start_date']) & (data_week['start_date'] < after)]
    data_month = data_month[(before < data_month['start_date']) & (data_month['start_date'] < after)]

    # Load the appropriate prophet predictions
    
    try:
        file_path = f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_prophet_predictions.csv'
        predictions = pd.read_csv(file_path)
    except FileNotFoundError:
        raise(Exception(f"Prophet predictions not found for {pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}"))



    # Select data based on time_period
    if interval_length == 1:
        data = data_day
        title = "Daily Changes"
    elif interval_length == 7:
        data = data_week
        title = "Weekly Changes"
    elif interval_length == 30:
        data = data_month
        title = "Monthly Changes"
    else:
        raise ValueError("Invalid time_period. Choose from 'day', 'week', or 'month'.")

    # Plot data
    plt.figure(figsize=(12, 6))
    plt.plot(data['start_date'], data['creates'], label='Creates', marker='.', linestyle='-', color='blue')
    plt.plot(data['start_date'], data['edits'], label='Edits', marker='.', linestyle='-', color='orange')
    plt.plot(data['start_date'], data['deletes'], label='Deletes', marker='.', linestyle='-', color='green')
    plt.plot(data['start_date'], data['total'], label='Total', marker='.', linestyle='-', color='red')

    if prophet_model:
        # Plot prediction data
        plt.plot(data['start_date'], predictions['creates'], label='Creates prediction', linestyle='--', color='blue')
        plt.plot(data['start_date'], predictions['edits'], label='Edits prediction', linestyle='--', color='orange')
        plt.plot(data['start_date'], predictions['deletes'], label='Deletes prediction', linestyle='--', color='green')
        plt.plot(data['start_date'], predictions['total'], label='Total prediction',  linestyle='--', color='red')
    
    plt.title(f'{title} in {disaster_country}, {disaster_area}')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    plt.legend()
    plt.grid(which='major', color='black', linestyle='-', linewidth=0.5)
    plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    plt.minorticks_on()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    # Save the figure
    if not os.path.exists(f"Results/ChangeCounting/disaster{disaster_id}/charts"):
        os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/charts")

    file_path = f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}.png'
    plt.savefig(file_path, dpi=350)
    print("saved: ",file_path)

    # Save the charts
    if not os.path.exists(f"visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts"):
        os.makedirs(f"visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts")
    
    plt.savefig(f'visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_{time_period}_count_changes{"_prophet_forecast" if prophet_model else ""}.png', dpi=350)
    plt.close()




if __name__ == "__main__":
    db_utils = DB_Utils()
    connection = db_utils.db_connect()
    periods = [(365,30,365), (180,30,365)]
    periods = [(365,30,365),]
    periods = [(1095, 30, 365)]
    prophet_model_bools = [True, False]

    for disaster_id in range(1,7):
        for prophet_model in prophet_model_bools:
            _, disaster_country, disaster_area, _, disaster_date, _  = db_utils.get_disaster_with_id(disaster_id)

            for period in periods:
                print(f"{disaster_id} {disaster_area[0]} {disaster_date}")
                plot_counts(disaster_id, disaster_country[0], disaster_area[0],  disaster_date, prophet_model,  pre_disaster_days=period[0], imm_disaster_days=period[1], post_disaster_days=period[2])
                plot_counts_specific(disaster_id, disaster_country[0], disaster_area[0],  disaster_date, prophet_model, pre_disaster_days=period[0], imm_disaster_days=period[1], post_disaster_days=period[2], interval_length=1)
                plot_counts_specific(disaster_id, disaster_country[0], disaster_area[0], disaster_date, prophet_model, pre_disaster_days=period[0], imm_disaster_days=period[1], post_disaster_days=period[2], interval_length=7)
                plot_counts_specific(disaster_id, disaster_country[0], disaster_area[0], disaster_date, prophet_model, pre_disaster_days=period[0], imm_disaster_days=period[1], post_disaster_days=period[2], interval_length=30)


