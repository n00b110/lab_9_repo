"""Utility functions and helpers for the application."""

import logging
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PerformanceTimer:
    """Context manager for measuring execution time."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.elapsed_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time = time.time() - self.start_time
        logger.info(f"{self.name} completed in {self.elapsed_time:.4f} seconds")
        return False


def time_execution(func):
    """Decorator to measure function execution time."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(
                f"Function '{func.__name__}' executed in {elapsed:.4f} seconds"
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Function '{func.__name__}' failed after {elapsed:.4f} seconds: {str(e)}"
            )
            raise

    return wrapper


def validate_question(
    question: str, min_length: int = 3, max_length: int = 1000
) -> tuple[bool, str]:
    """
    Validate user question.

    Args:
        question: The question to validate
        min_length: Minimum question length
        max_length: Maximum question length

    Returns:
        Tuple of (is_valid, message)
    """
    if not question or not isinstance(question, str):
        return False, "Question must be a non-empty string"

    question = question.strip()

    if len(question) < min_length:
        return False, f"Question must be at least {min_length} characters long"

    if len(question) > max_length:
        return False, f"Question must not exceed {max_length} characters"

    return True, "Valid"


def format_response(text: str, max_length: Optional[int] = None) -> str:
    """
    Format response text for display.

    Args:
        text: Raw response text
        max_length: Maximum length to truncate to

    Returns:
        Formatted response text
    """
    # Remove extra whitespace
    text = " ".join(text.split())

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "..."

    return text


def get_timestamp() -> str:
    """Get current timestamp as ISO format string."""
    return datetime.now().isoformat()


class ResponseCache:
    """Simple in-memory cache for responses."""

    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key in self.cache:
            self.hits += 1
            logger.debug(f"Cache hit for key: {key}")
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        """Store value in cache."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache evicted key: {oldest_key}")

        self.cache[key] = value
        logger.debug(f"Cached key: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate": f"{hit_rate:.2f}%",
            "cached_items": len(self.cache),
            "max_size": self.max_size,
        }


class MetricsTracker:
    """Track application metrics."""

    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "total_inference_time": 0.0,
            "request_times": [],
            "start_time": datetime.now(),
        }

    def record_request(self, inference_time: float, success: bool = True) -> None:
        """Record a request."""
        self.metrics["total_requests"] += 1
        if not success:
            self.metrics["total_errors"] += 1
        self.metrics["total_inference_time"] += inference_time
        self.metrics["request_times"].append(inference_time)

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated metrics."""
        total_requests = self.metrics["total_requests"]
        if total_requests == 0:
            return {
                "total_requests": 0,
                "total_errors": 0,
                "average_inference_time": 0.0,
                "error_rate": 0.0,
                "uptime_seconds": 0,
            }

        uptime = (datetime.now() - self.metrics["start_time"]).total_seconds()
        error_rate = (self.metrics["total_errors"] / total_requests) * 100

        return {
            "total_requests": total_requests,
            "total_errors": self.metrics["total_errors"],
            "average_inference_time": self.metrics["total_inference_time"]
            / total_requests,
            "min_inference_time": min(self.metrics["request_times"]),
            "max_inference_time": max(self.metrics["request_times"]),
            "error_rate": f"{error_rate:.2f}%",
            "uptime_seconds": int(uptime),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "total_inference_time": 0.0,
            "request_times": [],
            "start_time": datetime.now(),
        }
        logger.info("Metrics reset")


def create_response(
    response_text: str, inference_time: float, **kwargs
) -> Dict[str, Any]:
    """
    Create a structured API response.

    Args:
        response_text: Generated response text
        inference_time: Time taken to generate response
        **kwargs: Additional fields to include

    Returns:
        Structured response dictionary
    """
    response = {
        "response": response_text,
        "inference_time": round(inference_time, 4),
        "timestamp": get_timestamp(),
        "tokens_generated": len(response_text.split()),
    }
    response.update(kwargs)
    return response


def create_error_response(
    error_message: str, error_code: str = "UNKNOWN_ERROR", **kwargs
) -> Dict[str, Any]:
    """
    Create a structured error response.

    Args:
        error_message: Error description
        error_code: Error code for categorization
        **kwargs: Additional fields to include

    Returns:
        Structured error response dictionary
    """
    error_response = {
        "error": True,
        "error_code": error_code,
        "message": error_message,
        "timestamp": get_timestamp(),
    }
    error_response.update(kwargs)
    return error_response


def safe_get_dict(data: Dict, key: str, default: Any = None, expected_type=None) -> Any:
    """
    Safely get value from dictionary with type checking.

    Args:
        data: Dictionary to get value from
        key: Key to retrieve
        default: Default value if key doesn't exist
        expected_type: Expected type for validation

    Returns:
        Value from dictionary or default
    """
    value = data.get(key, default)

    if expected_type and value is not None:
        if not isinstance(value, expected_type):
            logger.warning(
                f"Expected type {expected_type} for key '{key}', got {type(value)}"
            )
            return default

    return value
