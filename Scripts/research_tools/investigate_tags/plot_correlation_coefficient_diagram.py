import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil
import matplotlib.pyplot as plt
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'database')))

from db_utils import DB_Utils


def generate_plot_3d_correlation_diagram(period, disaster_ids):
    period1, period2 = period
    all_disasters = pd.read_csv(f"./Results/TagInvestigation/summary/key_correlation_rank_analysis.csv")
    all_disasters['disaster_id'] = 'all'

    disaster_data = []
    for disaster_id in disaster_ids:
        disaster_df = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/key_correlation_rank_analysis.csv")
        disaster_df['disaster_id'] = disaster_id  # Add the disaster ID
        disaster_data.append(disaster_df)

    # Combine all datasets into a single DataFrame
    combined_data = pd.concat([all_disasters] + disaster_data, ignore_index=True)
    columns = ['disaster_id'] + [col for col in combined_data.columns if col != 'disaster_id']
    combined_data = combined_data[columns]

    if period == ("pre","imm"):
        offset = 0
    elif period == ("pre","post"):
        offset = 1
    elif period == ("imm","post"):
        offset = 2
    

    df = pd.DataFrame(columns=["disaster_id", "disaster_title", "kendall_rank_correlation", "cosine_similarity", "pearson_correlation"])
    for i in range(0, len(combined_data), 3):

        row = combined_data.iloc[i+offset].copy()
        disaster_id = row['disaster_id']
        if disaster_id == "all":
            row['disaster_title'] = "All Disasters"
        else:
            (_, disaster_country, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
            row['disaster_title'] = f"{disaster_area[0]} {disaster_date.year}"
        df.loc[len(df)] = row

    print(df)
    


    fig = px.scatter_3d(
        df,
        x='kendall_rank_correlation',
        y='cosine_similarity',
        z='pearson_correlation',
        color='disaster_title',
        text='disaster_title',
        title=f"3D Plot of Correlation Coefficients for {period1}-{period2}",
        labels={'kendall_rank_correlation': 'Kendall Rank Correlation', 'cosine_similarity': 'Cosine Similarity', 'pearson_correlation': 'Pearson Correlation', 'disaster_title': 'Disaster'}
    )


    fig.update_traces(marker=dict(size=6, opacity=0.8, symbol='x'))

    # Save as interactive HTML
    fig.write_html(f"./Results/TagInvestigation/summary/3d_correlation_plot_{period1}_{period2}.html")
    fig.write_html(f"visualisation-site/public/TagInvestigation/summary/3d_correlation_plot_{period1}_{period2}.html")



def generate_plot_kendall_correlation_coefficients(periods, disaster_ids, key_pair):
    plt.figure(figsize=(10, 9))
    
    # Loop through periods and plot each on the same scatter plot
    for period in periods:
        period1, period2 = period
        all_disasters = pd.read_csv(f"./Results/TagInvestigation/summary/key_value_correlation_rank_analysis/{period1}_{period2}.csv")
        all_disasters = all_disasters[all_disasters["key"].isin(key_pair)]
        all_disasters['disaster_id'] = 'all'
        all_disasters['disaster_title'] = 'All disasters'

        disaster_data = []
        for disaster_id in disaster_ids:
            disaster_df = pd.read_csv(f"./Results/TagInvestigation/disaster{disaster_id}/key_value_correlation_rank_analysis/{period1}_{period2}.csv")
            disaster_df['disaster_id'] = disaster_id 

            (_, _, disaster_area, _, disaster_date, _ ) = db_utils.get_disaster_with_id(disaster_id)
            disaster_df['disaster_title'] = f"{disaster_area[0]} {disaster_date.year}"

            disaster_df = disaster_df[disaster_df["key"].isin(key_pair)]
            disaster_data.append(disaster_df)

        combined_data = pd.concat([all_disasters] + disaster_data, ignore_index=True)
        columns = ['disaster_id'] + [col for col in combined_data.columns if col != 'disaster_id']
        combined_data = combined_data[columns]

        # Extract data for keys
        key1_data = combined_data[combined_data["key"] == key_pair[0]]["kendall_rank_correlation"]
        key2_data = combined_data[combined_data["key"] == key_pair[1]]["kendall_rank_correlation"]

        # Plot scatter for the current period
        plt.scatter(
            key1_data,
            key2_data,
            alpha=0.7,
            label=f"{period1}-{period2}",
            s=50
        )

        # Add titles to each data point
        x = key1_data.values
        y = key2_data.values
        for i, label in enumerate(combined_data["disaster_title"].unique()):
            plt.text(x[i] + 0.05 * random.random(), y[i] + 0.02 * random.random(), label, fontsize=8, ha='right', alpha=0.7)

    # Customize plot
    plt.title(
        f"Kendall Rank Correlation for values of '{key_pair[0]}' and '{key_pair[1]}' keys across the different periods",
        fontsize=14
    )
    plt.xlabel(f"{key_pair[0]} Kendall Correlation", fontsize=12)
    plt.ylabel(f"{key_pair[1]} Kendall Correlation", fontsize=12)
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.5)
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.5)
    plt.grid(alpha=0.3)
    plt.axis('equal')
    plt.legend(title="Periods", fontsize=10)

    # Emergency has a negative value, and automatically checking the values seems to break the plot for some reason
    plt.xlim(-1 , 1)
    plt.ylim(-1 , 1)
    plt.tight_layout()


    file_path = f"./Results/TagInvestigation/summary/key_value_correlation_rank_analysis/kendall_rank_correlation_{key_pair[0]}_{key_pair[1]}.png"
    plt.savefig(file_path, dpi=350)
    visualisation_file_path = f"visualisation-site/public/TagInvestigation/summary/key_value_correlation_rank_analysis/kendall_rank_correlation_{key_pair[0]}_{key_pair[1]}.png"
    shutil.copyfile(file_path, visualisation_file_path)

    plt.close()
 


if __name__ == "__main__":
    db_utils = DB_Utils()
    db_utils.db_connect()
    disaster_ids = [7,8,9,10]

    # Key pairs should aways be alphabetically ordered
    specified_keys = sorted(["building","highway","source","name","surface","amenity","landuse","waterway","natural","leisure","emergency"])
    #specified_keys = sorted(["building","highway","emergency"])
    key_pairs=[]
    for i in range(len(specified_keys)-1):
        for j in range(i+1, len(specified_keys)):
            key_pairs.append((specified_keys[i], specified_keys[j]))
    

    print(key_pairs)
    periods = [("pre", "imm"), ("pre", "post"), ("imm", "post")]

    for key_pair in key_pairs:
        generate_plot_kendall_correlation_coefficients(periods, disaster_ids, key_pair)
        print(key_pair)


