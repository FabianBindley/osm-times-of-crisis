import sys
import ast
import os
from datetime import datetime, timedelta
from shapely import wkb
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
from shapely.geometry import mapping
from shapely.ops import transform
from PIL import Image
import io
import math
import folium

import h3
from collections import Counter
import csv
import pandas as pd
import numpy as np
from count_changes_lower import save_hex_counts_to_csv


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))
from db_utils import DB_Utils

def changes_for_interval(disaster_id, disaster_date, pre_disaster_days, imm_disaster_days, post_disaster_days, exclude_imm):
    pre_disaster = timedelta(pre_disaster_days)
    imm_disaster = timedelta(imm_disaster_days)
    post_disaster = timedelta(post_disaster_days)

    if exclude_imm:
        interval_start_date = disaster_date + imm_disaster
        interval_end_date = interval_start_date + post_disaster + timedelta(hours=1)
    else:
        interval_start_date = disaster_date - pre_disaster
        interval_end_date = disaster_date + imm_disaster + post_disaster + timedelta(hours=1)

    return db_utils.get_changes_in_interval(interval_start_date, interval_end_date, disaster_id)

def generate_counts_for_polygons_for_gini(changes, disaster_id, disaster_geojson_encoded, resolution, file_path):
    disaster_multipolygon = wkb.loads(disaster_geojson_encoded)

    hex_counts = {}
    # Convert the multipolygon to a LatLngPoly or LatLngMultiPoly
    polygons = []
    for geom in disaster_multipolygon.geoms:  # Handle each polygon in the MultiPolygon
        geojson_poly = mapping(geom)  # Convert Shapely geometry to GeoJSON
        # Reverse coordinates for the outer ring and holes
        outer = [(lat, lon) for lon, lat in geojson_poly['coordinates'][0]]
        holes = [[(lat, lon) for lon, lat in hole] for hole in geojson_poly['coordinates'][1:]]
        polygons.append(h3.LatLngPoly(outer, *holes))

    # Combine polygons into a LatLngMultiPoly if there are multiple
    if len(polygons) > 1:
        h3_shape = h3.LatLngMultiPoly(*polygons)
    else:
        h3_shape = polygons[0]

    # Get all hexagons that cover the multipolygon
    all_hexagons = h3.h3shape_to_cells(h3_shape, resolution)

    # Ensure all hexagons in the area are included, even with zero counts
    for hex_index in all_hexagons:
        hex_counts[hex_index] = [0,0,0,0]


    # Count the changes in the hexagons
    for change in changes:
        coords = list(wkb.loads(change[4]).coords)[0]
        lon, lat = coords[0], coords[1]

        if lon == 0 and lat == 0:
            continue
        
        # 0 for creates, 1 for edits, 2 for deletes
        # Get the H3 index of the hexagon and increment the count
        h3_index = h3.latlng_to_cell(lat, lon, resolution)

        # This adds the hexagons where changes were not in the area multipolygon. Useful to check that filtering is working
        # if h3_index not in hex_counts:
            #hex_counts[h3_index] = [0,0,0,0]

        if h3_index in hex_counts:

            edit_type = change[2]
            if edit_type == "create":
                hex_counts[h3_index][0] += 1
            elif edit_type == "edit":
                hex_counts[h3_index][1] += 1
            else:
                hex_counts[h3_index][2] += 1
            hex_counts[h3_index][3] += 1

     # Save the counts
    if not os.path.exists(f"Results/ChangeDensityMapping/disaster{disaster_id}/data"):
        os.makedirs(f"Results/ChangeDensityMapping/disaster{disaster_id}/data")

    save_hex_counts_to_csv(hex_counts, file_path)


