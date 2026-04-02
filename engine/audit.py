import json
from datetime import datetime
import uuid

class AuditLog:
    def __init__(self):
        self.data = {
            "schema_version": "1.0",
            "run_id": str(uuid.uuid4()),
            "trace": []
        }

    def log(self, entry):
        entry["timestamp"] = datetime.utcnow().isoformat()
        self.data["trace"].append(entry)

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f, indent=2)
