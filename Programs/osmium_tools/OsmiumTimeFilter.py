import os
import subprocess
from osmium_tools.OsmiumExtract import OsmiumExtract

class OsmiumTimeFilter:
    def __init__(self):
        
        self.OsmiumExtract = OsmiumExtract()

    def run_filter(self, input_file, output_file, timestamp, geojson_file, with_history):
        """
        Runs the osmium time filter command to filter OSM data up to the specified timestamp.
        """
        command = [
            'osmium', 'time-filter',
            input_file,
            timestamp,
            '-o', output_file,
            '--overwrite'
        ]
        try:
            subprocess.run(command, check=True)
            print(f"Time filter applied successfully. Output saved to {output_file}.")
            print(f"Refiltering File based on Geojson provided")
            self.OsmiumExtract.run_extract(output_file, output_file, geojson_file, with_history)



        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running osmium time filter: {e}")

