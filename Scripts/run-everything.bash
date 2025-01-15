#!/bin/bash

# Function to run a Python script and print its status
run_script() {
    script_path=$1
    echo "Running $script_path"
    /Users/fabian/Documents/GitHub/osm-times-of-crisis/.venv/bin/python  $script_path

    if [ $? -ne 0 ]; then
        echo "Script $script_path failed!"
    else
        echo "Script $script_path completed successfully."
    fi
    echo "----------------------------------"
}

# Lower level map count scripts
run_script "scripts/research_tools/count_changes_lower/count_changes_lower.py"
run_script "scripts/research_tools/count_changes_lower/generate_maps_count_changes.py"
run_script "scripts/research_tools/count_changes_lower/percent_difference_lower.py"
run_script "scripts/research_tools/count_changes_lower/generate_map_percent_difference.py"
run_script "scripts/research_tools/count_changes_lower/analyse_gini_coefficient.py"


# Overall map count scripts
run_script "scripts/research_tools/count_changes/count_changes.py"
run_script "scripts/research_tools/count_changes/plot_count_changes.py"
run_script "scripts/research_tools/count_changes/percent_difference.py"
run_script scripts/"research_tools/count_changes/plot_percent_difference.py"
