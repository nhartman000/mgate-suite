import sys
from engine.loader import load_project
from engine.executor import Executor
from engine.audit import AuditLog

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_project.py <base_path> <mg8_file>")
        return

    base_path = sys.argv[1]
    mg8_file = sys.argv[2]

    mg8, gitson, gst, qson_path = load_project(base_path, mg8_file)

    audit = AuditLog()
    executor = Executor(gitson, audit)

    user_input = input("INPUT: ")

    result = executor.run(mg8["entry_gate"], user_input)

    print("\nOUTPUT:\n", result)

    audit.save(qson_path)
    print("\nAudit saved:", qson_path)

if __name__ == "__main__":
    main()
