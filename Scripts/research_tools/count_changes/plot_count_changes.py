import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import ast
import shutil
import numpy as np
import concurrent.futures
import math
from itertools import product

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils



def plot_counts(disaster_id, disaster_country, disaster_area, disaster_date, prophet_model, plot_edit_types, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days):
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



    if post_only:
        before = disaster_date + timedelta(days=imm_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)
    else:
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
    axes[0].set_title(f'Daily Changes in {disaster_area}, {disaster_country} | {disaster_date.year}')
    axes[0].set_ylabel('Count')
    axes[0].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[0].axvline(x=disaster_date+timedelta(imm_disaster_days), color='firebrick', linestyle='--', linewidth=1, label='Post Disaster Period Start')
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
    axes[1].set_title(f'Weekly Changes in {disaster_area}, {disaster_country} | {disaster_date.year}')
    axes[1].set_ylabel('Count')
    axes[1].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[1].axvline(x=disaster_date+timedelta(imm_disaster_days), color='firebrick', linestyle='--', linewidth=1, label='Post Disaster Period Start')
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
    axes[2].set_title(f'Monthly Changes in {disaster_area}, {disaster_country} | {disaster_date.year}')
    axes[2].set_xlabel('Date')
    axes[2].set_ylabel('Count')
    axes[2].axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    axes[2].axvline(x=disaster_date+timedelta(imm_disaster_days), color='firebrick', linestyle='--', linewidth=1, label='Post Disaster Period Start')
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
    os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/charts", exist_ok=True)

    plt.savefig(f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_counts{"_post_only" if post_only else ""}.png', dpi=350)

    plt.close()


def plot_counts_specific(disaster_id, disaster_country, disaster_area, disaster_date, prophet_model, plot_edit_types, post_only, pre_disaster_days, imm_disaster_days, post_disaster_days, interval_length):
    time_period = "day" if interval_length == 1 else "week" if interval_length == 7 else "month"
    print(f"Plotting {time_period} data for {pre_disaster_days}, {post_disaster_days}")
    print(f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{post_disaster_days}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png')

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

    if post_only:
        #before = disaster_date + timedelta(days=imm_disaster_days)
        before = disaster_date
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)
    else:
        before = disaster_date - timedelta(days=pre_disaster_days)
        after = disaster_date + timedelta(days=imm_disaster_days) + timedelta(days=post_disaster_days) + timedelta(days=1)

    # Filter datasets
    data_day = data_day[(before < data_day['start_date']) & (data_day['start_date'] < after)]
    data_week = data_week[(before < data_week['start_date']) & (data_week['start_date'] < after)]
    data_month = data_month[(before < data_month['start_date']) & (data_month['start_date'] < after)]


    # Load the appropriate prophet predictions
    if prophet_model:
        try:
            file_path = f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_prophet_predictions.csv'
            predictions = pd.read_csv(file_path)
            errors = pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}_change_count_prophet_predictions_errors.csv')
        except FileNotFoundError:
            raise(Exception(f"Prophet predictions not found for {pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{str(interval_length)}"))

        """
        if post_only:
            before_prophet = disaster_date + timedelta(days=imm_disaster_days)
        else:
            before_prophet = disaster_date
            """
        before_prophet = disaster_date
        predictions['start_date'] = pd.to_datetime(predictions['start_date'])
        predictions = predictions[(before_prophet < pd.to_datetime(predictions['start_date'])) & (pd.to_datetime(predictions['start_date']) < after)]

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
    plt.figure(figsize=(12, 7))

    if "creates" in plot_edit_types:
        plt.plot(data['start_date'], data['creates'], label='Creates', marker='.', linestyle='-', color='blue')
    if "edits" in plot_edit_types:
        plt.plot(data['start_date'], data['edits'], label='Edits', marker='.', linestyle='-', color='orange')
    if "deletes" in plot_edit_types:
        plt.plot(data['start_date'], data['deletes'], label='Deletes', marker='.', linestyle='-', color='green')
    if "total" in plot_edit_types:
        plt.plot(data['start_date'], data['total'], label='Total', marker='.', linestyle='-', color='red')

    
    if prophet_model:

        if "creates" in plot_edit_types:
            mae_creates = int(errors.iloc[0]["creates"]) if not np.isinf(errors.iloc[0]["creates"]) else "N/A"
            mape_creates = round(errors.iloc[1]["creates"],1) if not np.isinf(errors.iloc[1]["creates"]) else "N/A"
            plt.plot(predictions['start_date'], predictions['creates'], label=f'Creates Prediction (MAE: {mae_creates}, MAPE: {mape_creates}%)', linestyle='--', color='blue',)
        if "edits" in plot_edit_types:
            mae_edits = int(errors.iloc[0]["edits"]) if not np.isinf(errors.iloc[0]["edits"]) else "N/A"
            mape_edits = round(errors.iloc[1]["edits"],1) if not np.isinf(errors.iloc[1]["edits"]) else "N/A"
            plt.plot(predictions['start_date'], predictions['edits'], label=f'Edits Prediction (MAE: {mae_edits}, MAPE: {mape_edits}%)', linestyle='--', color='orange', )
        if "deletes" in plot_edit_types:
            mae_deletes = int(errors.iloc[0]["deletes"]) if not np.isinf(errors.iloc[0]["deletes"]) else "N/A"
            mape_deletes = round(errors.iloc[1]["deletes"],1) if not np.isinf(errors.iloc[1]["deletes"]) else "N/A"
            plt.plot(predictions['start_date'], predictions['deletes'], label=f'Deletes Prediction (MAE: {mae_deletes}, MAPE: {mape_deletes}%)', linestyle='--', color='green', )

        if "total" in plot_edit_types:
            mae_total = int(errors.iloc[0]["total"]) if not np.isinf(errors.iloc[0]["total"]) else "N/A"
            mape_total = round(errors.iloc[1]["total"],1) if not np.isinf(errors.iloc[1]["total"]) else "N/A"
            plt.plot(predictions['start_date'], predictions['total'], label=f'Total Prediction (MAE: {mae_total}, MAPE: {mape_total}%)', linestyle='--', color='red',)

    
    plt.title(f'{title} in {disaster_area}, {disaster_country} | {disaster_date.year}')
    plt.xlabel('Date')
    plt.ylabel('Count')

    plt.axvline(x=disaster_date, color='purple', linestyle='--', linewidth=1, label='Disaster Date')
    plt.axvline(x=disaster_date+timedelta(imm_disaster_days), color='firebrick', linestyle='--', linewidth=1, label='Post Disaster Period Start')

    plt.legend()
    plt.grid(which='major', color='black', linestyle='-', linewidth=0.5)
    plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    plt.minorticks_on()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=90 if pre_disaster_days > 365 else 45)

    if post_only:
        post_disaster_data = data[data['start_date'] >= disaster_date + timedelta(days=imm_disaster_days)]

        # Collect max values only for the plotted types
        max_post_values = [
            post_disaster_data[edit_type].max()
            for edit_type in plot_edit_types 
        ]

        if prophet_model:
            post_disaster_predictions = predictions[predictions['start_date'] >= disaster_date + timedelta(days=imm_disaster_days)]
            max_pred_values = [
                post_disaster_predictions[edit_type].max()
                for edit_type in plot_edit_types if edit_type in post_disaster_predictions.columns
            ]
            max_post_values.extend(max_pred_values)  # Merge both actual & predicted max values
    

        # Ensure we have valid data to scale
        if max_post_values and not all(np.isnan(max_post_values)):  
            y_max = 1.2 * max([v for v in max_post_values if not np.isnan(v)])  
            plt.ylim(0, y_max)

    # Save the figure
    if not os.path.exists(f"Results/ChangeCounting/disaster{disaster_id}/charts"):
        os.makedirs(f"Results/ChangeCounting/disaster{disaster_id}/charts")

    file_path = f'./Results/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png'
    plt.savefig(file_path, dpi=350)
    print("saved: ",file_path)

    os.makedirs(f"visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/ChangeCounting/disaster{disaster_id}/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png'
    shutil.copyfile(file_path, visualisation_file_path)
    
    plt.close()

def plot_full_periods_change_count(pre_disaster_days, imm_disaster_days, post_disaster_days, show_percent):
    
    file_path = f"./Results/ChangeCounting/summary/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")

    summary_data = pd.read_csv(file_path)

    periods = ['Pre', 'Imm', 'Post']
    creates = summary_data['creates'][:3].values
    edits = summary_data['edits'][:3].values
    deletes = summary_data['deletes'][:3].values
    total_changes = creates + edits + deletes  # Compute total for each period

    if show_percent:
        # Convert to percentage of total changes for each period
        creates = (creates / total_changes) * 100
        edits = (edits / total_changes) * 100
        deletes = (deletes / total_changes) * 100

    # Stacked bar chart for detailed breakdown
    plt.figure(figsize=(8, 6))
    width = 0.6
    x = np.arange(len(periods))  # Use np.arange for proper alignment

    plt.grid(which='major', color='black', linestyle='-', linewidth=0.5, zorder=0)
    plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5, zorder=0)
    plt.minorticks_on()
    
    alpha = 0.8
    plt.bar(x, creates, width, label='Creates', color='blue', zorder=2, alpha=alpha)
    plt.bar(x, edits, width, bottom=creates, label='Edits', color='orange', zorder=2, alpha=alpha)
    plt.bar(x, deletes, width, bottom=creates + edits, label='Deletes', color='green', zorder=2, alpha=alpha)

    # Format y-axis labels
    if show_percent:
        plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter())
        plt.ylabel("Percentage of Changes")
        title = "Proportion of Change Types by Period"
    else:
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x / 1e6)}M'))
        plt.ylabel("Number of Changes")
        title = "Total Change Counts by Period"

    # Configure axis labels and title
    plt.xticks(x, periods)
    plt.title(title)
    plt.xlabel('Period')
    plt.legend()

    # Save the plot
    output_dir = "./Results/ChangeCounting/summary/charts"
    os.makedirs(output_dir, exist_ok=True)
    percent_suffix = "_percent" if show_percent else ""
    file_path = f'./Results/ChangeCounting/summary/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_count_stacked_bar{percent_suffix}.png'
    plt.savefig(file_path, dpi=350)

    # Copy to visualization site
    vis_output_dir = "visualisation-site/public/ChangeCounting/summary/charts"
    os.makedirs(vis_output_dir, exist_ok=True)
    vis_output_path = f"{vis_output_dir}/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_count_stacked_bar{percent_suffix}.png"
    shutil.copyfile(file_path, vis_output_path)

    plt.close()

