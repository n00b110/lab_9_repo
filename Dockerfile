# Multi-stage build for Domain Adapted AI Assistant

# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    DEBUG_MODE=False \
    MODEL_PATH=/app/models

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/models /app/evaluation_results

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port 8000 &\nstreamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
```

<file_path>
lab_9_repo/docker-compose.yml
</file_path>

<edit_description>
Create docker-compose configuration for multi-container deployment
</edit_description>

```
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: domain-ai-api
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - DEBUG_MODE=False
      - MODEL_PATH=/app/models
      - API_TIMEOUT=30
      - MAX_RESPONSE_LENGTH=500
      - ENABLE_CACHING=True
    volumes:
      - ./logs:/app/logs
      - ./models:/app/models
    command: python -m uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: domain-ai-frontend
    ports:
      - "8501:8501"
    environment:
      - LOG_LEVEL=INFO
      - DEBUG_MODE=False
    volumes:
      - ./logs:/app/logs
    command: streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
    depends_on:
      api:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge
```

<file_path>
lab_9_repo/.env.example
</file_path>

<edit_description>
Create environment configuration template
</edit_description>

```
# Model Configuration
MODEL_NAME=microsoft/phi-2
MODEL_PATH=./models
ENVIRONMENT=production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_TIMEOUT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=./logs
DEBUG_MODE=False

# Model Generation Configuration
MAX_RESPONSE_LENGTH=500
MIN_RESPONSE_LENGTH=50
TEMPERATURE=0.7
TOP_P=0.95

# Evaluation Configuration
EVAL_BATCH_SIZE=1

# Performance Configuration
ENABLE_CACHING=True
CACHE_SIZE=100

# Monitoring Configuration
TRACK_METRICS=True

# Streamlit Configuration
STREAMLIT_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

<file_path>
lab_9_repo/.gitignore
</file_path>

<edit_description>
Create gitignore for version control
</edit_description>

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
logs/
*.log

# Models
models/
*.bin
*.safetensors

# Evaluation results
evaluation_results/

# Environment variables
.env
.env.local
.env.*.local

# Streamlit
.streamlit/

# Cache
.cache/
*.cache

# Database
*.db
*.sqlite

# Docker
.dockerignore
docker-compose.override.yml

# Metrics
*.json
!dataset/*.json

# OS
.DS_Store
Thumbs.db

# Temporary
tmp/
temp/
*.tmp
```

<file_path>
lab_9_repo/Makefile
</file_path>

<edit_description>
Create Makefile for development convenience
</edit_description>

```
.PHONY: help install clean run api frontend test logs evaluate docker-build docker-run docker-stop format lint

help:
	@echo "Domain Adapted AI Assistant - Development Commands"
	@echo "=================================================="
	@echo "make install       - Install dependencies"
	@echo "make clean         - Clean up cache and logs"
	@echo "make api           - Start API server"
	@echo "make frontend      - Start Streamlit frontend"
	@echo "make run           - Run both API and frontend"
	@echo "make test          - Run evaluation"
	@echo "make logs          - View application logs"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-run    - Run Docker container"
	@echo "make docker-stop   - Stop Docker container"
	@echo "make format        - Format code with black"
	@echo "make lint          - Run linting"
	@echo "make train         - Train/fine-tune the model"

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

clean:
	rm -rf __pycache__ .pytest_cache .coverage
	rm -rf logs/*.log
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

api:
	python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

frontend:
	streamlit run app/streamlit_app.py --server.port 8501

run:
	@echo "Starting API and Frontend..."
	@echo "API will run on: http://localhost:8000"
	@echo "Frontend will run on: http://localhost:8501"
	python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000 & \
	streamlit run app/streamlit_app.py --server.port 8501

test:
	python evaluation/evaluate.py

logs:
	tail -f logs/app.log

docker-build:
	docker build -t domain-ai-assistant:latest .

docker-run:
	docker run -d \
		-p 8000:8000 \
		-p 8501:8501 \
		--name domain-ai-assistant \
		domain-ai-assistant:latest

docker-stop:
	docker stop domain-ai-assistant
	docker rm domain-ai-assistant

format:
	black app/ training/ evaluation/ monitoring/

lint:
	python -m flake8 app/ training/ evaluation/ monitoring/

train:
	python training/train_lora.py

env:
	cp .env.example .env
	@echo "Created .env file. Please update with your settings."
