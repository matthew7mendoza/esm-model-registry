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

def get_expected_prefix() -> str:
    """Derives expected table prefix from output directory"""
    directory_name = Path(OUTPUT_DIRECTORY).name
    return f"{directory_name.upper()}_"

def retrieve_live_table_list(expected_prefix: str) -> List[str]:
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
    
    controlled_vocab_prefix = f"{expected_prefix}CV"
    return [
        info["name"]
        for info in all_files_list
        if info["name"].endswith(".json")
        and not info["name"].startswith(controlled_vocab_prefix)
    ]

def remove_file_if_standard(file_path: Path) -> None:
    """Safely removes standard table file"""
    is_override = file_path.name == "local_overrides.yaml"
    if is_override:
        return
    try:
        file_path.unlink()
    except OSError:
        return

def clean_output_directory() -> None:
    """Removes existing table files to prevent orphaned duplicates"""
    directory = Path(OUTPUT_DIRECTORY)
    if not directory.exists():
        return
    for file_path in directory.glob("*.yaml"):
        remove_file_if_standard(file_path)

def process_single_table(javascript_object_notation_filename: str, expected_prefix: str) -> None:
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
    
    clean_name = javascript_object_notation_filename
    has_prefix = clean_name.startswith(expected_prefix)
    if has_prefix:
        prefix_length = len(expected_prefix)
        clean_name = clean_name[prefix_length:]
        
    target_filename = clean_name.replace(".json", ".yaml")
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
    expected_prefix = get_expected_prefix()
    live_tables_list = retrieve_live_table_list(expected_prefix)
    if not live_tables_list:
        sys.exit(1)
        
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    clean_output_directory()
    
    for filename in live_tables_list:
        process_single_table(filename, expected_prefix)

if __name__ == "__main__":
    main()