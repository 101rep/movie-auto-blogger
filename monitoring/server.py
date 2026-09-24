"""
AAOS Metrics HTTP Server
Exposes Prometheus /metrics endpoint independently or mounts on existing apps.
"""

import sys
import uvicorn
from fastapi import FastAPI, Response
from monitoring.metrics import metrics_collector

app = FastAPI(title="AAOS Metrics Server", version="1.0.0")

@app.get("/metrics")
def get_metrics():
    return Response(
        content=metrics_collector.get_metrics_payload(),
        media_type=metrics_collector.get_content_type()
    )

@app.get("/health")
def health_check():
    return {"status": "ok", "system": "AAOS Monitoring"}

def start_metrics_server(host: str = "0.0.0.0", port: int = 9090):
    uvicorn.run(app, host=host, port=port, log_level="warning")

if __name__ == "__main__":
    start_metrics_server()
