mgate-suite/
├── spec/
│   ├── mg8.schema.json
│   ├── gitson.schema.json
│   ├── gst.schema.json
│   ├── qson.schema.json
│   └── zipson.schema.json
│
├── engine/
│   ├── loader.py
│   ├── validator.py
│   ├── executor.py
│   ├── audit.py
│   └── model_adapter.py
│
├── cli/
│   └── run_project.py
│
└── requirements.txt


pip install -r requirements.txt

python cli/run_project.py ./example project.mg8
