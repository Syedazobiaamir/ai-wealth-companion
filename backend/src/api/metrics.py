"""
Phase V: Prometheus Metrics Endpoint
AI Wealth Companion Cloud-Native Observability

Provides Prometheus-compatible metrics endpoint for monitoring
application performance, business metrics, and health indicators.
"""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Response

router = APIRouter(tags=["metrics"])


@dataclass
class MetricValue:
    """A single metric value with optional labels."""
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: Optional[float] = None


@dataclass
class Metric:
    """A Prometheus metric with type, help text, and values."""
    name: str
    metric_type: str  # counter, gauge, histogram, summary
    help_text: str
    values: List[MetricValue] = field(default_factory=list)


class PrometheusMetrics:
    """
    Prometheus metrics collector for AI Wealth Companion.

    Collects and exposes metrics in Prometheus text format.
    """

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._counters: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

        # Initialize default metrics
        self._init_default_metrics()

    def _init_default_metrics(self) -> None:
        """Initialize default application metrics."""
        # HTTP metrics
        self.register_counter(
            "http_requests_total",
            "Total number of HTTP requests",
        )
        self.register_counter(
            "http_request_errors_total",
            "Total number of HTTP request errors",
        )
        self.register_histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
        )

        # Event metrics
        self.register_counter(
            "events_published_total",
            "Total number of events published",
        )
        self.register_counter(
            "events_processed_total",
            "Total number of events processed",
        )
        self.register_counter(
            "events_failed_total",
            "Total number of failed event processing",
        )
        self.register_gauge(
            "events_pending",
            "Number of pending events in queue",
        )

        # Business metrics
        self.register_counter(
            "transactions_created_total",
            "Total number of transactions created",
        )
        self.register_gauge(
            "active_users",
            "Number of active users",
        )
        self.register_counter(
            "ai_insights_generated_total",
            "Total number of AI insights generated",
        )
        self.register_counter(
            "budget_alerts_sent_total",
            "Total number of budget alerts sent",
        )

        # Database metrics
        self.register_gauge(
            "database_connections_active",
            "Number of active database connections",
        )
        self.register_histogram(
            "database_query_duration_seconds",
            "Database query duration in seconds",
        )

        # Dapr metrics (collected from sidecar)
        self.register_gauge(
            "dapr_sidecar_healthy",
            "Whether the Dapr sidecar is healthy (1) or not (0)",
        )

    def register_counter(self, name: str, help_text: str) -> None:
        """Register a counter metric."""
        self._metrics[name] = Metric(
            name=name,
            metric_type="counter",
            help_text=help_text,
        )

    def register_gauge(self, name: str, help_text: str) -> None:
        """Register a gauge metric."""
        self._metrics[name] = Metric(
            name=name,
            metric_type="gauge",
            help_text=help_text,
        )

    def register_histogram(self, name: str, help_text: str) -> None:
        """Register a histogram metric."""
        self._metrics[name] = Metric(
            name=name,
            metric_type="histogram",
            help_text=help_text,
        )

    def inc_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None) -> None:
        """Increment a counter metric."""
        label_key = self._labels_to_key(labels or {})
        self._counters[name][label_key] += value

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge metric value."""
        label_key = self._labels_to_key(labels or {})
        self._gauges[name][label_key] = value

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a histogram metric value."""
        label_key = self._labels_to_key(labels or {})
        self._histograms[name][label_key].append(value)
        # Keep only last 1000 observations
        if len(self._histograms[name][label_key]) > 1000:
            self._histograms[name][label_key] = self._histograms[name][label_key][-1000:]

    def _labels_to_key(self, labels: Dict[str, str]) -> str:
        """Convert labels dict to a string key."""
        if not labels:
            return ""
        return ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))

    def _key_to_labels(self, key: str) -> str:
        """Convert string key back to label format."""
        if not key:
            return ""
        return "{" + key + "}"

    def format_prometheus(self) -> str:
        """Format all metrics in Prometheus text format."""
        lines = []

        for name, metric in self._metrics.items():
            # Add HELP and TYPE
            lines.append(f"# HELP {name} {metric.help_text}")
            lines.append(f"# TYPE {name} {metric.metric_type}")

            if metric.metric_type == "counter":
                for label_key, value in self._counters.get(name, {}).items():
                    label_str = self._key_to_labels(label_key)
                    lines.append(f"{name}{label_str} {value}")

            elif metric.metric_type == "gauge":
                for label_key, value in self._gauges.get(name, {}).items():
                    label_str = self._key_to_labels(label_key)
                    lines.append(f"{name}{label_str} {value}")

            elif metric.metric_type == "histogram":
                for label_key, values in self._histograms.get(name, {}).items():
                    if not values:
                        continue
                    label_str = self._key_to_labels(label_key)
                    # Calculate histogram buckets
                    buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
                    counts = [sum(1 for v in values if v <= b) for b in buckets]
                    total = len(values)
                    total_sum = sum(values)

                    for bucket, count in zip(buckets, counts):
                        bucket_label = f'le="{bucket}"'
                        if label_key:
                            bucket_label = f"{label_key},{bucket_label}"
                        lines.append(f'{name}_bucket{{{bucket_label}}} {count}')

                    inf_label = 'le="+Inf"'
                    if label_key:
                        inf_label = f"{label_key},{inf_label}"
                    lines.append(f'{name}_bucket{{{inf_label}}} {total}')
                    lines.append(f"{name}_sum{label_str} {total_sum}")
                    lines.append(f"{name}_count{label_str} {total}")

            lines.append("")

        return "\n".join(lines)


# Singleton metrics instance
_metrics: Optional[PrometheusMetrics] = None


def get_metrics() -> PrometheusMetrics:
    """Get the singleton metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = PrometheusMetrics()
    return _metrics


# Request timing context manager
@asynccontextmanager
async def track_request_time(method: str, path: str):
    """Context manager to track HTTP request timing."""
    metrics = get_metrics()
    start_time = time.time()
    try:
        yield
        metrics.inc_counter(
            "http_requests_total",
            labels={"method": method, "path": path, "status": "success"},
        )
    except Exception:
        metrics.inc_counter(
            "http_request_errors_total",
            labels={"method": method, "path": path},
        )
        raise
    finally:
        duration = time.time() - start_time
        metrics.observe_histogram(
            "http_request_duration_seconds",
            duration,
            labels={"method": method, "path": path},
        )


# API Endpoints
@router.get("/metrics", response_class=Response)
async def get_prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns all application metrics in Prometheus text format.
    """
    metrics = get_metrics()

    # Update some real-time gauges
    metrics.set_gauge("dapr_sidecar_healthy", 1)

    content = metrics.format_prometheus()
    return Response(
        content=content,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get("/metrics/health")
async def metrics_health():
    """Health check for metrics endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
