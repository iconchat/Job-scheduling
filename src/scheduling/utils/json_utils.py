import json
import os
from pathlib import Path
from typing import Any, Dict, Union

def get_project_root() -> Path:
    """Returns the project root directory."""
    return Path(__file__).parent.parent

def get_data_dir() -> Path:
    """Returns the path to the data directory."""
    return get_project_root() / "data"

def load_json_file(filename: str) -> Dict[str, Any]:
    """
    Loads a JSON file from the data directory.
    
    Args:
        filename (str): Name of the JSON file (with or without .json extension)
        
    Returns:
        Dict[str, Any]: The loaded JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    current_dir = Path(__file__).parent.parent
    data_dir = current_dir / "data"
    file_path = data_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file '{filename}' not found in data directory: {data_dir}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file '{filename}': {str(e)}", e.doc, e.pos)

def save_json_file(data: Dict[str, Any], filename: str) -> None:
    """
    Saves data to a JSON file in the data directory.
    
    Args:
        data (Dict[str, Any]): The data to save
        filename (str): Name of the JSON file (with or without .json extension)
        
    Raises:
        IOError: If there's an error writing the file
    """
    if not filename.endswith('.json'):
        filename += '.json'
    
    file_path = get_data_dir() / filename
    
    # Ensure the data directory exists
    os.makedirs(get_data_dir(), exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise IOError(f"Error writing to file '{filename}': {str(e)}")
