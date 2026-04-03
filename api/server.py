#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.macro_triangulation import MacroTriangulation
from engine.mobius import TriadicMobiusTransport, CANONICAL_MOS
from engine.model_adapter import call_model

app = FastAPI(title="Kadmon Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class KadmonSession:
    def __init__(self):
        self.tri = MacroTriangulation()
        self.running = False
    
    async def run_negotiation(self):
        self.running = True
        for round in range(20):
            if not self.running:
                break
                
            self.tri.execute_second_order(mode="COUPLE")
            alignment = self.tri.calculate_alignment()
            
            yield {
                "round": round,
                "user": [self.tri.user_point.x, self.tri.user_point.y, self.tri.user_point.z],
                "query": [self.tri.query_point.x, self.tri.query_point.y, self.tri.query_point.z],
                "ai": [self.tri.ai_resolved_point.x, self.tri.ai_resolved_point.y, self.tri.ai_resolved_point.z],
                "alignment_gap": alignment['alignment_gap_area'],
                "stability": alignment['mandelbulb_stability']
            }
            
            await asyncio.sleep(0.1)
        
        self.running = False

@app.websocket("/ws/negotiate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = KadmonSession()
    
    try:
        while True:
            data = await websocket.receive_text()
            params = json.loads(data)
            
            session.tri.set_query_position(params.get('x', -0.75), params.get('y', 0.0), params.get('z', 0.0))
            
            async for frame in session.run_negotiation():
                await websocket.send_text(json.dumps(frame))
                
    except Exception as e:
        session.running = False
        await websocket.close()

@app.get("/api/status")
def status():
    return {"status": "running", "version": "1.0"}