def plot_total_change_counts(pre_disaster_days, imm_disaster_days, post_disaster_days, disaster_ids):
    db_utils = DB_Utils()
    db_utils.db_connect()

    total_counts = pd.DataFrame(columns=["disaster_id","disaster_title","total"])
    for disaster_id in disaster_ids:
        data = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_full_periods_change_count.csv")
        total = data.iloc[-1]["total"]
        _, _, disaster_area, _, disaster_date, _, _  = db_utils.get_disaster_with_id(disaster_id)

        total_counts = pd.concat(
            [total_counts, pd.DataFrame({"disaster_id": [disaster_id], "disaster_title": [f"{disaster_area[0]} | {disaster_date.year}"], "total": [total]})],
            ignore_index=True,
        )
      
    print(total_counts)
    
    # Pie chart for total operations
    plt.figure(figsize=(6, 5))
    plt.pie(total_counts["total"], labels=total_counts["disaster_title"], autopct='%1.1f%%', startangle=140)
    plt.title('Proportion of total changes by disaster')

    os.makedirs(f"Results/ChangeCounting/summary/charts", exist_ok=True)
    file_path = f'./Results/ChangeCounting/summary/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_total_count_pie.png'
    plt.savefig(file_path, dpi=350)
    print(f"Saved: ./Results/ChangeCounting/summary/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_total_count_pie.png")

    os.makedirs(f"visualisation-site/public/ChangeCounting/summary/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/ChangeCounting/summary/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_changes_total_count_pie.png'
    shutil.copyfile(file_path, visualisation_file_path)

    plt.close()

def plot_change_counts_all_disasters(disaster_ids, prophet_model, post_only, plot_edit_types, period, interval_length, columns, disaster_ids_type):

    time_period = "day" if interval_length == 1 else "week" if interval_length == 7 else "month"

    num_disasters = len(disaster_ids)
    rows = math.ceil(num_disasters / columns)

    # Adjust the figure size to fit tightly without space
    fig, axes = plt.subplots(rows, columns, figsize=(columns * 12, rows * 7))


    # Iterate through disasters
    for idx, disaster_id in enumerate(disaster_ids):
        row, col = divmod(idx, columns)
        ax = axes[row, col] if rows > 1 else axes[col]

        file_path = f'./Results/ChangeCounting/disaster{disaster_id}/charts/{period[0]}_{period[1]}_{period[2]}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}.png'
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
    os.makedirs(f"./Results/ChangeCounting/combined/charts/", exist_ok=True)
    output_path = f'./Results/ChangeCounting/combined/charts/{period[0]}_{period[1]}_{period[2]}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}_grid_{disaster_ids_type}.png'
    plt.savefig(output_path, dpi=200, bbox_inches='tight', pad_inches=0)

    print(f"Saved: {output_path}")

    os.makedirs(f"visualisation-site/public/ChangeCounting/combined/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/ChangeCounting/combined/charts/{period[0]}_{period[1]}_{period[2]}_{time_period}_counts{"_prophet_forecast" if prophet_model else ""}{"" if len(plot_edit_types) == 4 else "_"+"_".join(plot_edit_types)}{"_post_only" if post_only else ""}_grid_{disaster_ids_type}.png'
    shutil.copyfile(output_path, visualisation_file_path)

    print(f"Saved: {visualisation_file_path}")

    plt.close()


# Multithread the plotting
def process_disaster(disaster_id, periods, prophet_model_bools, post_only_bools, plot_edit_types_list):

    db_utils = DB_Utils()
    db_utils.db_connect()

    # Get disaster details
    _, disaster_country, disaster_area, _, disaster_date, _, _ = db_utils.get_disaster_with_id(disaster_id)
    
    for prophet_model in prophet_model_bools:
        for post_only in post_only_bools:
            for plot_edit_types in plot_edit_types_list:
                for period in periods:
                    print(f"Processing: {disaster_id}, {disaster_area[0]}, {disaster_date}")
                    # Call plotting functions
                    """
                    plot_counts(
                        disaster_id, 
                        disaster_country[0], 
                        disaster_area[0], 
                        disaster_date, 
                        prophet_model, 
                        plot_edit_types, 
                        post_only,
                        pre_disaster_days=period[0], 
                        imm_disaster_days=period[1], 
                        post_disaster_days=period[2]
                    )
                    """

                    for interval_length in [1, 7, 30]:
                        plot_counts_specific(
                            disaster_id, 
                            disaster_country[0], 
                            disaster_area[0], 
                            disaster_date, 
                            prophet_model, 
                            plot_edit_types, 
                            post_only, 
                            pre_disaster_days=period[0], 
                            imm_disaster_days=period[1], 
                            post_disaster_days=period[2], 
                            interval_length=interval_length
                        )
    return f"Completed disaster_id: {disaster_id}"
    
def process_combined_disaster_plots(disaster_ids, plot_edit_types_list, period, prophet_model_bools, post_only_bools, interval_lengths, columns, disaster_ids_type):
    for plot_edit_types in plot_edit_types_list:
        for prophet_model in prophet_model_bools:
            for post_only in post_only_bools:
                for interval_length in interval_lengths:
    
                    plot_change_counts_all_disasters(
                        disaster_ids=disaster_ids,
                        prophet_model=prophet_model,
                        post_only=post_only,
                        plot_edit_types=plot_edit_types,
                        period=period,
                        interval_length=interval_length,
                        columns=columns,
                        disaster_ids_type=disaster_ids_type,
                    )




if __name__ == "__main__":

    periods = [(365,30,365), (180,30,365),]
    periods = [ (1095, 30, 365),  (365, 60, 335), (1095, 60, 365),(180,60,365),]
    periods = [(365,60,365),(1095,60,365)]
    prophet_model_bools = [True, False]
    post_only_bools = [True, False]
    interval_lengths = [1,7,30]
    plot_edit_types_list = [["creates", "edits", "deletes", "total"],["creates"],["edits"],["deletes"],["total"]]
    #plot_edit_types_list = [["deletes"],["total"]]

    # Sorted by geographic region
    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = [2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
        disaster_ids = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]
        #disaster_ids = [3]
        print("Disaster IDs defined:", disaster_ids)
        
   #disaster_ids = range(2,19)
    generate_specific = True
    generate_combined = False
    #disaster_ids = [5]

    for period in periods:
        plot_full_periods_change_count(period[0], period[1], period[2], False)
        plot_full_periods_change_count(period[0], period[1], period[2], True)
        plot_total_change_counts(period[0], period[1], period[2], disaster_ids)
        
    
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
                    plot_edit_types_list
                ): disaster_id for disaster_id in disaster_ids
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                disaster_id = futures[future]
                try:
                    result = future.result()
                    print(result)
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
                    ): (period) for period in periods
                }

                # Collect results as tasks complete
                for future in concurrent.futures.as_completed(futures):
                    task_details = futures[future]
                    try:
                        result = future.result()
                        print(result)
                    except Exception as e:
                        print(f"Plotting failed for {task_details}: {e}")