import os
import random

try:
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

def call_model(prompt, seed=None):
    if VERTEX_AVAILABLE:
        project = os.environ.get('GCP_PROJECT_ID', 'true-artwork-479005-r3')
        location = os.environ.get('GCP_LOCATION', 'us-central1')
        
        vertexai.init(project=project, location=location)
        model = GenerativeModel("gemini-pro")
        
        generation_config = {}
        if seed is not None:
            generation_config['seed'] = seed
            
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    else:
        # Deterministic mock response
        if seed is not None:
            random.seed(seed)
        confidence = round(random.uniform(0.8, 0.99), 2)
        return f"[MOCK MODEL] confidence={confidence} response for: {prompt[:60]}..."