def compute_gini_coefficients(hex_counts):
    # Assuming hex_counts is a DataFrame with columns 'creates', 'edits', 'deletes', 'total'
    cumulative_sum_counts_creates = np.cumsum(np.sort(hex_counts['create_count']))
    cumulative_sum_counts_edits = np.cumsum(np.sort(hex_counts['edit_count']))
    cumulative_sum_counts_deletes = np.cumsum(np.sort(hex_counts['delete_count']))
    cumulative_sum_counts_total = np.cumsum(np.sort(hex_counts['total_count']))

    n = len(hex_counts)

    if n == 0:
        return pd.DataFrame({
        "creates": [0],
        "edits": [0],
        "deletes": [0],
        "total": [0]
         })

    gini_index_counts_creates = (n + 1 - 2 * np.sum(cumulative_sum_counts_creates) / cumulative_sum_counts_creates[-1]) / n
    gini_index_counts_edits = (n + 1 - 2 * np.sum(cumulative_sum_counts_edits) / cumulative_sum_counts_edits[-1]) / n
    gini_index_counts_deletes = (n + 1 - 2 * np.sum(cumulative_sum_counts_deletes) / cumulative_sum_counts_deletes[-1]) / n
    gini_index_counts_total = (n + 1 - 2 * np.sum(cumulative_sum_counts_total) / cumulative_sum_counts_total[-1]) / n

    ginis = pd.DataFrame({
        "creates": [gini_index_counts_creates],
        "edits": [gini_index_counts_edits],
        "deletes": [gini_index_counts_deletes],
        "total": [gini_index_counts_total]
    })
    return ginis

# We assume that the pre and post csv files have already been generated, but the imm are not yet used - so we may generate them here
def get_count_gini_coefficients(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, resolution):

    file_path_pre = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/{pre_disaster_days}_0_0_{resolution}_hex_count.csv"
    if not os.path.exists(file_path_pre):
        print(f"Generating {pre_disaster_days} 0 0")
        changes = changes_for_interval(disaster_id, disaster_date, pre_disaster_days, 0, 0, exclude_imm=False)
        generate_counts_for_polygons_for_gini(changes, disaster_id, disaster_geojson_encoded, resolution, file_path_pre)

    file_path_imm = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/0_{imm_disaster_days}_0_{resolution}_hex_count.csv"
    if not os.path.exists(file_path_imm):
        print(f"Generating 0 {imm_disaster_days} 0")
        changes = changes_for_interval(disaster_id, disaster_date, 0, imm_disaster_days, 0, exclude_imm=False)
        generate_counts_for_polygons_for_gini(changes, disaster_id, disaster_geojson_encoded, resolution, file_path_imm)

    file_path_post = f"./Results/ChangeDensityMapping/disaster{disaster_id}/data/0_{imm_disaster_days}_{post_disaster_days}_{resolution}_post_only_hex_count.csv"
    if not os.path.exists(file_path_post):
        print(f"Generating 0 {imm_disaster_days} {post_disaster_days} post_only")
        changes = changes_for_interval(disaster_id, disaster_date, 0, imm_disaster_days, post_disaster_days, exclude_imm=True)
        generate_counts_for_polygons_for_gini(changes, disaster_id, disaster_geojson_encoded, resolution, file_path_post)


    hex_counts_pre= pd.read_csv(file_path_pre)
    hex_counts_imm = pd.read_csv(file_path_imm)
    hex_counts_post = pd.read_csv(file_path_post)

    gini_pre = compute_gini_coefficients(hex_counts_pre)
    gini_imm = compute_gini_coefficients(hex_counts_imm)
    gini_post = compute_gini_coefficients(hex_counts_post)

    return gini_pre, gini_imm, gini_post

def compute_percent_difference_in__count_ginis(gini_before, gini_after):
    percent_difference = (gini_after - gini_before) / gini_before * 100
    return percent_difference


