import os
import sys
import requests
import yaml
from pathlib import Path
from typing import List

INTERFACE_ADDRESS = os.environ.get(
    "CLIMATE_MODEL_INTERCOMPARISON_PROJECT_API_URL",
    "https://api.github.com/repos/PCMDI/cmip6-cmor-tables/contents/Tables",
)
RAW_ADDRESS = os.environ.get(
    "CLIMATE_MODEL_INTERCOMPARISON_PROJECT_RAW_URL",
    "https://raw.githubusercontent.com/PCMDI/cmip6-cmor-tables/master/Tables/",
)
OUTPUT_DIRECTORY = "tables/cmip6"

def retrieve_live_table_list() -> List[str]:
    """Queries the remote registry to find all table files"""
    empty_list = []
    try:
        response = requests.get(INTERFACE_ADDRESS, timeout=15)
    except requests.exceptions.RequestException:
        return empty_list
    
    if response.status_code != 200:
        return empty_list
    
    try:
        all_files_list = response.json()
    except ValueError:
        return empty_list
    
    return [
        file_information["name"]
        for file_information in all_files_list
        if file_information["name"].endswith(".json")
        and not file_information["name"].startswith("CMIP6_CV")
    ]

def process_single_table(javascript_object_notation_filename: str) -> None:
    """Process a single table"""
    full_address = f"{RAW_ADDRESS}{javascript_object_notation_filename}"
    try:
        response = requests.get(full_address, timeout=15)
    except requests.exceptions.RequestException:
        return
    
    if response.status_code != 200:
        return
    
    try:
        raw_table_dictionary = response.json()
    except ValueError:
        return
    
    parsed_variables_dictionary = raw_table_dictionary.get("variable_entry", {})
    if not parsed_variables_dictionary:
        return
    
    target_filename = javascript_object_notation_filename.replace(".json", ".yaml")
    output_file_path = os.path.join(OUTPUT_DIRECTORY, target_filename)
    try:
        yaml_content = yaml.dump(parsed_variables_dictionary)
    except yaml.YAMLError:
        return
    
    try:
        Path(output_file_path).write_text(yaml_content, encoding="utf-8")
    except OSError:
        return

def main() -> None:
    """Main execution"""
    live_tables_list = retrieve_live_table_list()
    if not live_tables_list:
        sys.exit(1)
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    for javascript_object_notation_filename in live_tables_list:
        process_single_table(javascript_object_notation_filename)

if __name__ == "__main__":
    main()