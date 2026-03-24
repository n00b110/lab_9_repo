import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""

    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "microsoft/phi-2")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # Model Generation Configuration
    MAX_RESPONSE_LENGTH: int = int(os.getenv("MAX_RESPONSE_LENGTH", "500"))
    MIN_RESPONSE_LENGTH: int = int(os.getenv("MIN_RESPONSE_LENGTH", "50"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P: float = float(os.getenv("TOP_P", "0.95"))

    # Evaluation Configuration
    EVAL_LOG_FILE: str = os.path.join(LOG_DIR, "evaluation.log")
    EVAL_BATCH_SIZE: int = int(os.getenv("EVAL_BATCH_SIZE", "1"))

    # Performance Configuration
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    CACHE_SIZE: int = int(os.getenv("CACHE_SIZE", "100"))

    # Monitoring Configuration
    TRACK_METRICS: bool = os.getenv("TRACK_METRICS", "True").lower() == "true"
    METRICS_LOG_FILE: str = os.path.join(LOG_DIR, "metrics.log")

    @classmethod
    def ensure_log_directory(cls) -> None:
        """Ensure log directory exists"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)

    @classmethod
    def get_config_dict(cls) -> dict:
        """Get all configuration as dictionary"""
        return {
            "model_name": cls.MODEL_NAME,
            "model_path": cls.MODEL_PATH,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "log_level": cls.LOG_LEVEL,
            "debug_mode": cls.DEBUG_MODE,
            "max_response_length": cls.MAX_RESPONSE_LENGTH,
            "temperature": cls.TEMPERATURE,
            "tracking_metrics": cls.TRACK_METRICS,
        }


class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG_MODE: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(Config):
    """Production environment configuration"""

    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"


class TestingConfig(Config):
    """Testing environment configuration"""

    DEBUG_MODE: bool = True
    LOG_LEVEL: str = "DEBUG"
    MODEL_NAME: str = "gpt2"  # Use smaller model for testing
    MAX_RESPONSE_LENGTH: int = 100


def get_config(env: Optional[str] = None) -> Config:
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "production").lower()

    config_map = {
        "development": DevelopmentConfig,
        "dev": DevelopmentConfig,
        "production": ProductionConfig,
        "prod": ProductionConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
    }

    config_class = config_map.get(env, ProductionConfig)
    config = config_class()
    config.ensure_log_directory()

    return config


# Default configuration instance
config = get_config()
