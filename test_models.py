import vertexai
from vertexai.preview.generative_models import GenerativeModel
import os

project = os.environ.get('GCP_PROJECT_ID', 'true-artwork-479005-r3')
location = os.environ.get('GCP_LOCATION', 'us-central1')
vertexai.init(project=project, location=location)

models_to_test = [
    "gemini-3.0-flash-preview",
    "gemini-3-flash-preview",
    "gemini-3-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-preview",
    "gemini-1.5-pro",
    "gemini-pro"
]

for m in models_to_test:
    try:
        model = GenerativeModel(m)
        resp = model.generate_content("hello")
        print(f"SUCCESS: {m}")
        break
    except Exception as e:
        print(f"FAILED: {m} - ERROR: {e}")
