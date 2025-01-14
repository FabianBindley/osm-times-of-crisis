import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv 
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def load_count_percent_differences(disaster_id, pre_disaster_days, imm_disaster_days, average_metric):

    return pd.read_csv(f'./Results/ChangeCounting/disaster{disaster_id}/data/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_percent_difference_{average_metric}.csv')



def plot_disaster_percent_differences(disaster_percent_differences, average_metric):
  
    # Prepare data for plotting
    disaster_labels = []
    creates_imm = []
    edits_imm = []
    deletes_imm = []
    total_imm = []

    creates_post = []
    edits_post = []
    deletes_post = []
    total_post = []

    for _, _, disaster_area, disaster_date, percent_differences in disaster_percent_differences:
        # Use disaster area and year for labeling
        disaster_labels.append(f"{disaster_area[0]} ({disaster_date.year})")
        
        # Append percent differences for the immediate period (first row)
        creates_imm.append(percent_differences['creates'].iloc[0])
        edits_imm.append(percent_differences['edits'].iloc[0])
        deletes_imm.append(percent_differences['deletes'].iloc[0])
        total_imm.append(percent_differences['total'].iloc[0])

        # Append percent differences for the post-disaster period (second row)
        creates_post.append(percent_differences['creates'].iloc[1])
        edits_post.append(percent_differences['edits'].iloc[1])
        deletes_post.append(percent_differences['deletes'].iloc[1])
        total_post.append(percent_differences['total'].iloc[1])

    x = np.arange(len(disaster_labels))  # Label positions
    width = 0.2  # Width of the bars

    fig, axes = plt.subplots(2, 1, figsize=(12, 12), sharex=True)


    for axis in axes:
        axis.grid(which='major', color='black', linestyle='-', linewidth=0.5)
        axis.grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
        axis.minorticks_on()

    # Plot for immediate period
    axes[0].bar(x - width*1.5, creates_imm, width, label="Creates", zorder=3)
    axes[0].bar(x - width/2, edits_imm, width, label="Edits", zorder=3)
    axes[0].bar(x + width/2, deletes_imm, width, label="Deletes", zorder=3)
    axes[0].bar(x + width*1.5, total_imm, width, label="Total", zorder=3)

    axes[0].set_ylabel(f"% Difference During Disaster({average_metric.title()}) SymLog Scale")
    axes[0].set_title("Immediate Period Percent Differences in OSM Activity")

    # Plot for post-disaster period
    axes[1].bar(x - width*1.5, creates_post, width, label="Creates", zorder=3)
    axes[1].bar(x - width/2, edits_post, width, label="Edits", zorder=3)
    axes[1].bar(x + width/2, deletes_post, width, label="Deletes", zorder=3)
    axes[1].bar(x + width*1.5, total_post, width, label="Total", zorder=3)

    axes[1].set_ylabel(f"% Difference Post-Disaster ({average_metric.title()}) SymLog Scale")
    axes[1].set_title("Post-Disaster Percent Differences in OSM Activity")

    for axis in axes:
        axis.axhline(y=0, color='black', linewidth=0.8, linestyle='--')
        axis.set_yscale('symlog', linthresh=1)  # Use symmetric log scale
        axis.set_xlabel("Disaster")
        axis.set_xticks(x)
        axis.set_xticklabels(disaster_labels)
        axis.legend()

    # Adjust layout and show the plot
    plt.tight_layout()
    plt.savefig(f'./Results/ChangeCounting/summary/charts/{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_percent_difference_{average_metric}.png', dpi=350)

    plt.close()



if __name__ == "__main__":

    db_utils = DB_Utils()
    db_utils.db_connect()

    # Define the period lengths
    periods = [(365, 30, 365)]
    period_length = 30
    average_metrics = ["mean","median"] # mean or median

    
    for average_metric in average_metrics:
        disaster_percent_differences = []
        for disaster_id in range(2,7):
            for period in periods:

                (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
                pre_disaster_days, imm_disaster_days, post_disaster_days = period
                # First, compute the mean and median of pre and post disaster monthly counts:
                percent_differences = load_count_percent_differences(disaster_id, pre_disaster_days, imm_disaster_days, average_metric)
                disaster_percent_differences.append((disaster_id, disaster_country, disaster_area, disaster_date, percent_differences))


        plot_disaster_percent_differences(disaster_percent_differences, average_metric)