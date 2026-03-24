"""Monitoring and metrics collection for the application."""

import logging
import json
from datetime import datetime
from typing import Any, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and store application metrics."""

    def __init__(self, metrics_file: str = "logs/metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics: List[Dict[str, Any]] = []
        self.load_metrics()

    def load_metrics(self) -> None:
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    self.metrics = json.load(f)
                logger.info(f"Loaded {len(self.metrics)} existing metrics")
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
                self.metrics = []

    def save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2, default=str)
            logger.debug(f"Saved {len(self.metrics)} metrics")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def record_request(
        self,
        question: str,
        inference_time: float,
        response_length: int,
        success: bool = True,
        from_cache: bool = False,
        error_message: str = None,
    ) -> None:
        """Record a request metric."""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "question_length": len(question),
            "inference_time": inference_time,
            "response_length": response_length,
            "success": success,
            "from_cache": from_cache,
        }

        if error_message:
            metric["error"] = error_message

        self.metrics.append(metric)
        logger.debug(f"Recorded metric: {metric}")

        # Save periodically
        if len(self.metrics) % 10 == 0:
            self.save_metrics()

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics from metrics."""
        if not self.metrics:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_inference_time": 0,
                "average_response_length": 0,
                "cache_hit_rate": 0,
            }

        successful = [m for m in self.metrics if m.get("success", False)]
        failed = [m for m in self.metrics if not m.get("success", True)]
        cached = [m for m in self.metrics if m.get("from_cache", False)]

        avg_inference = (
            sum(m.get("inference_time", 0) for m in successful) / len(successful)
            if successful
            else 0
        )
        avg_response = (
            sum(m.get("response_length", 0) for m in successful) / len(successful)
            if successful
            else 0
        )
        cache_hit_rate = len(cached) / len(self.metrics) * 100 if self.metrics else 0

        return {
            "total_requests": len(self.metrics),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": f"{len(successful) / len(self.metrics) * 100:.2f}%",
            "average_inference_time": f"{avg_inference:.3f}s",
            "average_response_length": f"{avg_response:.0f}",
            "cache_hit_rate": f"{cache_hit_rate:.2f}%",
        }

    def export_metrics(self, filename: str) -> None:
        """Export metrics to a file."""
        try:
            with open(filename, "w") as f:
                json.dump(
                    {
                        "metrics": self.metrics,
                        "statistics": self.get_statistics(),
                        "export_time": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                    default=str,
                )
            logger.info(f"Metrics exported to {filename}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")


class PerformanceMonitor:
    """Monitor application performance."""

    def __init__(self):
        self.start_time = datetime.now()
        self.requests_count = 0
        self.errors_count = 0
        self.total_inference_time = 0.0

    def record_request(self, inference_time: float, success: bool = True) -> None:
        """Record a request."""
        self.requests_count += 1
        if not success:
            self.errors_count += 1
        self.total_inference_time += inference_time

    def get_uptime_seconds(self) -> int:
        """Get uptime in seconds."""
        return int((datetime.now() - self.start_time).total_seconds())

    def get_error_rate(self) -> float:
        """Get error rate percentage."""
        if self.requests_count == 0:
            return 0.0
        return (self.errors_count / self.requests_count) * 100

    def get_average_inference_time(self) -> float:
        """Get average inference time."""
        if self.requests_count == 0:
            return 0.0
        return self.total_inference_time / self.requests_count

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        return {
            "total_requests": self.requests_count,
            "total_errors": self.errors_count,
            "error_rate": f"{self.get_error_rate():.2f}%",
            "average_inference_time": f"{self.get_average_inference_time():.3f}s",
            "uptime_seconds": self.get_uptime_seconds(),
            "requests_per_minute": (
                f"{self.requests_count / (self.get_uptime_seconds() / 60):.2f}"
                if self.get_uptime_seconds() > 0
                else "N/A"
            ),
        }


# Global instances
metrics_collector = MetricsCollector()
performance_monitor = PerformanceMonitor()
```

Now let me create an __init__.py file for the monitoring package and update the evaluation script:
