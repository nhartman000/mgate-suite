#!/usr/bin/env python3
import json
import os
import glob
from typing import List, Dict, Any

class QSONDatasetParser:
    """Parse QSON audit logs into ML training vectors"""
    
    def __init__(self, qson_directory: str):
        self.qson_dir = qson_directory
        self.samples = []
        
    def parse_all(self) -> List[Dict[str, Any]]:
        """Parse all QSON files in directory"""
        for qson_path in glob.glob(os.path.join(self.qson_dir, "*.qson")):
            sample = self.parse_single(qson_path)
            if sample:
                self.samples.append(sample)
        return self.samples
    
    def parse_single(self, qson_path: str) -> Dict[str, Any]:
        """Parse single QSON file into training sample"""
        with open(qson_path, 'r') as f:
            qson = json.load(f)
            
        # Extract trajectory sequence
        trajectory = []
        for event in qson['events']:
            if 'kadmon' in event:
                point = complex(event['kadmon']['problem_position'])
                trajectory.append({
                    "round": event['kadmon']['round'],
                    "x": point.real,
                    "y": point.imag,
                    "stability": event['kadmon']['mathematical'],
                    "confidence": event['confidence_at_decision']
                })
        
        if not trajectory:
            return None
            
        final_point = trajectory[-1]
        
        return {
            "run_trace_id": qson['run_trace_id'],
            "context_ref": qson['context_ref'],
            "model": qson['model'],
            "total_rounds": len(trajectory),
            "final_x": final_point['x'],
            "final_y": final_point['y'],
            "final_stability": final_point['stability'],
            "trajectory": trajectory,
            "converged": final_point['stability'] > 0.75,
            "distance_to_anchor": abs(complex(final_point['x'], final_point['y']) - complex(-0.500003, 0.0))
        }
    
    def export_csv(self, output_path: str):
        """Export parsed dataset to CSV"""
        import csv
        
        fieldnames = [
            "run_trace_id", "context_ref", "model", "total_rounds",
            "final_x", "final_y", "final_stability", "converged",
            "distance_to_anchor"
        ]
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for sample in self.samples:
                writer.writerow({k: v for k, v in sample.items() if k in fieldnames})


if __name__ == "__main__":
    parser = QSONDatasetParser("examples/out/")
    samples = parser.parse_all()
    print(f"Parsed {len(samples)} valid QSON samples")
    parser.export_csv("training/dataset.csv")
    print(f"Dataset exported to training/dataset.csv")
