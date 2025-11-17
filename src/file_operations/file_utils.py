from pathlib import Path
from datetime import datetime

def get_file_modification_date(file_path: Path) -> datetime:
    """ Get file modification date as datetime object. """
    return datetime.fromtimestamp(file_path.stat().st_mtime)

def get_unique_file_path(destination_folder: Path, filename: str) -> Path:
    """ Generate a unique file path by adding counter suffix if file exists. """
    destination_path = destination_folder / filename
    if not destination_path.exists():
        return destination_path
    
    stem   = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    
    while destination_path.exists():
        new_filename     = f"{stem}_{counter}{suffix}"
        destination_path = destination_folder / new_filename
        counter         += 1
    
    return destination_path

def ensure_directory_exists(directory_path: Path) -> bool:
    """ Ensure directory exists, creating it if necessary. """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False
