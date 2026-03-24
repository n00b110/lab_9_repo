"""Domain Adapted AI Assistant - App Package

This package contains the main application components:
- API: FastAPI backend with model inference
- Streamlit: Web UI for user interaction
- Config: Configuration management
- Utils: Utility functions and helpers
"""

__version__ = "2.0.0"
__author__ = "Ibrahim Alborno, Immanuel Olaoye"
__description__ = "Domain Adapted AI Assistant with LoRA Fine-tuning"

# Package exports
__all__ = [
    "api",
    "streamlit_app",
    "config",
    "utils",
]
