#!/bin/bash

LOGFILE="Scripts/run-everything.log"
echo "\n\n" > "$LOGFILE"
exec > >(tee -a "$LOGFILE") 2>&1  # Redirect stdout and stderr to the log file

echo "Starting script execution at $(date)"
echo "==================================="

# Function to run a Python script and print its status
run_script() {
    script_path=$1
    echo "Running $script_path at $(date)"
    PYTHONUNBUFFERED=1 /Users/fabian/Documents/GitHub/osm-times-of-crisis/.venv/bin/python "$script_path"

    if [ $? -ne 0 ]; then
        echo "Script $script_path failed!"
    else
        echo "Script $script_path completed successfully."
    fi
    echo "----------------------------------"
}


# Double check data integrity 
#run_script "scripts/database/db_bulk_insert.py"
#run_script "scripts/database/db_prepare_change_differences.py"
#run_script "scripts/database/bulk_import_filtering.py"
#run_script "scripts/database/db_geojson_filtering.py"


# Lower level map count scripts
#run_script "scripts/research_tools/count_changes_lower/count_changes_lower.py"
#run_script "scripts/research_tools/count_changes_lower/generate_maps_count_changes.py"
#run_script "scripts/research_tools/count_changes_lower/percent_difference_lower.py"
#run_script "scripts/research_tools/count_changes_lower/generate_map_percent_difference.py"
#run_script "scripts/research_tools/count_changes_lower/analyse_gini_coefficient.py"


# Overall map count scripts
run_script "scripts/research_tools/count_changes/count_changes.py"
run_script "scripts/research_tools/count_changes/plot_count_changes.py"
run_script "scripts/research_tools/count_changes/percent_difference.py"
run_script scripts/"research_tools/count_changes/plot_percent_difference.py"


# RQ2 - Tags 
run_script "scripts/research_tools/investigate_tags/tag_key_investigation.py"
run_script "scripts/research_tools/investigate_tags/tag_value_investigation.py"
run_script "scripts/research_tools/investigate_tags/value_kendall_rank_correlation_coefficient.py"
run_script "scripts/research_tools/investigate_tags/plot_correlation_coefficient_diagram.py"

# RQ2 - Change Differences
run_script "scripts/research_tools/change_differences/analyse_change_differences.py"
run_script "scripts/research_tools/change_differences/timestamp_between_changes_prophet_modelling.py"