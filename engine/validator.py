import json
from jsonschema import validate

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_file(data, schema):
    validate(instance=data, schema=schema)
