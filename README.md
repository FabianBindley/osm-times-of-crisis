# OSM During Times of Crisis Research
## Fabian Bindley, Supervised by Prof Licia Capra

## Data

To get data ready for use:
1)  Create a folder for the data in /Data
2) Download and paste in the .osh.pbf file for the area
3) Define a geocoded boundary for the area at https://geojson.io/
4) Extract the area using osmium extract and the defined geojson with:
```
osmium extract -p Data/{Place}/{Place}ManuallyDefined.geojson Data/{Place}/{place}-internal.osh.pbf -o  Data/{Place}/{Place}.osh.pbf -H --overwrite
eg: osmium extract -p Data/California/CaliforniaTop10Boundaries.geojson Data/California/california-internal.osh.pbf -o  Data/California/California.osh.pbf -H --overwrite

osmium extract -p Data/Freetown/FreetownManuallyDefined.geojson Data/Freetown/sierra-leone-internal.osh.pbf -o  Data/Freetown/Freetown.osh.pbf -H --overwrite
```
5) Extract only the nodes and ways
```
osmium tags-filter Data/{place}/{place}.osh.pbf n/ w/ -o Data/{place}/{place}NodesWays.osh.pbf
eg: osmium tags-filter Data/Texas/Texas.osh.pbf n/ w/ -o Data/Texas/TexasNodesWays.osh.pbf
```

6) Set up the Postgresql database running locally on your device
6) Create changes and disaster tables according to their schemas
6) Import the data into the Postgresql database by running the db_bulk_insert.py script
7) Start analysing!!


To combine 2 osh files:
osmium merge input_file1.osm input_file2.osm -o output_combined.osm
osmium merge Data/TurkeySyia/syria-internal.osh.pbf Data/TurkeySyia/turkey-internal.osh.pbf -o Data/TurkeySyia/TurkeySyriaMerge.osh.pbf --with-history --overwrite