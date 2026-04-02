import os
import json

def load_project(base_path, mg8_file):
    mg8_path = os.path.join(base_path, mg8_file)

    with open(mg8_path, "r") as f:
        mg8 = json.load(f)

    root = os.path.dirname(mg8_path)

    def resolve(p):
        return os.path.join(root, p)

    with open(resolve(mg8["gitson"])) as f:
        gitson = json.load(f)

    with open(resolve(mg8["gst"])) as f:
        gst = json.load(f)

    return mg8, gitson, gst, resolve(mg8["qson"])
