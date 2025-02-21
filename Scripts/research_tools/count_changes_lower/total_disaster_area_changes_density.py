import sys
import os
import ast
from contextlib import contextmanager
import numpy as np
from datetime import datetime, timedelta
import matplotlib.image as mpimg
import h3
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json
import pandas as pd
import concurrent.futures
import shutil 
import matplotlib.pyplot as plt
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def compute_disaster_areas(disaster_ids):

    # To compute the disaster area - we count the number of resolution 9 hexagons for urban areas, else number of res 8 hexagons
    areas = pd.DataFrame(columns=["disaster_id","resolution","num_hexes","area"])

    for disaster_id in disaster_ids:
        if disaster_id in [10,14,15,18]:
            resolution = 9
        else:
            resolution = 8

    
        hex_count = pd.read_csv(f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/365_365_{resolution}_hex_count.csv")
        accumulated_area = 0

        for index, row in hex_count.iterrows():
            area = h3.cell_area(row["h3_index"], unit='km^2')
            accumulated_area += area

        areas.loc[len(areas)] = {"disaster_id": int(disaster_id), "resolution": int(resolution), "num_hexes": int(len(hex_count)), "area": int(accumulated_area)}

    areas.to_csv("Results/ChangeDensityMapping/Summary/data/disaster_areas.csv", index=False)



def compute_disaster_area_densities(disaster_ids, period):
    pre_disaster_days, imm_disaster_days, post_disaster_days = period

    areas = pd.read_csv("Results/ChangeDensityMapping/Summary/data/disaster_areas.csv")
    area_densitys = pd.DataFrame(columns=["disaster_id","resolution","num_hexes","area","change_density"])


    for index, row in areas.iterrows():
        disaster_id = int(row["disaster_id"])

        if disaster_id not in disaster_ids:
            continue

        change_counts = pd.read_csv(f"./Results/ChangeCounting/disaster{disaster_id}/data/365_60_365_full_periods_change_count.csv")
        total_change_count = 0
        if pre_disaster_days != 0:
            total_change_count+=change_counts.iloc[0]["total"]
        if imm_disaster_days != 0:
            total_change_count+=change_counts.iloc[1]["total"]
        if post_disaster_days != 0:
            total_change_count+=change_counts.iloc[2]["total"]

        change_density = total_change_count / row["area"] if row["area"] > 0 else None
        print(change_density)
        area_densitys.loc[len(area_densitys)] = {"disaster_id": disaster_id, "resolution": row["resolution"], "num_hexes": row["num_hexes"], "area": row["area"], "change_density": change_density}


    area_densitys.to_csv(f"Results/ChangeDensityMapping/Summary/data/disaster_area_densities_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.csv", index=False)

def plot_all_disaster_area_densities(disaster_ids, period):
    pre_disaster_days, imm_disaster_days, post_disaster_days = period
    # Load disaster area densities
    area_densitys = pd.read_csv(f"Results/ChangeDensityMapping/Summary/data/disaster_area_densities_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.csv")

    db_utils = DB_Utils()
    db_utils.db_connect()

    area_densitys = area_densitys.sort_values(by="change_density", ascending=False)

    areas = area_densitys["area"].tolist()
    densities = area_densitys["change_density"].tolist()
    disaster_labels = [
        f"{disaster_area[0]} ({disaster_date.year})"
        for disaster_id in area_densitys["disaster_id"].tolist()
        for _, _, disaster_area, _, disaster_date, _ in [db_utils.get_disaster_with_id(disaster_id)]
    ]

   # Create the figure and axis
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Create a second y-axis for area
    ax2 = ax1.twinx()
    ax2.plot(disaster_labels, areas, color="red", marker="o", linestyle="-", linewidth=2, label="Area (km²)", zorder=3, alpha=0.6)

    # Bar chart for change count density (blue bars at the bottom)
    bars = ax1.bar(disaster_labels, densities, color="dodgerblue", alpha=0.8, label="Change Density", zorder=2)


    # Add labels on top of bars (text at the highest layer)
    if imm_disaster_days != 0:
        height_addition = 100
    elif pre_disaster_days == 365:
        height_addition = 10
    else:
        height_addition = 12


    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            height + height_addition,  # Offset above the bar
            f"{height:,.2f}",  # Format with commas
            ha="center",
            fontsize=8,
            fontweight="bold",
            zorder=5  # Ensure text is on top
        )
    ax1.set_ylim(0, max(densities) * 1.1)
    ax2.set_ylim(min(areas) * 0.9, max(areas) * 1.1)

    ax2.set_yscale("linear")


    # Formatting primary y-axis (change count density)
    ax1.set_ylabel("Change Count Density (Changes per km²)", fontsize=12, color="dodgerblue")
    ax1.tick_params(axis="y", labelcolor="dodgerblue")
    ax1.grid(axis="y", linestyle="--", alpha=0.7)

    # Formatting secondary y-axis (area)
    ax2.set_ylabel("Total Area (km²)", fontsize=12, color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Title and x-axis formatting
    if period == (365,60,365):
        period_designator = "all periods"
    elif period == (365,0,0):
        period_designator = "pre disaster"
    elif period == (0,60,0):
        period_designator = "imm disaster"
    else:
        period_designator = "post disaster"

    ax1.set_title(f"Comparison of change count densities and areas across disasters for {period_designator}", fontsize=14, fontweight="bold")
    ax1.set_xticklabels(disaster_labels, rotation=60, fontsize=10)

    # Legends
    # Combine both legends into one
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper center")


    # Save the plot
    os.makedirs("Results/ChangeDensityMapping/Summary/charts", exist_ok=True)
    file_path = f"Results/ChangeDensityMapping/Summary/charts/disaster_area_density_comparison_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.png"
    plt.savefig(file_path, dpi=350, bbox_inches="tight")
    print(f"Saved: {file_path}")

    plt.close()

    visualisation_file_path = f'visualisation-site/public/ChangeDensityMapping/Summary/charts/disaster_area_density_comparison_{pre_disaster_days}_{imm_disaster_days}_{post_disaster_days}.png'
    shutil.copyfile(file_path, visualisation_file_path)

def combine_plots_disaster_area_densities(disaster_ids, periods):
    # Paths for the 4 generated images
    image_paths = [
        f"Results/ChangeDensityMapping/Summary/charts/disaster_area_density_comparison_{pre}_{imm}_{post}.png"
        for pre, imm, post in periods
    ]

    # Verify that all image files exist
    image_paths = [img for img in image_paths if os.path.exists(img)]
    if len(image_paths) < 4:
        print(f"Warning: Only {len(image_paths)} images found, expected 4. Some plots may be missing.")
    
    # Load the images
    images = [mpimg.imread(img) for img in image_paths]

    # Create a 2x2 grid figure
    fig, axes = plt.subplots(2, 2, figsize=(24, 14))

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    # Plot each image in a subplot
    for i, img in enumerate(images):
        axes[i].imshow(img)
        axes[i].axis('off')  # Hide axes

    # Adjust layout and save
    plt.tight_layout()
    output_path = "Results/ChangeDensityMapping/Summary/charts/combined_disaster_area_densities.png"
    plt.savefig(output_path, dpi=350)
    print(f"Saved combined image: {output_path}")

    # Copy to visualization site
    visualisation_site_path = "visualisation-site/public/ChangeDensityMapping/Summary/charts/combined_disaster_area_densities.png"
    shutil.copyfile(output_path, visualisation_site_path)
    print(f"Copied to: {visualisation_site_path}")

    plt.close()

def plot_percent_difference_density(disaster_ids, disaster_ids_type):

    pre_df = pd.read_csv(
        "Results/ChangeDensityMapping/Summary/data/disaster_area_densities_365_0_0.csv"
    )[["disaster_id", "change_density"]].rename(columns={"change_density": "pre_density"})

    imm_df = pd.read_csv(
        "Results/ChangeDensityMapping/Summary/data/disaster_area_densities_0_60_0.csv"
    )[["disaster_id", "change_density"]].rename(columns={"change_density": "imm_density"})

    post_df = pd.read_csv(
        "Results/ChangeDensityMapping/Summary/data/disaster_area_densities_0_0_365.csv"
    )[["disaster_id", "change_density"]].rename(columns={"change_density": "post_density"})


    merged = pre_df.merge(imm_df, on="disaster_id", how="outer").merge(post_df, on="disaster_id", how="outer")


    merged = merged[merged["disaster_id"].isin(disaster_ids)]


    merged["sort_order"] = merged["disaster_id"].apply(lambda x: disaster_ids.index(x))
    merged.sort_values(by="sort_order", inplace=True)
    merged.drop(columns=["sort_order"], inplace=True) 


    merged["pre_imm_percent_diff"] = (
        (merged["imm_density"] - merged["pre_density"]) / merged["pre_density"] * 100
    )
    merged["pre_post_percent_diff"] = (
        (merged["post_density"] - merged["pre_density"]) / merged["pre_density"] * 100
    )


    disaster_labels = [
        f"{disaster_area[0]} ({disaster_date.year})"
        for disaster_id in disaster_ids
        for _, _, disaster_area, _, disaster_date, _, _ in [db_utils.get_disaster_with_id(disaster_id)]
    ]
    
     # Extract sorted lists for plotting
    x_labels = disaster_labels
    pre_imm_percent_diff = merged["pre_imm_percent_diff"].tolist()
    pre_post_percent_diff = merged["pre_post_percent_diff"].tolist()

    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 8))  # Wider figure to fit all labels

    x = range(len(x_labels))
    width = 0.4

    # Pre → Imm bars
    bars_pre_imm = ax.bar(
        [v - width/2 for v in x],
        pre_imm_percent_diff,
        width=width,
        color="dodgerblue",
        label="Pre → Imm"
    )

    # Pre → Post bars
    bars_pre_post = ax.bar(
        [v + width/2 for v in x],
        pre_post_percent_diff,
        width=width,
        color="orange",
        label="Pre → Post"
    )

    # Add bar labels
    for bar in bars_pre_imm:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f"{height:0.1f}%",
            ha='center', va='bottom', fontsize=8
        )

    for bar in bars_pre_post:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2,
            height,
            f"{height:0.1f}%",
            ha='center', va='bottom', fontsize=8
        )

    ax.set_yscale("symlog", linthresh=10)



    # Format plot
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels, rotation=90)
    ax.set_ylabel("Percent difference in density (%)")
    ax.set_title(f'Change in mapping density between Pre-Imm and Pre-Post disaster periods, sorted by {"region" if disaster_ids_type == "region" else "disaster type"}')
    ax.legend()


    # Add major and minor grid lines
    ax.grid(which='major', color='black', linestyle='--', linewidth=0.5)
    ax.grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
    ax.minorticks_on()  # Ensures minor grid lines appear

    plt.tight_layout()

    # Save plot
    output_dir = "Results/ChangeDensityMapping/Summary/charts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"Results/ChangeDensityMapping/Summary/charts/percent_difference_density_{disaster_ids_type}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved plot: {output_path}")

    # Copy to visualization site
    vis_path = f"visualisation-site/public/ChangeDensityMapping/Summary/charts/percent_difference_density_{disaster_ids_type}.png"
    shutil.copyfile(output_path, vis_path)

    # Show plot
    plt.show()
    plt.close()


