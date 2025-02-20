import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import os
import shutil
import sys
import json
import re

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

    """
        # Exclude building yes because its boring
    if key == "building":
        tag_key_values = tag_key_values[tag_key_values["value"] != "yes"]
    """

    for idx, key in enumerate(keys):

        # Load and filter data
        filtered_df_pre = values_df_pre[values_df_pre['key'] == key]
        filtered_df_imm = values_df_imm[values_df_imm['key'] == key]
        filtered_df_post = values_df_post[values_df_post['key'] == key]

        # **Exclude "yes" if the key is "building"**
        if key == "building":
            filtered_df_pre = filtered_df_pre[filtered_df_pre["value"] != "yes"]
            filtered_df_imm = filtered_df_imm[filtered_df_imm["value"] != "yes"]
            filtered_df_post = filtered_df_post[filtered_df_post["value"] != "yes"]

        filtered_df_pre = (
            filtered_df_pre.sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n * 2)
            .rename(columns={"percent_of_total_changes_for_key": "percent_of_total_changes_pre"})
        )

        filtered_df_imm = (
            filtered_df_imm.sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n * 2)
            .rename(columns={"percent_of_total_changes_for_key": "percent_of_total_changes_imm"})
        )

        filtered_df_post = (
            filtered_df_post.sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n * 2)
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

def plot_usage_charts_key_legacy(disaster_ids, key, period):
    key_usage_df = pd.DataFrame(columns=["disaster_id", "key", "percent_of_total_changes","disaster_label"])

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

def plot_usage_charts_for_key(disaster_ids, key, sort_by, disaster_ids_type):
    

    tag_keys = pd.read_csv("Results/TagInvestigation/summary/unique_tag_keys_count_all.csv")
    tag_keys = tag_keys[tag_keys["key"]==key]

    disaster_labels = {}

    for disaster_id in disaster_ids:
        (_, _, disaster_area, _, disaster_date, _, disaster_type) = db_utils.get_disaster_with_id(disaster_id)
        #disaster_labels[disaster_id] = f"{disaster_area[0]} {disaster_date.year} | {disaster_type}"
        disaster_labels[disaster_id] = f"{disaster_area[0]} {disaster_date.year}"


    key_usage_df = pd.DataFrame(columns=["disaster_id", "key", "percent_of_total_changes_pre", "percent_of_total_changes_imm", "percent_of_total_changes_post","disaster_label"]) 

    for disaster_id in disaster_ids:

        key_usage_for_disaster_pre = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_pre.csv")
        key_usage_for_disaster_pre = key_usage_for_disaster_pre[key_usage_for_disaster_pre["key"]==key]

        key_usage_for_disaster_imm = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_imm.csv")
        key_usage_for_disaster_imm = key_usage_for_disaster_imm[key_usage_for_disaster_imm["key"]==key]

        key_usage_for_disaster_post = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_keys_count_post.csv")
        key_usage_for_disaster_post = key_usage_for_disaster_post[key_usage_for_disaster_post["key"]==key]

        pre_value = key_usage_for_disaster_pre[key_usage_for_disaster_pre["key"] == key]["percent_of_total_changes"]
        imm_value = key_usage_for_disaster_imm[key_usage_for_disaster_imm["key"] == key]["percent_of_total_changes"]
        post_value = key_usage_for_disaster_post[key_usage_for_disaster_post["key"] == key]["percent_of_total_changes"]

        pre_percent = pre_value.iloc[0] if not pre_value.empty else 0
        imm_percent = imm_value.iloc[0] if not imm_value.empty else 0
        post_percent = post_value.iloc[0] if not post_value.empty else 0


        key_usage_df.loc[len(key_usage_df)] = {
            "disaster_id": disaster_id, 
            "key": key,  
            "percent_of_total_changes_pre": pre_percent,  
            "percent_of_total_changes_imm": imm_percent,  
            "percent_of_total_changes_post": post_percent,  
            "disaster_label": disaster_labels[disaster_id]
        }

    # Sort by percentage of total changes
    if sort_by != None:
        key_usage_df = key_usage_df.sort_values(by=f"percent_of_total_changes_{sort_by}", ascending=False)

    # Extract disasters and their corresponding data
    disasters = key_usage_df["disaster_label"]
    pre_values = key_usage_df["percent_of_total_changes_pre"]
    imm_values = key_usage_df["percent_of_total_changes_imm"]
    post_values = key_usage_df["percent_of_total_changes_post"]

    # Bar chart settings
    bar_width = 0.25  # Width of each bar
    x_indexes = np.arange(len(disasters))  # Position for each disaster on the x-axis

    # Create the figure and plot the bars
    plt.figure(figsize=(18, 7))
    bars_pre = plt.bar(x_indexes, pre_values, width=bar_width, label="Pre", color="firebrick", alpha=0.7)
    bars_imm = plt.bar(x_indexes + bar_width, imm_values, width=bar_width, label="Imm", color="darkgreen", alpha=0.7)
    bars_post = plt.bar(x_indexes + 2 * bar_width, post_values, width=bar_width, label="Post", color="blueviolet", alpha=0.7)

    # Formatting the plot
    plt.ylabel("% of Total Changes")
    plt.title(f"% of changes that change an object of type '{key}' across disaster periods")
    plt.xticks(x_indexes + bar_width, disasters, rotation=90, fontsize=10)
    plt.legend(title="Time Period")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.minorticks_on()  # Enable minor ticks
    plt.grid(which="minor", axis="y", linestyle=":", alpha=0.4)  # Minor gridlines with dotted style
    plt.subplots_adjust(bottom=0.3)  # Adjust bottom margin to prevent cutoff

    # Save the plot
    os.makedirs("Results/TagInvestigation/summary/charts/key_usage_charts", exist_ok=True)
    file_path = f"Results/TagInvestigation/summary/charts/key_usage_charts/usage_{key}_{disaster_ids_type}.png"
    plt.savefig(file_path, dpi=350, bbox_inches="tight")
    print(f"Saved: {file_path}")

    os.makedirs("visualisation-site/public/TagInvestigation/summary/charts/key_usage_charts", exist_ok=True)
    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/charts/key_usage_charts/usage_{key}_{disaster_ids_type}.png"
    shutil.copyfile(file_path, visualisation_file_path)
    print(f"Copied to: {visualisation_file_path}")

    plt.close()

