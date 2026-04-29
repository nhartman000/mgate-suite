#!/usr/bin/env python3
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.environment import KadmonEnvironment

def batch_run(prompt_list: list, output_dir: str = "examples/out/"):
    """Run batch negotiation jobs to generate training dataset"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    env = KadmonEnvironment()
    env.start()
    
    print(f"Starting batch run with {len(prompt_list)} prompts")
    print(f"Environment ID: {env.environment_id}")
    
    results = []
    
    for i, prompt in enumerate(prompt_list):
        print(f"\nRunning prompt {i+1}/{len(prompt_list)}: {prompt[:50}...")
        
        pair = env.create_pair("gemini-pro", "gemini-pro")
        result = env.run_negotiation(pair)
        
        results.append(result)
        
        if result['consensus']:
            print(f"  ✓ Consensus reached in {result['rounds']} rounds")
            print(f"  Agreed position: {result['agreed_position']}")
        else:
            print(f"  ✗ No consensus after {result['rounds']} rounds")
    
    env.shutdown()
    
    print(f"\nBatch complete. {sum(1 for r in results if r['consensus'])} / {len(results)} converged.")
    print(f"All QSON logs written to {output_dir}")
    
    return results


if __name__ == "__main__":
    # Example prompt dataset - replace with actual problem set
    test_prompts = [
        "Explain photosynthesis",
        "What is gravity?",
        "How does evolution work?",
        "Define entropy",
        "Explain quantum entanglement"
    ]
    
    batch_run(test_prompts)
