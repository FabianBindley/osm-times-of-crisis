import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_utils import DB_Utils

def get_disaster_with_id(disaster_id, connection):
    disaster = db_utils.get_disaster_with_id(disaster_id)

    return disaster[1][0], disaster[2][0], disaster[4]

def plot_counts(disaster_id, disaster_country, disaster_area, disaster_date, before_after_time_length):
    # Load datasets
    data_day = pd.read_csv(f'./Results/ChangeCounting/data/change_count_{disaster_id}_day.csv')[:-1]
    data_week = pd.read_csv(f'./Results/ChangeCounting/data/change_count_{disaster_id}_week.csv')[:-1]
    data_month = pd.read_csv(f'./Results/ChangeCounting/data/change_count_{disaster_id}_month.csv')[:-1]



    # Ensure `start_date` is parsed as datetime
    data_day['start_date'] = pd.to_datetime(data_day['start_date'])
    data_week['start_date'] = pd.to_datetime(data_week['start_date'])
    data_month['start_date'] = pd.to_datetime(data_month['start_date'])

    after = disaster_date - timedelta(days=before_after_time_length)
    before = disaster_date + timedelta(days=before_after_time_length)

    data_day = data_day[(data_day['start_date'] > after) & (data_day['start_date'] < before)]
    data_week = data_week[(data_week['start_date'] > after) & (data_week['start_date'] < before)]
    data_month = data_month[(data_month['start_date'] > after) & (data_month['start_date'] < before)]

    # Create subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 18), sharex=False)

    # Plot data for 'day'
    axes[0].plot(data_day['start_date'], data_day['creates'], label='Creates', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['edits'], label='Edits', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['total'], label='Total', marker='.', linestyle='-')
    axes[0].set_title(f'Daily Changes in {disaster_country}, {disaster_area}')
    axes[0].set_ylabel('Count')
    axes[0].legend()
    axes[0].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[0].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[0].minorticks_on()

    # Plot data for 'week'
    axes[1].plot(data_week['start_date'], data_week['creates'], label='Creates', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['edits'], label='Edits', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['total'], label='Total', marker='.', linestyle='-')
    axes[1].set_title(f'Weekly Changes in {disaster_country}, {disaster_area}')
    axes[1].set_ylabel('Count')
    axes[1].legend()
    axes[1].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[1].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[1].minorticks_on()

    # Plot data for 'month'
    axes[2].plot(data_month['start_date'], data_month['creates'], label='Creates', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['edits'], label='Edits', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['total'], label='Total', marker='.', linestyle='-')
    axes[2].set_title(f'Monthly Changes in {disaster_country}, {disaster_area}')
    axes[2].set_xlabel('Date')
    axes[2].set_ylabel('Count')
    axes[2].legend()
    axes[2].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[2].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[2].minorticks_on()

    # Format x-axis with rotated datetime labels
    
    for ax in axes:
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Set monthly ticks, for weekly use WeekdayLocator()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format as YYYY-MM
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig(f'./Results/ChangeCounting/charts/{disaster_country}_{disaster_area}_{disaster_date.year}_{before_after_time_length}_day_counts.png', dpi=300)

    

if __name__ == "__main__":
    db_utils = DB_Utils()
    connection = db_utils.db_connect()

    for disaster_id in range(1,7):
        if disaster_id == 3:
            continue
        disaster_country, disaster_area, disaster_date = get_disaster_with_id(disaster_id, connection)
        plot_counts(disaster_id, disaster_country, disaster_area, disaster_date, before_after_time_length=365)
        plot_counts(disaster_id, disaster_country, disaster_area, disaster_date, before_after_time_length=90)