def sanitize_filename(value):
    return re.sub(r'[\/:*?"<>|]', '_', value)  


def plot_usage_charts_values_for_key(disaster_ids, key, n, sort_by, disaster_ids_type):
    

    tag_key_values = pd.read_csv("Results/TagInvestigation/summary/tag_key_values_count_all.csv")
    tag_key_values = tag_key_values[tag_key_values["key"]==key]

    key_top_n_values = tag_key_values[:n]

    disaster_labels = {}

    for disaster_id in disaster_ids:
        (_, _, disaster_area, _, disaster_date, _, disaster_type) = db_utils.get_disaster_with_id(disaster_id)
        #disaster_labels[disaster_id] = f"{disaster_area[0]} {disaster_date.year} | {disaster_type}"
        disaster_labels[disaster_id] = f"{disaster_area[0]} {disaster_date.year}"


    for index, tag_value in key_top_n_values.iterrows():
        value = tag_value["value"]
        value_usage_df = pd.DataFrame(columns=["disaster_id", "value",  "percent_of_total_changes_for_key_pre", "percent_of_total_changes_for_key_imm", "percent_of_total_changes_for_key_post", "disaster_label"])

        for disaster_id in disaster_ids:

            value_usage_for_disaster_pre = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_pre.csv")
            value_usage_for_disaster_pre = value_usage_for_disaster_pre[value_usage_for_disaster_pre["value"]==value]

            value_usage_for_disaster_imm = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_imm.csv")
            value_usage_for_disaster_imm = value_usage_for_disaster_imm[value_usage_for_disaster_imm["value"]==value]

            value_usage_for_disaster_post = pd.read_csv(f"Results/TagInvestigation/disaster{disaster_id}/unique_tag_key_values_count_post.csv")
            value_usage_for_disaster_post = value_usage_for_disaster_post[value_usage_for_disaster_post["value"]==value]

            pre_value = value_usage_for_disaster_pre[value_usage_for_disaster_pre["value"] == value]["percent_of_total_changes_for_key"]
            imm_value = value_usage_for_disaster_imm[value_usage_for_disaster_imm["value"] == value]["percent_of_total_changes_for_key"]
            post_value = value_usage_for_disaster_post[value_usage_for_disaster_post["value"] == value]["percent_of_total_changes_for_key"]

            pre_percent = pre_value.iloc[0] if not pre_value.empty else 0
            imm_percent = imm_value.iloc[0] if not imm_value.empty else 0
            post_percent = post_value.iloc[0] if not post_value.empty else 0


            value_usage_df.loc[len(value_usage_df)] = {
                "disaster_id": disaster_id, 
                "value": value,  
                "percent_of_total_changes_for_key_pre": pre_percent,  
                "percent_of_total_changes_for_key_imm": imm_percent,  
                "percent_of_total_changes_for_key_post": post_percent,  
                "disaster_label": disaster_labels[disaster_id]
            }


        # Sort by percentage of total changes
        if sort_by != None:
            value_usage_df = value_usage_df.sort_values(by=f"percent_of_total_changes_for_key_{sort_by}", ascending=False)
    

        # Extract disasters and their corresponding data
        disasters = value_usage_df["disaster_label"]
        pre_values = value_usage_df["percent_of_total_changes_for_key_pre"]
        imm_values = value_usage_df["percent_of_total_changes_for_key_imm"]
        post_values = value_usage_df["percent_of_total_changes_for_key_post"]

        # Bar chart settings
        bar_width = 0.25  # Width of each bar
        x_indexes = np.arange(len(disasters))  # Position for each disaster on the x-axis

        # Create the figure and plot the bars
        plt.figure(figsize=(18, 7))
        bars_pre = plt.bar(x_indexes, pre_values, width=bar_width, label="Pre", color="firebrick", alpha=0.7)
        bars_imm = plt.bar(x_indexes + bar_width, imm_values, width=bar_width, label="Imm", color="darkgreen", alpha=0.7)
        bars_post = plt.bar(x_indexes + 2 * bar_width, post_values, width=bar_width, label="Post", color="blueviolet", alpha=0.7)

        # Formatting the plot
        plt.ylabel("% of Total Changes")
        plt.title(f"Percentage of changes of '{key}' objects with value '{value}' across disaster periods")
        plt.xticks(x_indexes + bar_width, disasters, rotation=90, fontsize=10)
        plt.legend(title="Time Period")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.minorticks_on()  # Enable minor ticks
        plt.grid(which="minor", axis="y", linestyle=":", alpha=0.4)  # Minor gridlines with dotted style
        plt.subplots_adjust(bottom=0.3)  # Adjust bottom margin to prevent cutoff

        # Save the plot
        os.makedirs("Results/TagInvestigation/summary/charts/key_value_usage_charts", exist_ok=True)
        file_path = f"Results/TagInvestigation/summary/charts/key_value_usage_charts/usage_{key}_{sanitize_filename(value)}_{disaster_ids_type}.png"
        plt.savefig(file_path, dpi=350, bbox_inches="tight")
        print(f"Saved: {file_path}")

        os.makedirs("visualisation-site/public/TagInvestigation/summary/charts/key_value_usage_charts", exist_ok=True)
        visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/charts/key_value_usage_charts/usage_{key}_{sanitize_filename(value)}_{disaster_ids_type}.png"
        shutil.copyfile(file_path, visualisation_file_path)
        print(f"Copied to: {visualisation_file_path}")

        plt.close()

