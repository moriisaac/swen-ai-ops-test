#!/usr/bin/env python3
"""
SWEN Cloud Intelligence Console - API
FastAPI backend for real-time telemetry and AI decision visualization
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import logging
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SWEN Cloud Intelligence API",
    description="Real-time telemetry and AI decision API for SWEN AIOps",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
TELEMETRY_PATH = os.getenv('TELEMETRY_PATH', '../ai-engine/latest_telemetry.json')
DECISIONS_PATH = os.getenv('DECISIONS_PATH', '../ai-engine/ai_decisions.json')
TERRAFORM_OUTPUT_PATH = os.getenv('TF_OUTPUT_PATH', '../../infra/envs/prod/outputs.json')

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

# Pydantic models
class DeploymentEvent(BaseModel):
    branch: str
    commit: str
    status: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    active_providers: List[str]
    last_ai_commit: Optional[str]
    services: Dict[str, str]
    timestamp: str

# Helper functions
def read_json_file(path: str, default: dict = None) -> dict:
    """Read JSON file with error handling."""
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return default or {}
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return default or {}

def get_current_timestamp() -> str:
    """Get current UTC timestamp."""
    return datetime.utcnow().isoformat() + 'Z'

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "SWEN Cloud Intelligence API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/healthz",
            "telemetry": "/api/telemetry",
            "decisions": "/api/decisions",
            "metrics": "/api/metrics",
            "websocket": "/ws"
        }
    }

@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with current system state."""
    telemetry = read_json_file(TELEMETRY_PATH, {})
    decisions = read_json_file(DECISIONS_PATH, [])
    
    # Extract active providers
    active_providers = set()
    services = {}
    
    for service, data in telemetry.items():
        if isinstance(data, dict) and 'current_provider' in data:
            provider = data['current_provider']
            active_providers.add(provider)
            services[service] = provider
    
    # Get last AI commit
    last_commit = None
    if decisions and len(decisions) > 0:
        last_decision = decisions[-1]
        last_commit = last_decision.get('git_branch', last_decision.get('timestamp'))
    
    return HealthResponse(
        status="ok",
        active_providers=list(active_providers),
        last_ai_commit=last_commit,
        services=services,
        timestamp=get_current_timestamp()
    )

@app.get("/api/telemetry")
async def get_telemetry():
    """Get latest telemetry data."""
    telemetry = read_json_file(TELEMETRY_PATH, {})
    
    if not telemetry:
        raise HTTPException(status_code=404, detail="No telemetry data available")
    
    return {
        "data": telemetry,
        "timestamp": get_current_timestamp()
    }

@app.get("/api/decisions")
async def get_decisions(limit: int = 50):
    """Get AI decision history."""
    decisions = read_json_file(DECISIONS_PATH, [])
    
    # Return most recent decisions
    recent_decisions = decisions[-limit:] if len(decisions) > limit else decisions
    
    return {
        "decisions": recent_decisions,
        "total": len(decisions),
        "timestamp": get_current_timestamp()
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get aggregated metrics and statistics."""
    telemetry = read_json_file(TELEMETRY_PATH, {})
    decisions = read_json_file(DECISIONS_PATH, [])
    
    # Calculate metrics
    total_services = len(telemetry)
    
    # Provider distribution
    provider_counts = {}
    total_cost = 0.0
    
    for service, data in telemetry.items():
        if isinstance(data, dict):
            provider = data.get('current_provider', 'unknown')
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            
            # Sum costs
            for p in ['aws', 'alibaba']:
                if p in data and 'cost' in data[p]:
                    total_cost += data[p]['cost']
    
    # Decision statistics
    total_decisions = len(decisions)
    recent_decisions = [d for d in decisions if 'timestamp' in d][-10:]
    
    avg_confidence = 0.0
    total_savings = 0.0
    
    if recent_decisions:
        confidences = [d.get('confidence', 0) for d in recent_decisions]
        avg_confidence = sum(confidences) / len(confidences)
        
        savings = [d.get('predicted_savings', 0) for d in recent_decisions]
        total_savings = sum(savings)
    
    return {
        "services": {
            "total": total_services,
            "by_provider": provider_counts
        },
        "cost": {
            "current_hourly": round(total_cost, 2),
            "estimated_monthly": round(total_cost * 24 * 30, 2)
        },
        "ai_decisions": {
            "total": total_decisions,
            "recent_count": len(recent_decisions),
            "avg_confidence": round(avg_confidence, 3),
            "total_predicted_savings": round(total_savings, 2)
        },
        "timestamp": get_current_timestamp()
    }

@app.get("/api/cost-analysis")
async def get_cost_analysis():
    """Get detailed cost analysis across providers."""
    telemetry = read_json_file(TELEMETRY_PATH, {})
    
    analysis = {
        "aws": {"services": 0, "total_cost": 0.0, "avg_latency": 0.0},
        "alibaba": {"services": 0, "total_cost": 0.0, "avg_latency": 0.0}
    }
    
    for service, data in telemetry.items():
        if not isinstance(data, dict):
            continue
            
        current_provider = data.get('current_provider')
        
        if current_provider in analysis:
            analysis[current_provider]["services"] += 1
            
            if current_provider in data:
                provider_data = data[current_provider]
                analysis[current_provider]["total_cost"] += provider_data.get('cost', 0)
                analysis[current_provider]["avg_latency"] += provider_data.get('latency', 0)
    
    # Calculate averages
    for provider in analysis:
        if analysis[provider]["services"] > 0:
            analysis[provider]["avg_latency"] /= analysis[provider]["services"]
            analysis[provider]["avg_latency"] = round(analysis[provider]["avg_latency"], 1)
        analysis[provider]["total_cost"] = round(analysis[provider]["total_cost"], 2)
    
    return {
        "analysis": analysis,
        "timestamp": get_current_timestamp()
    }

@app.post("/api/deployments")
async def receive_deployment_event(event: DeploymentEvent):
    """Receive deployment events from CI/CD pipeline."""
    logger.info(f"Deployment event received: {event.branch} - {event.status}")
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "deployment",
        "data": event.dict()
    })
    
    return {"status": "received", "timestamp": get_current_timestamp()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send periodic updates
            telemetry = read_json_file(TELEMETRY_PATH, {})
            metrics = await get_metrics()
            
            await websocket.send_json({
                "type": "update",
                "telemetry": telemetry,
                "metrics": metrics,
                "timestamp": get_current_timestamp()
            })
            
            # Wait for next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint."""
    telemetry = read_json_file(TELEMETRY_PATH, {})
    
    metrics = []
    
    # Service metrics
    for service, data in telemetry.items():
        if not isinstance(data, dict):
            continue
            
        current_provider = data.get('current_provider', 'unknown')
        
        for provider in ['aws', 'alibaba']:
            if provider in data:
                provider_data = data[provider]
                
                # Cost metric
                metrics.append(
                    f'swen_service_cost{{service="{service}",provider="{provider}"}} '
                    f'{provider_data.get("cost", 0)}'
                )
                
                # Latency metric
                metrics.append(
                    f'swen_service_latency{{service="{service}",provider="{provider}"}} '
                    f'{provider_data.get("latency", 0)}'
                )
                
                # GPU availability
                metrics.append(
                    f'swen_service_gpus{{service="{service}",provider="{provider}"}} '
                    f'{provider_data.get("available_gpus", 0)}'
                )
    
    return "\n".join(metrics)


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
