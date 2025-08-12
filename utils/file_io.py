import json

def write_file(path: str, text: dict) -> None:
    """
    Write a dictionary to a JSON file.
    
    Args:
        path (str): File path where to write the JSON data
        text (dict): Dictionary to write to the file
        
    Note:
        Silently handles exceptions and returns None on error.
        TODO: Add proper exception logging.
    """
    try:
        with open(path, 'w') as file:
            json.dump(text, file, indent = 4)
    except Exception as e:
        # EXCEPTION
        # TODO Add exception to log
        return 

def read_file(path: str) -> dict:
    """
    Read a JSON file and return its content as a dictionary.
    
    Args:
        path (str): File path to read from
        
    Returns:
        dict: Dictionary containing the JSON data, or empty dict on error
        
    Note:
        Silently handles exceptions and returns empty dict on error.
        TODO: Add proper exception logging.
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        # EXCEPTION
        # TODO Add exception to log
        return {}