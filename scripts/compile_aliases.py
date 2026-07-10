import json
import yaml
from pathlib import Path

UPSTREAM_DIRECTORY = Path("tables/cmip6")
OUTPUT_FILE = Path("compiled_aliases.json")

def extract_aliases_from_file(file_path: Path) -> dict:
    """Reads a single file and returns a flat mapping"""
    empty_dictionary = {}
    if not file_path.exists():
        return empty_dictionary
    try:
        file_content = file_path.read_text()
    except OSError:
        return empty_dictionary
    try:
        data = yaml.safe_load(file_content)
    except yaml.YAMLError:
        return empty_dictionary
    if not data:
        return empty_dictionary
    variables = data.get("variable_entry", {})
    return {
        variable_name.lower().strip(): variable_name 
        for variable_name in variables
    }

def save_compiled_aliases(flat_mapping: dict) -> None:
    """Handles writing the final alias map"""
    if not flat_mapping:
        return
    try:
        content = json.dumps(flat_mapping, indent=4)
    except TypeError:
        return
    try:
        OUTPUT_FILE.write_text(content)
    except OSError:
        return

def main() -> None:
    """Entry point"""
    if not UPSTREAM_DIRECTORY.exists():
        return
    flat_mapping = {}
    for file_path in UPSTREAM_DIRECTORY.glob("*.yaml"):
        file_aliases = extract_aliases_from_file(file_path)
        flat_mapping.update(file_aliases)
    save_compiled_aliases(flat_mapping)

if __name__ == "__main__":
    main()