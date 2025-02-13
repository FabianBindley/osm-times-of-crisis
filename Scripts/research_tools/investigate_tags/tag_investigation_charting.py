import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def plot_chart_percent_of_total_changes_period_for_keys(keys):
    # Load CSV files
    keys_df_pre = pd.read_csv("./Results/TagInvestigation/summary/top_4000_keys/pre.csv")
    keys_df_imm = pd.read_csv("./Results/TagInvestigation/summary/top_4000_keys/imm.csv")
    keys_df_post = pd.read_csv("./Results/TagInvestigation/summary/top_4000_keys/post.csv")

    # Filter and rename columns for each period
    filtered_df_pre = (
        keys_df_pre[keys_df_pre['key'].isin(keys)]
        .drop(columns=["percent_difference_from_pre", "percent_difference_from_pre_day", "count"]) 
        .rename(columns={"percent_of_total_changes": "percent_of_total_changes_pre"})
    )

    filtered_df_imm = (
        keys_df_imm[keys_df_imm['key'].isin(keys)]
        .drop(columns=["percent_difference_from_pre", "percent_difference_from_pre_day", "count"])  
        .rename(columns={"percent_of_total_changes": "percent_of_total_changes_imm"})
    )

    filtered_df_post = (
        keys_df_post[keys_df_post['key'].isin(keys)]
        .drop(columns=["percent_difference_from_pre", "percent_difference_from_pre_day", "count"])
        .rename(columns={"percent_of_total_changes": "percent_of_total_changes_post"})
    )

    # Merge datasets
    merged_df = (
        filtered_df_pre
        .merge(filtered_df_imm, on="key", how="outer")
        .merge(filtered_df_post, on="key", how="outer")
    )

    merged_df = merged_df.sort_values(by=["percent_of_total_changes_pre"], ascending=False)

    # Time periods (X-axis)
    time_periods = ["Pre", "Imm", "Post"]

    data_values = np.array([
        merged_df["percent_of_total_changes_pre"],
        merged_df["percent_of_total_changes_imm"],
        merged_df["percent_of_total_changes_post"]
    ]).T  # Transpose to match correct shape

    # Create the stacked area chart 
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.stackplot(time_periods, data_values, labels=merged_df["key"], alpha=0.8)

    ax.set_yscale('linear')

    # Labels & Formatting
    ax.set_title("Change in feature keys in phases across all disasters")
    ax.set_xlabel("Time Period")
    ax.set_ylabel(f"% of Total Changes")

    ax.legend(loc="upper left", bbox_to_anchor=(1, 1.02), title="Feature", frameon=True)
    plt.subplots_adjust(left=0.1, right=0.82, top=0.9, bottom=0.1)  # More space on the right

    # Show the plot
    os.makedirs(f"Results/TagInvestigation/summary/charts", exist_ok=True)
    file_path = f'./Results/TagInvestigation/summary/charts/change_keys_across_phases_all_disasters.png'
    plt.savefig(file_path, dpi=350)
    print(f"Saved: {file_path}")

    os.makedirs(f"visualisation-site/public/TagInvestigation/summary/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/TagInvestigation/summary/charts/change_keys_across_phases_all_disasters.png'
    shutil.copyfile(file_path, visualisation_file_path)

    plt.close()

def plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by):
    # Load CSV files
    values_df_pre = pd.read_csv("./Results/TagInvestigation/summary/top_n_tag_key_values/top_4000_key_values/pre.csv")
    values_df_imm = pd.read_csv("./Results/TagInvestigation/summary/top_n_tag_key_values/top_4000_key_values/imm.csv")
    values_df_post = pd.read_csv("./Results/TagInvestigation/summary/top_n_tag_key_values/top_4000_key_values/post.csv")

    # Define layout: len(keys) charts in a grid
    ncols = 2
    nrows = math.ceil(len(keys) / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(13, 4 * nrows))

    # Flatten axes array if more than 1 row/column, else keep it as a list
    axes = np.array(axes).flatten() if isinstance(axes, np.ndarray) else [axes]

    for idx, key in enumerate(keys):

        filtered_df_pre = (
            values_df_pre[values_df_pre['key'] == key]
            .sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n*2)
            .rename(columns={"percent_of_total_changes_for_key": "percent_of_total_changes_pre"})
        )

        filtered_df_imm = (
            values_df_imm[values_df_imm['key'] == key]
            .sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n*2)
            .rename(columns={"percent_of_total_changes_for_key": "percent_of_total_changes_imm"})
        )

        filtered_df_post = (
            values_df_post[values_df_post['key'] == key]
            .sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n*2)
            .rename(columns={"percent_of_total_changes_for_key": "percent_of_total_changes_post"})
        )

        # Merge datasets on 'value' column
        merged_df = (
            filtered_df_pre[['value', 'percent_of_total_changes_pre']]
            .merge(filtered_df_imm[['value', 'percent_of_total_changes_imm']], on="value", how="outer")
            .merge(filtered_df_post[['value', 'percent_of_total_changes_post']], on="value", how="outer")
        )

        # Sort by total changes across all periods
        merged_df = merged_df.sort_values(by=[f"percent_of_total_changes_{sort_by}"], ascending=False).head(n)


        time_periods = ["Pre", "Imm", "Post"]

        # Prepare data for plotting
        data_values = np.array([
            merged_df["percent_of_total_changes_pre"].fillna(0),
            merged_df["percent_of_total_changes_imm"].fillna(0),
            merged_df["percent_of_total_changes_post"].fillna(0)
        ]).T  # Transpose to match correct shape

        # Plot on the corresponding subplot
        ax = axes[idx]
        ax.stackplot(time_periods, data_values, labels=merged_df["value"], alpha=0.8)
        ax.set_yscale('linear')
        ax.set_title(f"{key.capitalize()}")
        ax.set_xlabel("Time Period")
        ax.set_ylabel("Percent of Total Changes")
         # Move legend outside each subplot
        ax.legend(
            loc="upper left",
            bbox_to_anchor=(1.03, 1.02),
            title="Value",
            fontsize=8,
            frameon=True,
            framealpha=0.8,
            borderpad=0.5
        )


    # Hide any empty subplots (if `len(keys)` is not exactly `nrows * ncols`)
    for i in range(idx + 1, len(axes)):
        fig.delaxes(axes[i])  # Remove unused subplot

    # Adjust layout and show the plot
    plt.tight_layout()
    fig.suptitle(f"Variation in proportion of changes for object types across disaster periods for 'Building', 'Highway', \n 'Amenity' and 'Leisure' feature keys. Sorted by % of total changes in the {sort_by.capitalize()} period, top {n} values.",
                 fontsize=14)
    
    plt.subplots_adjust(left=0.1, right=0.87, top=0.9, bottom=0.1)  # Increase right padding slightly

    # Show the plot
    os.makedirs(f"Results/TagInvestigation/summary/charts", exist_ok=True)
    file_path = f'./Results/TagInvestigation/summary/charts/change_key_top_{n}_values_across_phases_all_disasters_sort_{sort_by}.png'
    plt.savefig(file_path, dpi=350)
    print(f"Saved: {file_path}")

    os.makedirs(f"visualisation-site/public/TagInvestigation/summary/charts", exist_ok=True)
    visualisation_file_path = f'visualisation-site/public/TagInvestigation/summary/charts/change_key_top_{n}_values_across_phases_all_disasters_sort_{sort_by}.png'
    shutil.copyfile(file_path, visualisation_file_path)

    plt.close()

