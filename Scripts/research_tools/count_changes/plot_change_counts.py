import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils



def plot_counts(disaster_id, disaster_country, disaster_area, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days):
    print(f"Ploting {pre_disaster_days} {post_disaster_days}")
    # Load datasets
    data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/1_change_count.csv')[:-1]
    data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/7_change_count.csv')[:-1]
    data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/30_change_count.csv')[:-1]

    # Ensure `start_date` is parsed as datetime
    data_day['start_date'] = pd.to_datetime(data_day['start_date'])
    data_week['start_date'] = pd.to_datetime(data_week['start_date'])
    data_month['start_date'] = pd.to_datetime(data_month['start_date'])


    before = disaster_date - timedelta(days=pre_disaster_days)
    after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    data_day = data_day[(before < data_day['start_date']) & (data_day['start_date'] < after)]
    data_week = data_week[(before < data_week['start_date']) & (data_week['start_date'] < after)]
    data_month = data_month[(before < data_month['start_date']) & (data_month['start_date'] < after)]


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
    if not os.path.exists(f"Results/ChangeCounting/disaster{disaster_id}/charts"):
        os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/charts")

    plt.savefig(f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_counts.png', dpi=350)

    plt.close()


if __name__ == "__main__":
    db_utils = DB_Utils()
    connection = db_utils.db_connect()

    for disaster_id in range(1,7):
        _, disaster_country, disaster_area, _, disaster_date, _  = db_utils.get_disaster_with_id(disaster_id)
        print(f"{disaster_id} {disaster_area[0]} {disaster_date}")
        plot_counts(disaster_id, disaster_country[0], disaster_area[0], disaster_date, pre_disaster_days=365, imm_disaster_days=28, post_disaster_days=365)
        plot_counts(disaster_id, disaster_country[0], disaster_area[0], disaster_date, pre_disaster_days=180, imm_disaster_days=28, post_disaster_days=365)
        plot_counts(disaster_id, disaster_country[0], disaster_area[0], disaster_date, pre_disaster_days=90, imm_disaster_days=28, post_disaster_days=365)
        plot_counts(disaster_id, disaster_country[0], disaster_area[0], disaster_date, pre_disaster_days=90, imm_disaster_days=28, post_disaster_days=180)