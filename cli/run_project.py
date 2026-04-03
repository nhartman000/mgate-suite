#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.loader import load_project
from engine.validator import validate_mg8, validate_gate_contract
from engine.audit import AuditLog
from engine.executor import Executor

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/project.mg8>")
        sys.exit(1)
    
    mg8_path = sys.argv[1]
    
    try:
        print(f"Loading MG8: {mg8_path}")
        project = load_project(mg8_path)
        
        print("Validating project...")
        validate_mg8(project.mg8)
        validate_gate_contract(project.gitson['gates'], project.gst)
        
        print("Initializing audit log...")
        audit = AuditLog(
            context_ref=project.gst['context_id'],
            model=project.mg8['model']
        )
        
        print(f"Run trace ID: {audit.run_trace_id}")
        
        print("Executing DAG...")
        executor = Executor(project, audit)
        result = executor.run()
        
        print(f"Writing QSON to: {project.qson_path}")
        audit.save(project.qson_path)
        
        print(f"Execution complete. {len(result['events'])} events logged.")
        print(f"QSON written successfully.")
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
