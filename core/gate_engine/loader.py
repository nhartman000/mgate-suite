import os
import json


class MGateProject:
    def __init__(self, mg8, gitson, gst, qson_path, base_dir, mg8_rel_path, gitson_rel_path, gst_rel_path):
        self.mg8 = mg8
        self.gitson = gitson
        self.gst = gst
        self.qson_path = qson_path
        self.base_dir = base_dir
        self.mg8_rel_path = mg8_rel_path
        self.gitson_rel_path = gitson_rel_path
        self.gst_rel_path = gst_rel_path


def _resolve_path(base_path, file_name):
    """
    Deterministic path resolver.
    """
    full_path = os.path.abspath(os.path.join(base_path, file_name))

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"[MGATE] Missing file: {full_path}")

    return full_path


def _read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_project(mg8_path):
    """
    Loads full MGATE project from MG8 file path:
    Resolves gitson, gst paths relative to MG8 location
    """
    mg8_path = os.path.abspath(mg8_path)
    base_dir = os.path.dirname(mg8_path)
    
    # Load MG8
    mg8 = _read_json(mg8_path)
    
    # Resolve relative paths from MG8 location
    gitson_path = os.path.abspath(os.path.join(base_dir, mg8['gitson']))
    gst_path = os.path.abspath(os.path.join(base_dir, mg8['gst']))
    qson_path = os.path.abspath(os.path.join(base_dir, mg8['qson']))
    
    if not os.path.exists(gitson_path):
        raise FileNotFoundError(f"[MGATE] Missing gitson: {gitson_path}")
    if not os.path.exists(gst_path):
        raise FileNotFoundError(f"[MGATE] Missing gst: {gst_path}")
    
    # Load content
    gitson = _read_json(gitson_path)
    gst = _read_json(gst_path)
    
    # Return structured object
    return MGateProject(
        mg8=mg8,
        gitson=gitson,
        gst=gst,
        qson_path=qson_path,
        base_dir=base_dir,
        mg8_rel_path=os.path.basename(mg8_path),
        gitson_rel_path=mg8['gitson'],
        gst_rel_path=mg8['gst']
    )