def plot_usage_charts_key(disaster_ids, key, period):
    key_usage_df = pd.DataFrame(columns=["disaster_id", "key", "percent_of_total_changes","disaster_label"])
    db_utils = DB_Utils()
    db_utils.db_connect()

    for disaster_id in disaster_ids:
        key_usage_for_disaster = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_{period}.csv")
        key_usage_for_disaster = key_usage_for_disaster[key_usage_for_disaster["key"] == key]
        print(f"{period} {disaster_id}")

        if not key_usage_for_disaster.empty:
            percent_of_total_changes = key_usage_for_disaster["percent_of_total_changes"].values[0]
        else:
            percent_of_total_changes = 0  # Assign a default value when the key is missing
        
        (_, _, disaster_area, _, disaster_date, _, disaster_type) = db_utils.get_disaster_with_id(disaster_id)
        disaster_label = f"{disaster_area[0]} {disaster_date.year} | {disaster_type}"
        
        key_usage_df.loc[len(key_usage_df)] = {
            "disaster_id": int(disaster_id),
            "key": key,
            "percent_of_total_changes": percent_of_total_changes,
            "disaster_label": disaster_label
        }

    # Sort by percentage of total changes
    key_usage_df = key_usage_df.sort_values(by="percent_of_total_changes", ascending=False)

    # Plotting
    plt.figure(figsize=(12, 6))
    bars = plt.bar(key_usage_df["disaster_label"], key_usage_df["percent_of_total_changes"], color='firebrick', alpha=0.8)

    
    # Add labels on top of bars
    for bar in bars:
        height = bar.get_height()

        if height > 5:
            multiplier = 0.005
        elif height > 1:
            multiplier = 0.01
        else:
            multiplier = 0.05

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + height * multiplier,  # Offset above the bar
            f"{height:,.2f}%",  # Format with percentage
            ha="center",
            fontsize=8,
            fontweight="bold"
        )
    
    
    plt.ylabel("% of Total Changes")
    plt.title(f"Percentage of Total Changes for Key '{key}' in '{period}' Period")
    plt.xticks(rotation=90, fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save the plot
    os.makedirs("Results/TagInvestigation/summary/charts/key_usage_charts", exist_ok=True)
    file_path = f"Results/TagInvestigation/summary/charts/key_usage_charts/usage_{key}_{period}.png"
    plt.savefig(file_path, dpi=350, bbox_inches="tight")
    print(f"Saved: {file_path}")

    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/charts/key_usage_charts/usage_{key}_{period}.png"
    os.makedirs("visualisation-site/public/TagInvestigation/summary/charts/key_usage_charts", exist_ok=True)
    shutil.copyfile(file_path, visualisation_file_path)
    print(f"Copied to: {visualisation_file_path}")

    plt.close()

def plot_usage_charts_values_for_key(disaster_ids, key, period, n):
    value_usage_df = pd.DataFrame(columns=["disaster_id", "key", "value", "percent_of_total_changes","disaster_label"])
    for disaster_id in disaster_ids:
        value_usage_for_disaster = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_{period}.csv")
        value_usage_for_disaster = value_usage_for_disaster[value_usage_for_disaster["key"] == key]

        # For building frop yes row because its boring
        if key == "building":
            value_usage_for_disaster = value_usage_for_disaster[value_usage_for_disaster["value"] != "yes"]

        value_usage_for_disaster = value_usage_for_disaster[:n]
        for index, row in value_usage_for_disaster.iterrows():
            value_usage_df.loc[len(value_usage_df)] = {"disaster_id": disaster_id, "key": key, "value": value_usage_for_disaster["value"], "percent_of_total_changes_for_key": value_usage_for_disaster["percent_of_total_changes_for_key"],}

    print(value_usage_df)

if __name__ == "__main__":
    #keys = ["building", "highway", "amenity", "leisure"]
    #keys = ["building","highway","source","name","surface","amenity","landuse","waterway","natural","leisure","emergency"]
    keys = ["building"]
    compare_percent_of_changes_period = False
    generate_charts_usage_by_disaster = True

    if compare_percent_of_changes_period:

        plot_chart_percent_of_total_changes_period_for_keys(keys)
        n = 12
        plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by="pre")
        plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by="imm")
        plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by="post")
    
    disaster_ids = range(2,19)
    disaster_ids = range(2,6)
    periods = ["pre","imm","post"]
    if generate_charts_usage_by_disaster:
        for key in keys:
            for period in periods:
                #plot_usage_charts_key(disaster_ids, key, period)
                plot_usage_charts_values_for_key(disaster_ids, key, period, n=15)