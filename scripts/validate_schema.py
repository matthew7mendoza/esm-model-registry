import sys
import yaml
from pathlib import Path

def validate_markup_file(file_path: Path) -> bool:
    """Validates a single markup file"""
    is_valid = True
    is_invalid = False
    if not file_path.exists():
        return is_invalid
    try:
        file_content = file_path.read_text()
    except OSError:
        return is_invalid
    except UnicodeDecodeError:
        return is_invalid
    try:
        data = yaml.safe_load(file_content)
    except yaml.YAMLError:
        return is_invalid
    is_invalid_dictionary = not isinstance(data, dict)
    if is_invalid_dictionary:
        return is_invalid
    return is_valid

def validate_directory(directory_path: Path) -> bool:
    """Validates all markup files in a directory"""
    is_valid = True
    is_invalid = False
    if not directory_path.exists():
        return is_invalid
    if not directory_path.is_dir():
        return is_invalid
    markup_files = list(directory_path.rglob("*.yaml"))
    validation_results = [validate_markup_file(path) for path in markup_files]
    has_errors = not all(validation_results)
    if has_errors:
        return is_invalid
    return is_valid

def main() -> None:
    """Entry point"""
    base_directory = Path(__file__).parent.parent
    components_directory = base_directory / "components"
    archetypes_directory = base_directory / "model_archetypes"
    tables_directory = base_directory / "tables" / "cmip6"
    valid_components = validate_directory(components_directory)
    if not valid_components:
        sys.exit(1)
    valid_archetypes = validate_directory(archetypes_directory)
    if not valid_archetypes:
        sys.exit(1)
    valid_tables = validate_directory(tables_directory)
    if not valid_tables:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
