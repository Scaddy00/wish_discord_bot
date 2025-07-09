import json

# Write File
def write_file(path: str, text: dict) -> None:
    try:
        with open(path, 'w') as file:
            json.dump(text, file, indent = 4)
    except Exception as e:
        # EXCEPTION
        # TODO Add exception in log
        return 

# Rad File
def read_file(path: str) -> dict:
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except Exception as e:
        # EXCEPTION
        # TODO Add exception in log
        return {}