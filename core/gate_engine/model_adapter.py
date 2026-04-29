import os
import random

try:
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

def call_model(prompt, model_name="gemini-3-flash-preview", seed=None):
    if not VERTEX_AVAILABLE:
        raise ImportError("Vertex AI SDK is not installed or available. Real live model execution requires vertexai.")

    project = os.environ.get('GCP_PROJECT_ID', 'true-artwork-479005-r3')
    location = os.environ.get('GCP_LOCATION', 'us-central1')
    
    vertexai.init(project=project, location=location)
    
    # Utilizing the production model variant dynamically
    model = GenerativeModel(model_name)
    
    generation_config = {}
    if seed is not None:
        generation_config['seed'] = seed
        
    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        raise RuntimeError(f"Live model execution failed: {e}\nEnsure you have active credentials by running 'gcloud auth application-default login'.")
