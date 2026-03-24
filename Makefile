.PHONY: help install clean run api frontend test logs evaluate docker-build docker-run docker-stop format lint train env

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
	@echo "make env           - Create .env file"

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
	@echo "Press Ctrl+C to stop"
	python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000 & \
	streamlit run app/streamlit_app.py --server.port 8501

evaluate:
	python evaluation/evaluate.py

logs:
	tail -f logs/app.log

docker-build:
	docker build -t domain-ai-assistant:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

format:
	black app/ training/ evaluation/ monitoring/

lint:
	python -m flake8 app/ training/ evaluation/ monitoring/ || true

train:
	python training/train_lora.py

env:
	cp .env.example .env
	@echo "Created .env file. Please update with your settings."
