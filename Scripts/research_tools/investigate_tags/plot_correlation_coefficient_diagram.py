import plotly.express as px
import pandas as pd
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import csv
import shutil

from scipy.stats import kendalltau, pearsonr
from sklearn.metrics.pairwise import cosine_similarity

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
    

if __name__ == "__main__":
    db_utils = DB_Utils()
    db_utils.db_connect()
    disaster_ids =  [2,3,4,5,6]

    periods = [("pre","imm"), ("pre","post"), ("imm","post")]
    for period in periods:
        generate_plot_3d_correlation_diagram(period, disaster_ids)

