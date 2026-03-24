"""Enhanced FastAPI backend with logging, monitoring, and error handling."""

import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.config import config
from app.utils import (
    MetricsTracker,
    PerformanceTimer,
    ResponseCache,
    create_error_response,
    create_response,
    format_response,
    time_execution,
    validate_question,
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(config.LOG_FILE), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Initialize global state
metrics_tracker = MetricsTracker()
response_cache = ResponseCache(max_size=config.CACHE_SIZE)

# Try to load the model
model = None
tokenizer = None
MODEL_LOADED = False


def load_model():
    """Load the fine-tuned model and tokenizer."""
    global model, tokenizer, MODEL_LOADED

    try:
        logger.info(f"Loading model: {config.MODEL_NAME}")
        from transformers import pipeline

        # Try to load from local path first
        try:
            logger.info(f"Attempting to load from local path: {config.MODEL_PATH}")
            pipeline_model = pipeline(
                "text-generation",
                model=config.MODEL_PATH,
                device=0,  # Use GPU if available
            )
            logger.info("Model loaded from local path")
        except Exception as e:
            logger.warning(
                f"Failed to load from local path: {e}. Trying from HuggingFace..."
            )
            pipeline_model = pipeline(
                "text-generation", model=config.MODEL_NAME, device=0
            )
            logger.info(f"Model loaded from HuggingFace: {config.MODEL_NAME}")

        model = pipeline_model
        MODEL_LOADED = True
        logger.info("Model loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        MODEL_LOADED = False
        logger.warning("Operating in degraded mode - model not loaded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Domain Adapted AI Assistant API")
    logger.info(f"Configuration: {config.get_config_dict()}")
    load_model()

    yield

    # Shutdown
    logger.info("Shutting down API")
    logger.info(f"Final metrics: {metrics_tracker.get_stats()}")


# Initialize FastAPI app
app = FastAPI(
    title="Domain Adapted AI Assistant",
    description="LoRA fine-tuned model for domain-specific Q&A",
    version="2.0.0",
    lifespan=lifespan,
)


# Request/Response Models
class QuestionRequest(BaseModel):
    """Request model for question endpoint."""

    question: str = Field(
        ..., min_length=3, max_length=1000, description="The question to ask"
    )
    max_length: Optional[int] = Field(
        default=None, description="Maximum response length in characters"
    )
    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=2.0, description="Sampling temperature for generation"
    )
    use_cache: Optional[bool] = Field(
        default=True, description="Whether to use cached responses"
    )


class QuestionResponse(BaseModel):
    """Response model for successful question endpoint."""

    response: str = Field(..., description="Generated response")
    inference_time: float = Field(
        ..., description="Time taken to generate response in seconds"
    )
    tokens_generated: int = Field(..., description="Number of tokens in response")
    timestamp: str = Field(..., description="ISO format timestamp")
    from_cache: bool = Field(
        default=False, description="Whether response was from cache"
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: bool = Field(default=True, description="Error flag")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    timestamp: str = Field(..., description="ISO format timestamp")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Health status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    uptime_seconds: int = Field(..., description="API uptime in seconds")
    requests_processed: int = Field(..., description="Total requests processed")


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    total_requests: int = Field(..., description="Total requests processed")
    total_errors: int = Field(..., description="Total errors encountered")
    average_inference_time: float = Field(
        ..., description="Average inference time in seconds"
    )
    error_rate: str = Field(..., description="Error rate percentage")
    uptime_seconds: int = Field(..., description="Uptime in seconds")
    cache_stats: dict = Field(..., description="Cache statistics")
    model_loaded: bool = Field(..., description="Model load status")


@app.get("/health", response_model=HealthResponse)
@time_execution
async def health_check():
    """Check API health status."""
    logger.debug("Health check requested")
    stats = metrics_tracker.get_stats()

    return HealthResponse(
        status="healthy" if MODEL_LOADED else "degraded",
        model_loaded=MODEL_LOADED,
        uptime_seconds=stats.get("uptime_seconds", 0),
        requests_processed=stats.get("total_requests", 0),
    )


@app.get("/metrics", response_model=MetricsResponse)
@time_execution
async def get_metrics():
    """Get application metrics."""
    logger.debug("Metrics requested")
    stats = metrics_tracker.get_stats()
    cache_stats = response_cache.get_stats()

    return MetricsResponse(
        total_requests=stats.get("total_requests", 0),
        total_errors=stats.get("total_errors", 0),
        average_inference_time=stats.get("average_inference_time", 0.0),
        error_rate=stats.get("error_rate", "0%"),
        uptime_seconds=stats.get("uptime_seconds", 0),
        cache_stats=cache_stats,
        model_loaded=MODEL_LOADED,
    )


@app.post("/ask", response_model=QuestionResponse)
@time_execution
async def ask(request: QuestionRequest):
    """
    Generate a response to a question using the fine-tuned model.

    Args:
        request: Question request containing the question and optional parameters

    Returns:
        Question response with generated text and metadata

    Raises:
        HTTPException: If model is not loaded or generation fails
    """
    logger.info(f"Question received: {request.question[:50]}...")

    # Validate question
    is_valid, validation_msg = validate_question(request.question)
    if not is_valid:
        logger.warning(f"Invalid question: {validation_msg}")
        error_resp = create_error_response(validation_msg, error_code="INVALID_INPUT")
        metrics_tracker.record_request(0, success=False)
        raise HTTPException(status_code=400, detail=error_resp)

    # Check model
    if not MODEL_LOADED:
        logger.error("Model not loaded")
        error_resp = create_error_response(
            "Model not available. Please try again later.",
            error_code="MODEL_NOT_LOADED",
        )
        metrics_tracker.record_request(0, success=False)
        raise HTTPException(status_code=503, detail=error_resp)

    # Check cache if enabled
    if request.use_cache:
        cached_response = response_cache.get(request.question)
        if cached_response:
            logger.info("Returning cached response")
            metrics_tracker.record_request(0, success=True)
            cached_response["from_cache"] = True
            return cached_response

    try:
        with PerformanceTimer("Question answering"):
            start_time = time.time()

            # Build prompt
            prompt = f"""You are a domain expert assistant specialized in computer science and operating systems.

Question:
{request.question}

Answer:"""

            logger.debug(f"Prompt: {prompt[:100]}...")

            # Generate response
            max_length = request.max_length or config.MAX_RESPONSE_LENGTH
            temperature = request.temperature or config.TEMPERATURE

            result = model(
                prompt,
                max_length=max_length,
                temperature=temperature,
                top_p=config.TOP_P,
                do_sample=True,
            )

            inference_time = time.time() - start_time

            # Extract and format response
            full_response = result[0]["generated_text"]
            # Extract only the answer part (after "Answer:")
            if "Answer:" in full_response:
                response_text = full_response.split("Answer:")[-1].strip()
            else:
                response_text = full_response

            response_text = format_response(response_text, max_length)

            logger.info(f"Response generated in {inference_time:.4f}s")
            logger.debug(f"Response: {response_text[:100]}...")

            # Create response object
            response_obj = create_response(
                response_text, inference_time, from_cache=False
            )

            # Cache the response if enabled
            if request.use_cache:
                response_cache.put(request.question, response_obj)

            # Record metrics
            metrics_tracker.record_request(inference_time, success=True)

            return QuestionResponse(**response_obj)

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        metrics_tracker.record_request(0, success=False)
        error_resp = create_error_response(
            f"Failed to generate response: {str(e)}", error_code="GENERATION_ERROR"
        )
        raise HTTPException(status_code=500, detail=error_resp)


@app.get("/config")
@time_execution
async def get_config_endpoint():
    """Get current configuration (for debugging)."""
    logger.debug("Configuration requested")

    if not config.DEBUG_MODE:
        logger.warning("Config endpoint accessed but DEBUG_MODE is disabled")
        raise HTTPException(
            status_code=403, detail={"error": "Config endpoint disabled in production"}
        )

    return config.get_config_dict()


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint accessed")
    return {
        "message": "Domain Adapted AI Assistant API",
        "version": "2.0.0",
        "endpoints": {
            "POST /ask": "Generate response to a question",
            "GET /health": "Check API health",
            "GET /metrics": "Get application metrics",
            "GET /config": "Get configuration (debug only)",
        },
        "docs": "/docs",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    error_resp = create_error_response(
        "An unexpected error occurred", error_code="INTERNAL_ERROR"
    )
    return JSONResponse(status_code=500, content=error_resp)


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting API server...")
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower(),
    )
