import subprocess
import os
import time

class OsmiumExtract:
    def __init__(self):
        pass
    
    def run_extract(self, input_file, output_file, geojson_file, with_history):
        """
        Runs the osmium extract command to extract the given area.
        """
        input_file_name = input_file
        time.sleep(1)
        # If input and output files are the same, create a renamed input file with '-extract' before the file extension.
        if input_file == output_file:
            input_file_name_split = input_file.rsplit('.', 1)
            input_file_name = f"{input_file_name_split[0]}-extract.{input_file_name_split[1]}"
            os.rename(input_file, input_file_name)  # Rename the file

        command = [
            'osmium', 'extract', '-p',
            geojson_file,
            input_file_name,
            '-o', output_file,
            '--overwrite'
        ]
        if with_history:
            command.append('--with-history')

        try:
            subprocess.run(command, check=True)
            print(f"Extract Applied - Output saved to {output_file}.")       

            if input_file == output_file:
                os.remove(input_file_name) 
                print("Deleted temp extract file")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running osmium extract: {e}")