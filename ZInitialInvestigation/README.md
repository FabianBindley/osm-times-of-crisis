# OpenStreetMap in times of Crisis
Fabian Bindley's COMP0138 Final Year Project investigating changes on Open Street Map (OSM) during times of crisis

## Tools Used
* Osmium - https://osmcode.org/osmium-tool/manual.html
* Pyosmium




### Using Osmium
Extract an area from a geocoded boundary:

Broxbourne:
```
osmium extract -p GeocodedBoundaries/broxbourne-boundary.osm DataDownloads/britain-and-ireland-latest.osm.pbf -o DataExtracts/osmium-broxbourne-boundary.osm --overwrite
```
Place with history:
```
osmium extract -p RawDataDownloads/GeocodedBoundaries/broxbourne-boundary.osm DataDownloads/great-britain-internal.osh.pbf -o DataExtracts/osmium-broxbourne-boundary-history.osm --overwrite --with-history
```

Time filter:
```
osmium time-filter DataExtracts/osmium-broxbourne-boundary-history.osm 2024-01-01T00:00:00Z -o DataExtracts/broxbourne-2024-01.osm
```
```
osmium time-filter DataDownloads/great-britain-internal.osh.pbf 2024-01-01T00:00:00Z -o DataExtracts/uk-2024-01.osm --overwrite
```

Tag filter:
```
osmium tags-filter DataExtracts/uk-2024-01.osm w/highway=trunk -o DataExtracts/uk-trunk-roads-2024-01.osm

```

## Extract from map with a geojson boundary
### Without history: Output file end in .osm



### With history: Output file end in .osh.pbf

osmium extract -p Data/GeocodedBoundaries/Broxbourne-geocode-boundary.geojson Data/Broxbourne/hertfordshire-internal.osh.pbf -o  Data/Broxbourne/Broxbourne.osh.pbf -H

osmium extract -p Data/GeocodedBoundaries/Emilia-Romagna-geocode-boundary.geojson Data/EmiliaRomagna/nord-est-internal.osh.pbf -o  Data/EmiliaRomagna/EmiliaRomagna.osh.pbf -H

### Filter at a specific time 
osmium time-filter Data/EmiliaRomagna/EmiliaRomagna.osh.pbf 2024-06-11T00:00:00Z -o Data/EmiliaRomagna/EmiliaRomagna-2024-06-11.osm.pbf

osmium time-filter Data/Broxbourne/Broxbourne.osh.pbf 2024-11-07T00:00:00Z -o Data/Broxbourne/Broxbourne-2024-11-07.osm


To get a reliable time extract - use initial extract, time filter, then extract again to get rid of stragglers


osmium extract -p Data/GeocodedBoundaries/Broxbourne-geocode-boundary.geojson Data/Broxbourne/Broxbourne.osh -o  Data/Broxbourne/BroxbourneAgain.osh -H


## To filter out relations
osmium tags-filter Data/EmiliaRomagna/EmiliaRomagna.osh.pbf n/ w/ -o Data/EmiliaRomagna/EmiliaRomagnaNodesWays.osh
osmium tags-filter Data/Broxbourne/Broxbourne.osh.pbf n/ w/ -o Data/EmiliaRomagna/BroxbourneNodesWays.osh

osmium cat Data/Broxbourne/Broxbourne.osh.pbf --object-type=node --object-type=way -o Data/Broxbourne/BroxbourneNodesWays.osh. --overwrite
osmium cat Data/UnitedKingdom/UnitedKingdom.osh.pbf --object-type=node --object-type=way -o Data/UnitedKingdom/UnitedKingdomNodesWays.osh.pbf --overwrite
osmium cat Data/Haiti/Haiti.osh.pbf --object-type=node --object-type=way -o Data/Haiti/HaitiNodesWays.osh.pbf --overwrite
osmium cat Data/EmiliaRomagna/EmiliaRomagna.osh.pbf --object-type=node --object-type=way -o Data/EmiliaRomagna/EmiliaRomagnaNodesWays.osh.pbf --overwrite
osmium cat Data/Nepal/Nepal.osh.pbf --object-type=node --object-type=way -o Data/Nepal/NepalNodesWays.osh.pbf --overwrite
