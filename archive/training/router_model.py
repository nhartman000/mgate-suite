#!/usr/bin/env python3
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class KadmonRouter(nn.Module):
    """
    Trained router model that predicts optimal Mandelbrot coordinate
    for a given problem embedding
    """
    
    def __init__(self, input_dim=768, hidden_dim=256):
        super().__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Linear(hidden_dim//2, 2)  # Output: (x, y) coordinate
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=1e-4)
        self.criterion = nn.MSELoss()
        
    def forward(self, x):
        return self.network(x)
    
    def predict_coordinate(self, prompt_embedding):
        """Predict optimal stability coordinate for prompt"""
        with torch.no_grad():
            xy = self.forward(prompt_embedding)
            x, y = xy[0].item(), xy[1].item()
            return complex(x, y)
    
    def train_step(self, prompt_embeddings, target_coordinates):
        self.train()
        self.optimizer.zero_grad()
        
        predictions = self.forward(prompt_embeddings)
        loss = self.criterion(predictions, target_coordinates)
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item()


def train_router(dataset_path: str, epochs: int = 100):
    """Train router from collected QSON dataset"""
    import pandas as pd
    
    df = pd.read_csv(dataset_path)
    
    # Filter for successful converged runs
    converged = df[df['converged'] == True]
    print(f"Training on {len(converged)} converged samples")
    
    # For demo: generate random embeddings (replace with actual LLM embeddings)
    embeddings = torch.randn(len(converged), 768)
    targets = torch.tensor(converged[['final_x', 'final_y']].values, dtype=torch.float32)
    
    model = KadmonRouter()
    
    for epoch in range(epochs):
        loss = model.train_step(embeddings, targets)
        if epoch % 10 == 0:
            print(f"Epoch {epoch:3d} | Loss: {loss:.6f}")
    
    torch.save(model.state_dict(), "training/router_model.pt")
    print("Router model saved to training/router_model.pt")


if __name__ == "__main__":
    train_router("training/dataset.csv")
