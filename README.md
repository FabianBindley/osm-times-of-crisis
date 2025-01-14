# OSM During Times of Crisis Research
## Fabian Bindley, Supervised by Prof Licia Capra

## Data

To get data ready for use:
1)  Create a folder for the data in /Data
2) Download and paste in the .osh.pbg file for the area
3) Define a geocoded boundary for the area at https://geojson.io/
4) Extract the area using osmium extract and the defined geojson with:
```
osmium extract -p Data/{Place}/{Place}ManuallyDefined.geojson Data/{Place}/{place}-internal.osh.pbf -o  Data/{Place}/{Place}.osh.pbf -H --overwrite
```
5) Set up the Postgresql database running locally on your device
6) Import the data into the Postgresql database 
7) Start analysing!