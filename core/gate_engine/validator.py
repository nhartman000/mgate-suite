import json
import os
from jsonschema import validate

FORBIDDEN_ROOT_KEYS = {'project_name', 'metadata', 'notes'}

def has_bom(path):
    with open(path, 'rb') as f:
        return f.read(3) == b'\xef\xbb\xbf'

def load_json(path):
    if has_bom(path):
        raise ValueError(f"File has UTF-8 BOM: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_mg8(mg8):
    for key in mg8.keys():
        if key in FORBIDDEN_ROOT_KEYS:
            raise ValueError(f"Forbidden root key in MG8: {key}")
    
    for path_field in ['gitson', 'gst', 'qson']:
        if os.path.isabs(mg8[path_field]):
            raise ValueError(f"Absolute path not allowed: {path_field}={mg8[path_field]}")
        if mg8[path_field].startswith('/') or mg8[path_field].startswith('\\'):
            raise ValueError(f"Root path not allowed: {path_field}={mg8[path_field]}")

def validate_gate_contract(gates, gst):
    emits = set(gst['emits'])
    for gate in gates:
        expects = set(gate['expects'])
        if not expects.issubset(emits):
            missing = expects - emits
            raise ValueError(f"Gate {gate['gate_id']} expects missing fields: {missing}")

def validate_qson(qson):
    trace_ids = set()
    if not qson['events']:
        raise ValueError("QSON events array is empty")
    for event in qson['events']:
        if event['trace_id'] in trace_ids:
            raise ValueError(f"Duplicate trace_id: {event['trace_id']}")
        trace_ids.add(event['trace_id'])
        if event['trace_id'] == qson['run_trace_id']:
            raise ValueError(f"Event trace_id matches run_trace_id: {event['trace_id']}")

def validate_file(data, schema):
    validate(instance=data, schema=schema)
