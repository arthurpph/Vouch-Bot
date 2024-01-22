import os
import json


def load_config(file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file)

    with open(file_path, 'r') as f:
        configuration = json.load(f)
    return configuration


config = load_config('config.json')
