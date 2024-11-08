from osmium_tools.OsmiumTimeFilter import OsmiumTimeFilter
# Example usage
if __name__ == "__main__":
    # Replace these with your actual file paths and timestamp
    timestamp = "2024-06-01T00:00:00Z"
    input_file = "Data/Broxbourne/Broxbourne.osh.pbf"
    output_file = f"Data/Broxbourne/Broxbourne-{timestamp[:10]}.osm"
    geojson_file = "Data/GeocodedBoundaries/Broxbourne-geocode-boundary.geojson"

    osmium_filter = OsmiumTimeFilter()
    osmium_filter.run_filter(input_file, output_file, timestamp, geojson_file, with_history=False)