def plot_gini_coefficients(gini_df, resolution):

    disaster_labels = gini_df.apply(
        lambda row: f"{row['disaster_area'][0]} ({row['disaster_date'].year})", axis=1
    )

    creates_pre = gini_df["gini_pre_creates"]
    edits_pre = gini_df["gini_pre_edits"]
    deletes_pre = gini_df["gini_pre_deletes"]
    total_pre = gini_df["gini_pre_total"]

    creates_imm = gini_df["gini_imm_creates"]
    edits_imm = gini_df["gini_imm_edits"]
    deletes_imm = gini_df["gini_imm_deletes"]
    total_imm = gini_df["gini_imm_total"]

    creates_post = gini_df["gini_post_creates"]
    edits_post = gini_df["gini_post_edits"]
    deletes_post = gini_df["gini_post_deletes"]
    total_post = gini_df["gini_post_total"]

    x = np.arange(len(disaster_labels))  
    width = 0.2  

    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

    for axis in axes:
        axis.grid(which='major', color='black', linestyle='-', linewidth=0.5)
        axis.grid(which='minor', color='gray', linestyle=':', linewidth=0.5)
        axis.minorticks_on()



    axes[0].bar(x - width*1.5, creates_pre, width, label="Creates", zorder=3)
    axes[0].bar(x - width/2, edits_pre, width, label="Edits", zorder=3)
    axes[0].bar(x + width/2, deletes_pre, width, label="Deletes", zorder=3)
    axes[0].bar(x + width*1.5, total_pre, width, label="Total", zorder=3)

    axes[0].set_ylabel("Gini Coefficient Pre-Disaster")
    axes[0].set_title("Gini Coefficients during Pre-Disaster Period")
    axes[0].tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False)



    axes[1].bar(x - width*1.5, creates_imm, width, label="Creates", zorder=3)
    axes[1].bar(x - width/2, edits_imm, width, label="Edits", zorder=3)
    axes[1].bar(x + width/2, deletes_imm, width, label="Deletes", zorder=3)
    axes[1].bar(x + width*1.5, total_imm, width, label="Total", zorder=3)

    axes[1].set_ylabel("Gini Coefficient Imm-Disaster")
    axes[1].set_title("Gini Coefficients during Immediate Period")
    axes[1].tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False)




    axes[2].bar(x - width*1.5, creates_post, width, label="Creates", zorder=3)
    axes[2].bar(x - width/2, edits_post, width, label="Edits", zorder=3)
    axes[2].bar(x + width/2, deletes_post, width, label="Deletes", zorder=3)
    axes[2].bar(x + width*1.5, total_post, width, label="Total", zorder=3)

    axes[2].set_ylabel("Gini Coefficient Post-Disaster")
    axes[2].set_title("Gini Coefficients during Post-Disaster Period")


    for axis in axes:
        axis.axhline(y=0, color='black', linewidth=0.8, linestyle='--')
        axis.set_yscale('linear') 
        axis.set_xticks(x)
        axis.set_xticklabels(disaster_labels, rotation=45)
        axis.legend()

    # Set a shared xlabel
    axes[1].set_xlabel("Disaster Area")

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f"./Results/ChangeDensityMapping/Summary/charts/gini_coefficients_pre_imm_post_{resolution}.png", dpi=350)
    plt.close()
    



