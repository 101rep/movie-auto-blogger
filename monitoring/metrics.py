"""
AAOS Monitoring & Metrics Layer
Uses prometheus_client to track API calls, verification results, queue depths, and latencies.
Exposes standard Prometheus metrics endpoint.
"""

import time
from typing import Optional, Callable
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY
)

# ── Counters ──────────────────────────────────────────────────────────────────
API_REQUESTS_TOTAL = Counter(
    "aaos_api_requests_total",
    "Total number of external platform API requests made by AAOS",
    ["platform", "endpoint", "status"]
)

PUBLICATIONS_TOTAL = Counter(
    "aaos_post_publications_total",
    "Total number of post publication attempts across platforms",
    ["platform", "status"]
)

VERIFICATION_CHECKS_TOTAL = Counter(
    "aaos_verification_checks_total",
    "Total number of Playwright DOM verification checks executed",
    ["platform", "result"]
)

RECOVERY_ATTEMPTS_TOTAL = Counter(
    "aaos_recovery_attempts_total",
    "Total number of automated recovery and retry attempts triggered",
    ["platform", "reason"]
)

# ── Gauges ────────────────────────────────────────────────────────────────────
ACTIVE_JOBS = Gauge(
    "aaos_active_jobs",
    "Number of jobs currently in progress",
    ["platform"]
)

QUEUE_DEPTH = Gauge(
    "aaos_queue_depth",
    "Current depth of task and publication queues",
    ["queue_name"]
)

SYSTEM_HEALTH = Gauge(
    "aaos_system_health",
    "Operational health status (1 = healthy, 0 = degraded/down)",
    ["component"]
)

# ── Histograms ────────────────────────────────────────────────────────────────
JOB_DURATION_SECONDS = Histogram(
    "aaos_job_duration_seconds",
    "Duration of AAOS jobs and tasks in seconds",
    ["platform", "operation"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float("inf"))
)


class MetricsCollector:
    """Helper class providing easy instrumentation wrappers and recorders."""

    @staticmethod
    def record_api_call(platform: str, endpoint: str, success: bool):
        status = "success" if success else "failure"
        API_REQUESTS_TOTAL.labels(platform=platform, endpoint=endpoint, status=status).inc()

    @staticmethod
    def record_publication(platform: str, success: bool):
        status = "success" if success else "failure"
        PUBLICATIONS_TOTAL.labels(platform=platform, status=status).inc()

    @staticmethod
    def record_verification(platform: str, verified: bool):
        result = "verified" if verified else "failed"
        VERIFICATION_CHECKS_TOTAL.labels(platform=platform, result=result).inc()

    @staticmethod
    def record_recovery(platform: str, reason: str = "auto_retry"):
        RECOVERY_ATTEMPTS_TOTAL.labels(platform=platform, reason=reason).inc()

    @staticmethod
    def set_system_health(component: str, is_healthy: bool):
        SYSTEM_HEALTH.labels(component=component).set(1.0 if is_healthy else 0.0)

    @staticmethod
    def update_queue_depth(queue_name: str, depth: int):
        QUEUE_DEPTH.labels(queue_name=queue_name).set(depth)

    @staticmethod
    def get_metrics_payload() -> bytes:
        return generate_latest(REGISTRY)

    @staticmethod
    def get_content_type() -> str:
        return CONTENT_TYPE_LATEST


metrics_collector = MetricsCollector()
