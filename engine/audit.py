import json
from datetime import datetime
import uuid

class AuditLog:
    def __init__(self, context_ref, model):
        self.run_trace_id = f"RUN_{str(uuid.uuid4())}"
        self.data = {
            "schema_version": "1.0",
            "run_trace_id": self.run_trace_id,
            "context_ref": context_ref,
            "model": model,
            "responses": [],
            "events": []
        }

    def log_event(self, event):
        event["timestamp"] = datetime.utcnow().isoformat().replace('+00:00', 'Z')
        if event.get('parent_trace_ids') is None:
            del event['parent_trace_ids']
        self.data["events"].append(event)

    def save(self, path):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
