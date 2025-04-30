# OSM During Times of Crisis


This project investigates crowd-worker mapping behaviour on [OpenStreetMap (OSM)](https://www.openstreetmap.org/) during natural disasters, focusing on changes in mapping frequency, content, and geographic distribution across pre, imm, and post-disaster periods.

---

## Project Structure

- `/Scripts/`: Python scripts for data processing, database insertion, and analysis
- `/Data/`: Input OSM data and GeoJSON boundaries
- `/Results/`: Computed results and visualisation charts
- `/visualisation-site/`: Frontend React dashboard for visualising results

---

## Dataset Preparation

### Prerequisites
To apply the methodologies used in this project, ensure the following tools are installed:
- [`osmium-tool`](https://osmcode.org/osmium-tool/) for processing `.osh.pbf` files.
- [PostgreSQL](https://www.postgresql.org/) with the [PostGIS](https://postgis.net/) extension for spatial data storage and analysis.

---

### 1. Set Up Data Folder  
Create a subfolder for each disaster under `/Data/` and place the corresponding `.osh.pbf` file (with full history) inside it.

### 2. Define Geographical Boundary  
Use [geojson.io](https://geojson.io/) to draw the boundary of the disaster-affected area. Export and save it as a `.geojson` file.

### 3. Extract Area Using `osmium`  
Run the following command to crop the dataset to your defined region:

```bash
osmium extract -p Data/{Place}/{Place}Boundary.geojson Data/{Place}/{place}-internal.osh.pbf \
-o Data/{Place}/{Place}.osh.pbf -H --overwrite
```

## 4. Filter for Nodes and Ways Only

To reduce file size and focus on meaningful edits, filter the `.osh.pbf` file to include only nodes and ways (skip relations):

```bash
osmium tags-filter Data/{Place}/{Place}.osh.pbf n/ w/ -o Data/{Place}/{Place}NodesWays.osh.pbf
```

## 5. Create changes and disasters database tables

Use the SQL schema files located in `/Scripts/database/schemas/` to create the required tables:

- `disasters`
- `changes`

## 6. Install Libraries

Install the required Python dependencies by running:

```bash
pip3 install -r Scripts/requirements.txt
```

## 7. Insert the Data

Run the bulk insert script to load processed OSM data into your database:

```bash
python3 Scripts/database/db_bulk_insert.py
```