def plot_percent_difference_in_gini_coefficients(gini_df, resolution, total_only, period, common_ylim=None):

    gini_df = gini_df[gini_df["resolution"] == resolution].copy()

    gini_df[f"gini_count_total_percent_difference_{period}"] = gini_df[f"gini_count_total_percent_difference_{period}"].fillna(0)

    gini_df = gini_df.sort_values(by=f"gini_count_total_percent_difference_{period}", ascending=False).reset_index(drop=True)

    disaster_labels = gini_df.apply(
        lambda row: f"{', '.join(row['disaster_area']) if isinstance(row['disaster_area'], list) else row['disaster_area']} ({row['disaster_date'].year})", axis=1
    )

    # Extract data for plotting
    if not total_only:
        creates_percent_difference= gini_df[f"gini_count_creates_percent_difference_{period}"]
        edits_percent_difference = gini_df[f"gini_count_edits_percent_difference_{period}"]
        deletes_percent_difference = gini_df[f"gini_count_deletes_percent_difference_{period}"]
    total_percent_difference = gini_df[f"gini_count_total_percent_difference_{period}"]

    x = np.arange(len(disaster_labels))

    # Start plotting
    width = 0.2
    #fig, axes = plt.subplots(2, 1, figsize=(12 if total_only else 18, 12), sharex=True)
    plt.figure(figsize=(12 if total_only else 18, 8))

    # Plot immediate differences
    if not total_only:
        plt.bar( x - width * 1.5, creates_percent_difference, width, label="Creates", color="blue", zorder=3)
        plt.bar( x - width / 2, edits_percent_difference, width, label="Edits", color="orange", zorder=3)
        plt.bar( x + width / 2, deletes_percent_difference, width, label="Deletes", color="green", zorder=3)
        plt.bar( x + width * 1.5, total_percent_difference, width, label="Total", color="red", zorder=3)
    else:
        plt.bar( x, total_percent_difference, width, label="Total", color="red", zorder=3)

    plt.ylabel(f"% Difference in Gini Coefficient ({period}-Disaster)")
    plt.title(f'% Difference in Gini Coefficients during {"Immediate" if period == "imm" else "Post"} Period | Resolution {resolution}')
    plt.legend()

    # Set x-axis labels and limits
    plt.xticks( x, disaster_labels, rotation=45)

    # Add both major and minor gridlines
    plt.grid(visible=True, which="major", linestyle="-", linewidth=0.8, color="black", zorder=0)
    plt.grid(visible=True, which="minor", linestyle=":", linewidth=0.5, color="gray", zorder=0)
    plt.minorticks_on()  # Enable minor ticks

    # Add a horizontal baseline at y=0
    plt.axhline(0, color="black", linewidth=0.8, linestyle="--", zorder=1)

    if common_ylim:
        plt.ylim(common_ylim)

    plt.tight_layout()


    plt.tight_layout()
    output_path = f"./Results/ChangeDensityMapping/Summary/charts/gini_percent_difference_{resolution}_{period}_{'total_only' if total_only else 'full'}.png"
    plt.savefig(output_path, dpi=300)

    os.makedirs('visualisation-site/public/ChangeDensityMapping/Summary/charts/', exist_ok=True)
    visualisation_site_path = f"visualisation-site/public/ChangeDensityMapping/Summary/charts/gini_percent_difference_{resolution}_{period}_{'total_only' if total_only else 'full'}.png"
    plt.savefig(visualisation_site_path, dpi=300)
    plt.close()

    return output_path

def combine_plots(image_path_1, image_path_2, output_path):
    """
    Combine two images (plots) into a single figure with subplots.

    Args:
        image_path_1 (str): Path to the first image.
        image_path_2 (str): Path to the second image.
        output_path (str): Path to save the combined figure.
    """
    # Load the images
    img1 = mpimg.imread(image_path_1)
    img2 = mpimg.imread(image_path_2)

    # Create a figure with two subplots
    if 'total_only' in output_path:
        fig, axes = plt.subplots(2, 1, figsize=(6, 8))
    else:
        fig, axes = plt.subplots(2, 1, figsize=(9, 8))
    # Display the first image
    axes[0].imshow(img1)
    axes[0].axis('off')  # Turn off axes for a cleaner look

    # Display the second image
    axes[1].imshow(img2)
    axes[1].axis('off')  # Turn off axes for a cleaner look

    # Adjust layout and save the combined figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

    visualisation_site_path = f"visualisation-site/public/ChangeDensityMapping/Summary/charts/gini_percent_difference_{resolution}_{'total_only' if total_only else ''}.png"
    plt.savefig(visualisation_site_path, dpi=300)
    plt.close()