def generate_top_n_keys_values_json(keys, n):
    """
    Generates a JSON file containing the top N values for each key.
    """
    keys_values_dict = {}

    # Read the master file containing key-value data
    tag_key_values = pd.read_csv("Results/TagInvestigation/summary/tag_key_values_count_all.csv")

    for key in keys:
        # Get the top N values for the key based on percent_of_total_changes_for_key
        top_values = (
            tag_key_values[tag_key_values["key"] == key]
            .sort_values(by="percent_of_total_changes_for_key", ascending=False)
            .head(n)["value"]
            .tolist()
        )

        # Store in dictionary
        keys_values_dict[key] = top_values

    # Save to JSON file
    json_output_path = "Results/TagInvestigation/summary/tag_keys_top_values.json"
    with open(json_output_path, "w") as json_file:
        json.dump(keys_values_dict, json_file, indent=4)

    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/tag_keys_top_values.json"
    shutil.copyfile(json_output_path, visualisation_file_path)


if __name__ == "__main__":

    keys = ["building", "highway", "amenity", "leisure"]

    compare_percent_of_changes_period = False
    generate_charts_usage_by_disaster = True

    db_utils = DB_Utils()
    db_utils.db_connect()

    if compare_percent_of_changes_period:

        plot_chart_percent_of_total_changes_period_for_keys(keys)
        n = 12
        plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by="pre")
        plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by="imm")
        plot_chart_percent_of_total_changes_period_for_values(keys, n, sort_by="post")
    
    
    keys = ["building","highway","amenity","leisure","surface","landuse","waterway","natural","leisure","emergency"]
    disaster_ids_region =   [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17] # Geographic region
    disaster_ids_disaster = [3,6,11,5,12,17,8,9,13,2,15,16,10,7,18,14] # Disaster Type
    disaster_ids_type = "region" # "region", "type"

    if disaster_ids_type == "region":
        disaster_ids = disaster_ids_region
    else:
        disaster_ids = disaster_ids_disaster

    periods = ["pre","imm","post"]

    n = 20 
    sort_by = None # None, "pre", "imm", "post"

    if generate_charts_usage_by_disaster:
        generate_top_n_keys_values_json(keys, n)
        for key in keys:
            for disaster_ids_type in ["type", "region"]:
                if disaster_ids_type == "region":
                    disaster_ids = disaster_ids_region
                else:
                    disaster_ids = disaster_ids_disaster
                    
                print(f"plotting for {disaster_ids_type}")
                plot_usage_charts_for_key(disaster_ids, key, sort_by, disaster_ids_type)
                plot_usage_charts_values_for_key(disaster_ids, key, n, sort_by, disaster_ids_type)