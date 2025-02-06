import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils



def plot_percent_difference(disaster_id, disaster_country, disaster_area, disaster_date, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric):
    print(f"Ploting {pre_disaster_days} {post_disaster_days}")
    # Load datasets
    try:
        data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_1_percent_difference_time_series_{average_metric}.csv')[:-1]
        data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_7_percent_difference_time_series_{average_metric}.csv')[:-1]
        data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_30_percent_difference_time_series_{average_metric}.csv')[:-1]
    except FileNotFoundError:
        print("Using default")
        data_day = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_1_percent_difference_time_series_{average_metric}.csv')[:-1]
        data_week = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_7_percent_difference_time_series_{average_metric}.csv')[:-1]
        data_month = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_30_percent_difference_time_series_{average_metric}.csv')[:-1]

    # Ensure `start_date` is parsed as datetime
    data_day['start_date'] = pd.to_datetime(data_day['start_date'])
    data_week['start_date'] = pd.to_datetime(data_week['start_date'])
    data_month['start_date'] = pd.to_datetime(data_month['start_date'])

    if post_only:
        print("Post only")
        before = disaster_date + timedelta(days=imm_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)
    else:
        before = disaster_date - timedelta(days=pre_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    data_day = data_day[(before < data_day['start_date']) & (data_day['start_date'] < after)]
    data_week = data_week[(before < data_week['start_date']) & (data_week['start_date'] < after)]
    data_month = data_month[(before < data_month['start_date']) & (data_month['start_date'] < after)]


    # Create subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 18), sharex=True)

    # Plot data for 'day'
    axes[0].plot(data_day['start_date'], data_day['creates'], label='Creates', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['edits'], label='Edits', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[0].plot(data_day['start_date'], data_day['total'], label='Total', marker='.', linestyle='-')
    axes[0].set_title(f'% Difference in changes daily, compared to mean pre-disaster in {disaster_country}, {disaster_area} {"Post only" if post_only else ""}')
    axes[0].set_ylabel('% Difference')
    axes[0].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[0].legend()
    axes[0].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[0].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[0].minorticks_on()

    # Plot data for 'week'
    axes[1].plot(data_week['start_date'], data_week['creates'], label='Creates', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['edits'], label='Edits', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[1].plot(data_week['start_date'], data_week['total'], label='Total', marker='.', linestyle='-')
    axes[1].set_title(f'Difference in changes Weekly, compared to mean pre-disaster in {disaster_country}, {disaster_area} {"Post only" if post_only else ""}')
    axes[1].set_ylabel('% Difference')
    axes[1].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[1].legend()
    axes[1].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[1].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[1].minorticks_on()

    # Plot data for 'month'
    axes[2].plot(data_month['start_date'], data_month['creates'], label='Creates', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['edits'], label='Edits', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['deletes'], label='Deletes', marker='.', linestyle='-')
    axes[2].plot(data_month['start_date'], data_month['total'], label='Total', marker='.', linestyle='-')
    axes[2].set_title(f'Difference in changes Monthly, compared to mean pre-disaster in {disaster_country}, {disaster_area} {"Post only" if post_only else ""}')
    axes[2].set_xlabel('Date')
    axes[2].set_ylabel('% Difference')
    axes[2].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[2].legend()
    axes[2].grid(which='major', color='black', linestyle='-', linewidth=0.5)
    axes[2].grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    axes[2].minorticks_on()

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

    save_path = f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_percent_difference_time_series{"_post_only" if post_only else ""}.png'
    print(save_path)
    plt.savefig(save_path, dpi=350)

    plt.close()

def plot_percent_difference_single(disaster_id, disaster_country, disaster_area, disaster_date, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, time_period, average_metric, plot_edit_types):
    print(f"Plotting {time_period} data for {pre_disaster_days}, {post_disaster_days}")

    # Load datasets
    try:
        data_day = pd.read_csv(
            f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_1_percent_difference_time_series_{average_metric}.csv')[:-1]
        data_week = pd.read_csv(
            f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_7_percent_difference_time_series_{average_metric}.csv')[:-1]
        data_month = pd.read_csv(
            f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_30_percent_difference_time_series_{average_metric}.csv')[:-1]
    except FileNotFoundError:
        print("Using default")
        data_day = pd.read_csv(
            f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_1_percent_difference_time_series.csv')[:-1]
        data_week = pd.read_csv(
            f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_7_percent_difference_time_series.csv')[:-1]
        data_month = pd.read_csv(
            f'./Results/ChangeCounting/disaster{disaster_id}/data/365_30_365_30_percent_difference_time_series.csv')[:-1]

    # Ensure `start_date` is parsed as datetime
    data_day['start_date'] = pd.to_datetime(data_day['start_date'])
    data_week['start_date'] = pd.to_datetime(data_week['start_date'])
    data_month['start_date'] = pd.to_datetime(data_month['start_date'])

    # Filter data
    if post_only:
        before = disaster_date + timedelta(days=imm_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days + post_disaster_days) + timedelta(days=1)
    else:
        before = disaster_date - timedelta(days=pre_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days + post_disaster_days) + timedelta(days=1)

    data_day = data_day[(data_day['start_date'] > before) & (data_day['start_date'] < after)]
    data_week = data_week[(data_week['start_date'] > before) & (data_week['start_date'] < after)]
    data_month = data_month[(data_month['start_date'] > before) & (data_month['start_date'] < after)]

    # Select dataset based on time_period
    if time_period == "day":
        data = data_day
        title = "Daily Changes"
    elif time_period == "week":
        data = data_week
        title = "Weekly Changes"
    elif time_period == "month":
        data = data_month
        title = "Monthly Changes"
    else:
        raise ValueError("Invalid time_period. Must be 'day', 'week', or 'month'.")

    # Plot data
    plt.figure(figsize=(12, 6))
    if "creates" in plot_edit_types:
        plt.plot(data['start_date'], data['creates'], label='Creates', marker='.', linestyle='-', color='blue',)
    if "edits" in plot_edit_types:
        plt.plot(data['start_date'], data['edits'], label='Edits', marker='.', linestyle='-', color='orange',)
    if "deletes" in plot_edit_types:
        plt.plot(data['start_date'], data['deletes'], label='Deletes', marker='.', linestyle='-', color='green',)
    if "total" in plot_edit_types:
        plt.plot(data['start_date'], data['total'], label='Total', marker='.', linestyle='-', color='red',)

    plt.title(f'{title} Percent Difference in {disaster_country}, {disaster_area} {"(Post only)" if post_only else ""}')
    plt.xlabel('Date')
    plt.ylabel('% Difference')
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

    save_path = f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{time_period}_percent_difference_time_series{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png'
    print(save_path)
    plt.savefig(save_path, dpi=350)

       # Save the charts
    if not os.path.exists(f"visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts"):
        os.makedirs(f"visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts")
    
    save_path = f'visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{time_period}_percent_difference_time_series{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png'
    plt.savefig(save_path, dpi=350)
    plt.close()



if __name__ == "__main__":
    db_utils = DB_Utils()
    connection = db_utils.db_connect()
    # We do post only so that we have a nice chart in the post that excludes the huge peak
    post_only = True

    # Define periods as an array of tuples
    periods = [ (365, 60, 365), (1095,60,365)]
    #periods = [(365, 30, 365)]
    average_metric = "median" # mean or median
    plot_edit_types_list = [["creates", "edits", "deletes", "total"],["creates"],["edits"],["deletes"],["total"]]

    # Loop through disasters and periods
    for post_only in [True, False]:
        for disaster_id in range(11,13):
            _, disaster_country, disaster_area, _, disaster_date, _ = db_utils.get_disaster_with_id(disaster_id)
            print(f"Processing Disaster {disaster_id} - {disaster_area[0]}")
            for plot_edit_types in plot_edit_types_list:
                for period in periods:
                    pre_disaster_days, imm_disaster_days, post_disaster_days = period

                    plot_percent_difference(disaster_id, disaster_country[0], disaster_area[0], disaster_date, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, average_metric)
                    plot_percent_difference_single(disaster_id, disaster_country[0], disaster_area[0], disaster_date, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, "day", average_metric, plot_edit_types)
                    plot_percent_difference_single(disaster_id, disaster_country[0], disaster_area[0], disaster_date, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, "week", average_metric, plot_edit_types)
                    plot_percent_difference_single(disaster_id, disaster_country[0], disaster_area[0], disaster_date, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, "month", average_metric, plot_edit_types)