# To analyse the gini coefficient - the changes per hexagon for the selected disasters must already have been completed and stored in the change_counts hex_coutn file for the specified resolution
if __name__ == "__main__":

    if len(sys.argv) > 1:
        disaster_ids = ast.literal_eval(sys.argv[1]) 
        print("Disaster IDs passed:", disaster_ids)
    else:
        disaster_ids = [2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
        # Res 9 ids
        #disaster_ids = [10,14,15,18]
        print("Disaster IDs defined:", disaster_ids)


    start_time = datetime.now()
    db_utils = DB_Utils()
    db_utils.db_connect()

    total_only_bools = [True, False]
    disaster_days = [(365, 60, 365)]
    resolutions = [7,8]
    gini_coefficients = []

    for disaster_day_tuple in disaster_days:
        for disaster_id in disaster_ids:
            for resolution in resolutions:
                (_, disaster_country, disaster_area, disaster_geojson_encoded, disaster_date, disaster_h3_resolution) = db_utils.get_disaster_with_id(disaster_id)
                pre_disaster_days, imm_disaster_days, post_disaster_days = disaster_day_tuple
                print(f"Computing gini coefficients for {disaster_area[0]} {disaster_date.year} | resolution {resolution}")

                gini_pre, gini_imm, gini_post = get_count_gini_coefficients(disaster_id, pre_disaster_days, imm_disaster_days, post_disaster_days, resolution)

                gini_count_percent_difference_imm = compute_percent_difference_in__count_ginis(gini_pre, gini_imm)
                gini_count_percent_difference_post = compute_percent_difference_in__count_ginis(gini_pre, gini_post)


                gini_coefficients.append({
                    "disaster_id": disaster_id,
                    "disaster_country": disaster_country,
                    "disaster_area": disaster_area,
                    "disaster_date": disaster_date,
                    "resolution": resolution,
                    "gini_pre_creates": gini_pre["creates"].values[0],
                    "gini_pre_edits": gini_pre["edits"].values[0],
                    "gini_pre_deletes": gini_pre["deletes"].values[0],
                    "gini_pre_total": gini_pre["total"].values[0],
                    "gini_imm_creates": gini_imm["creates"].values[0],
                    "gini_imm_edits": gini_imm["edits"].values[0],
                    "gini_imm_deletes": gini_imm["deletes"].values[0],
                    "gini_imm_total": gini_imm["total"].values[0],
                    "gini_post_creates": gini_post["creates"].values[0],
                    "gini_post_edits": gini_post["edits"].values[0],
                    "gini_post_deletes": gini_post["deletes"].values[0],
                    "gini_post_total": gini_post["total"].values[0],
                    "gini_count_creates_percent_difference_imm": gini_count_percent_difference_imm["creates"].values[0],
                    "gini_count_edits_percent_difference_imm": gini_count_percent_difference_imm["edits"].values[0],
                    "gini_count_deletes_percent_difference_imm": gini_count_percent_difference_imm["deletes"].values[0],
                    "gini_count_total_percent_difference_imm": gini_count_percent_difference_imm["total"].values[0],
                    "gini_count_creates_percent_difference_post": gini_count_percent_difference_post["creates"].values[0],
                    "gini_count_edits_percent_difference_post": gini_count_percent_difference_post["edits"].values[0],
                    "gini_count_deletes_percent_difference_post": gini_count_percent_difference_post["deletes"].values[0],
                    "gini_count_total_percent_difference_post": gini_count_percent_difference_post["total"].values[0],
                })

    gini_df = pd.DataFrame(gini_coefficients)
    #print(gini_df)
    gini_df.to_csv("./Results/ChangeDensityMapping/Summary/data/gini_coefficients.csv", index=False)

    for resolution in resolutions:
        for total_only in total_only_bools:

            # Calculate common y-axis limits
            imm_values = gini_df[f"gini_count_total_percent_difference_imm"].fillna(0)
            post_values = gini_df[f"gini_count_total_percent_difference_post"].fillna(0)

            # Compute the minimum and maximum values across both periods
            ymin = min(imm_values.min(), post_values.min())
            ymax = max(imm_values.max(), post_values.max())

            # Add padding to the y-axis range
            padding = 5  # Adjust padding as needed
            common_ylim = (ymin - padding, ymax + padding)

            #plot_gini_coefficients(gini_df, resolution)
            #plot_percent_difference_in_gini_coefficients(gini_df, resolution, total_only=False)
            imm_path = plot_percent_difference_in_gini_coefficients(gini_df, resolution, total_only, period="imm", common_ylim=common_ylim)
            post_path = plot_percent_difference_in_gini_coefficients(gini_df, resolution, total_only, period="post",  common_ylim=common_ylim)
            output_path = f"./Results/ChangeDensityMapping/Summary/charts/gini_percent_difference_{resolution}_{'total_only' if total_only else ''}.png"
            combine_plots(imm_path, post_path, output_path)