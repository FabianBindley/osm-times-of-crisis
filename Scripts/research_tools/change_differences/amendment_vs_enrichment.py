import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic
import concurrent.futures
import sys
import ast
import os
import pickle
import csv
import shutil
import osmium
from shapely import wkb
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def generate_full_periods_plot_for_all_disasters_by_edit_type(pre_disaster_days, imm_disaster_days, post_disaster_days, show_percent):

    # Load the dataset
    file_path = f"./Results/ChangeDifferences/summary/all_disaster_analysis_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")

    summary_data = pd.read_csv(file_path)

    # Aggregate change types across all disasters for each period
    periods = ['pre', 'imm', 'post']
    creates = []
    edits = []
    deletes = []
    total_changes = []

    for period in periods:
        period_data = summary_data[summary_data['period'] == period]
        creates.append(period_data['previous_change_creates'].sum())
        edits.append(period_data['previous_change_edits'].sum())
        deletes.append(period_data['previous_change_deletes'].sum())
        total_changes.append(creates[-1] + edits[-1] + deletes[-1])

    creates = np.array(creates)
    edits = np.array(edits)
    deletes = np.array(deletes)
    total_changes = np.array(total_changes)

    if show_percent:
        creates = (creates / total_changes) * 100
        edits = (edits / total_changes) * 100
        deletes = (deletes / total_changes) * 100

    # Create a stacked bar chart
    plt.figure(figsize=(8, 6))
    width = 0.6
    x = np.arange(len(periods))  # Use np.arange for proper alignment

    plt.grid(which='major', color='black', linestyle='-', linewidth=0.5, zorder=0)
    plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5, zorder=0)
    plt.minorticks_on()

    # Plot the stacked bars
    alpha = 0.8
    plt.bar(x, creates, width, label='Creates', color='blue', zorder=2, alpha=alpha)
    plt.bar(x, edits, width, bottom=creates, label='Edits', color='orange', zorder=2, alpha=alpha)
    plt.bar(x, deletes, width, bottom=creates + edits, label='Deletes', color='green', zorder=2, alpha=alpha)

    # Format y-axis labels
    if show_percent:
        plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter())
        plt.ylabel("Percentage of Changes")
    else:
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x / 1e6)}M'))
        plt.ylabel("Number of Changes")

    # Configure axis labels and title
    plt.xticks(x, ['Pre', 'Immediate', 'Post'])
    plt.title('Proportion of Previous Changes by Change Type Across All Disasters' if show_percent else 'Total Previous Changes by Change Type Across All Disasters')
    plt.xlabel('Period')
    plt.legend()

    # Save the plot
    output_dir = "./Results/ChangeDifferences/summary/charts"
    os.makedirs(output_dir, exist_ok=True)
    percent_suffix = "_percent" if show_percent else ""
    output_path = f"{output_dir}/all_disasters_previous_changes_stacked_bar_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}{percent_suffix}.png"
    plt.savefig(output_path, dpi=350)

    # Copy to visualization site
    vis_output_dir = "visualisation-site/public/ChangeDifferences/summary/charts"
    os.makedirs(vis_output_dir, exist_ok=True)
    vis_output_path = f"{vis_output_dir}/all_disasters_previous_changes_stacked_bar_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}{percent_suffix}.png"
    shutil.copyfile(output_path, vis_output_path)

    # Show and close the plot
    plt.close()

def generate_full_periods_plot_for_all_disasters_by_tag_edit_type(pre_disaster_days, imm_disaster_days, post_disaster_days, show_percent):
    # Load the dataset
    file_path = "./Results/ChangeDifferences/summary/all_disaster_analysis_365_60_365_.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")

    summary_data = pd.read_csv(file_path)

    # Aggregate tag changes across all disasters for each period
    periods = ['pre', 'imm', 'post']
    tags_created = []
    tags_edited = []
    tags_deleted = []

    for period in periods:
        period_data = summary_data[summary_data['period'] == period]
        tags_created.append(period_data['tags_created'].sum())
        tags_edited.append(period_data['tags_edited'].sum())
        tags_deleted.append(period_data['tags_deleted'].sum())

    # Convert to percentages if required
    if show_percent:
        total_changes = np.array(tags_created) + np.array(tags_edited) + np.array(tags_deleted)
        tags_created = (np.array(tags_created) / total_changes) * 100
        tags_edited = (np.array(tags_edited) / total_changes) * 100
        tags_deleted = (np.array(tags_deleted) / total_changes) * 100

    # Create a stacked bar chart
    plt.figure(figsize=(8, 6))
    width = 0.6
    x = np.arange(len(periods))  # Use np.arange for proper alignment

    plt.grid(which='major', color='black', linestyle='-', linewidth=0.5, zorder=0)
    plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5, zorder=0)
    plt.minorticks_on()

    # Plot the stacked bars
    alpha = 0.8
    plt.bar(x, tags_created, width, label='Tags Created', color='blue', zorder=2, alpha=alpha)
    plt.bar(x, tags_edited, width, bottom=tags_created, label='Tags Edited', color='orange', zorder=2, alpha=alpha)
    plt.bar(x, tags_deleted, width, bottom=np.array(tags_created) + np.array(tags_edited), label='Tags Deleted', color='green', zorder=2, alpha=alpha)

    # Format y-axis labels
    if show_percent:
        plt.ylabel("Percentage of Tag Changes")
        plt.ylim(0, 100)
    else:
        plt.ylabel("Number of Tag Changes")

    # Configure axis labels and title
    plt.xticks(x, ['Pre', 'Immediate', 'Post'])
    plt.title('Proportion of tag changes by type across all disasters' if show_percent else 'Total tag changes by change type across all disasters')
    plt.xlabel('Period')
    plt.legend()

    # Save the plot
    output_dir = "./Results/ChangeDifferences/summary/charts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/all_disasters_tag_changes_stacked_bar_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{'percent' if show_percent else 'count'}.png"
    plt.savefig(output_path, dpi=350)

    # Copy to visualization site
    vis_output_dir = "visualisation-site/public/ChangeDifferences/summary/charts"
    os.makedirs(vis_output_dir, exist_ok=True)
    vis_output_path = f"{vis_output_dir}/all_disasters_tag_changes_stacked_bar_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}_{'percent' if show_percent else 'count'}.png"
    shutil.copyfile(output_path, vis_output_path)

    # Show and close the plot
    plt.show()
    plt.close()


if __name__ == "__main__":
    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    disaster_ids_region =   [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17] # Geographic region
    disaster_ids_disaster = [3,6,11,5,12,17,8,9,13,2,15,16,10,7,18,14] # Disaster Type

    disaster_ids_types = ["type","region"] # "region", "type"
    
    #generate_full_periods_plot_for_all_disasters_by_edit_type(pre_disaster_days=365, imm_disaster_days=60, post_disaster_days=365, show_percent=False)
    #generate_full_periods_plot_for_all_disasters_by_edit_type(pre_disaster_days=365, imm_disaster_days=60, post_disaster_days=365, show_percent=True)

    generate_full_periods_plot_for_all_disasters_by_tag_edit_type(pre_disaster_days=365, imm_disaster_days=60, post_disaster_days=365, show_percent=False)
    generate_full_periods_plot_for_all_disasters_by_tag_edit_type(pre_disaster_days=365, imm_disaster_days=60, post_disaster_days=365, show_percent=True)

    for disaster_ids_type in disaster_ids_types:

        if disaster_ids_type == "region":
            disaster_ids = disaster_ids_region
        else:
            disaster_ids = disaster_ids_disaster

        