if __name__ == "__main__":

    # Define the period lengths
    periods = [(365, 30, 365), (180, 30, 365), (365, 60, 335), ]
    #periods = [(1095, 30, 365)]
    periods = [(365,60,365),(365,0,0),(0,60,0),(0,0,365),]
    prophet_model_bools = [True, False]
    post_only_bools = [True, False]
    periods = [(365,60,365),(365,0,0),(0,60,0),(0,0,365),]
    compute_disaster_densities = False
    plot_disaster_densities_single_period = False
    plot_change_disaster_densities = True

    db_utils = DB_Utils()
    db_utils.db_connect()


    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17]
        print("Disaster IDs defined:", disaster_ids)

    if compute_disaster_densities:
        compute_disaster_areas(disaster_ids)
        for period in periods:
            print(f"Computing Densities for {period}")
            compute_disaster_area_densities(disaster_ids, period)

    if plot_disaster_densities_single_period:
        for period in periods:
            print(f"Computing Densities for {period}")
            plot_all_disaster_area_densities(disaster_ids, period)

        combine_plots_disaster_area_densities(disaster_ids, periods)

    if plot_change_disaster_densities:
        disaster_ids_region =   [3,8,7,5,6,9,14,13,10,11,12,2,18,15,16,17] # Geographic region
        disaster_ids_disaster = [3,6,11,5,12,17,8,9,13,2,15,16,10,7,18,14] # Disaster Type

        disaster_ids_types = ["type","region"] # "region", "type"

        exclude_derna = True
     

        for disaster_ids_type in disaster_ids_types:

            if disaster_ids_type == "region":
                disaster_ids = disaster_ids_region
            else:
                disaster_ids = disaster_ids_disaster

            if exclude_derna and 15 in disaster_ids:
                disaster_ids.remove(15)

            plot_percent_difference_density(disaster_ids, disaster_ids_type)


    
    

