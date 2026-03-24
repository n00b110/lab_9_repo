# Lab 9 Project Index & Reference Guide

## 📚 Quick Navigation

### Getting Started
- [README.md](README.md) - Main project documentation
- [setup.sh](setup.sh) - Automated setup script (Linux/Mac)
- [setup.bat](setup.bat) - Automated setup script (Windows)
- [Makefile](Makefile) - Development commands

### Documentation
- [LAB9_SUMMARY.md](LAB9_SUMMARY.md) - Comprehensive Lab 9 enhancement summary
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide (local, Docker, cloud)
- [TESTING.md](TESTING.md) - Testing and evaluation guide
- [CONTRIBUTORS.md](CONTRIBUTORS.md) - Team contributions and responsibilities
- [INDEX.md](INDEX.md) - This file

### Configuration
- [.env.example](.env.example) - Environment variables template
- [.gitignore](.gitignore) - Git configuration
- [requirements.txt](requirements.txt) - Python dependencies

### Docker Configuration
- [Dockerfile](Dockerfile) - Multi-stage API Docker image
- [Dockerfile.streamlit](Dockerfile.streamlit) - Streamlit container image
- [docker-compose.yml](docker-compose.yml) - Multi-container orchestration

---

## 📂 Project Structure

### `/app` - Application Package
Core application components for API and UI

#### Files:
- **[api.py](app/api.py)** (370+ lines)
  - FastAPI backend with model inference
  - Comprehensive logging and error handling
  - Performance monitoring and metrics
  - Health checks and status endpoints
  - Request/response validation with Pydantic
  - Cache management
  - Endpoints: `/ask`, `/health`, `/metrics`, `/cache-stats`, `/config`

- **[streamlit_app.py](app/streamlit_app.py)** (550+ lines)
  - Interactive web UI with multi-tab interface
  - Chat interface with query history
  - Real-time metrics dashboard
  - Cache statistics display
  - Example questions for quick testing
  - Configuration panel
  - Response formatting with syntax highlighting

- **[config.py](app/config.py)** (110+ lines)
  - Environment-based configuration management
  - Support for dev/prod/test environments
  - Logging configuration
  - Model and API settings
  - Validation and defaults

- **[utils.py](app/utils.py)** (280+ lines)
  - Response caching system
  - Performance tracking and metrics
  - Input validation utilities
  - Response formatting functions
  - Error response builders
  - Timing decorators
  - Helper functions

- **[__init__.py](app/__init__.py)**
  - Package initialization
  - Version and metadata

---

### `/training` - Model Training
LoRA fine-tuning implementation

#### Files:
- **[train_lora.py](training/train_lora.py)**
  - LoRA fine-tuning with PEFT
  - Microsoft Phi-2 adaptation
  - Training dataset loading
  - Model checkpoint saving
  - Hyperparameter configuration

- **[__init__.py](training/__init__.py)**
  - Package initialization

---

### `/evaluation` - Model Evaluation
Comprehensive evaluation and testing suite

#### Files:
- **[evaluate.py](evaluate.py)** (370+ lines)
  - Model performance evaluation
  - Quality metrics calculation (length, structure, technical)
  - Performance benchmarking
  - Detailed evaluation reports (JSON + Markdown)
  - Test question suite (10+ questions)
  - API connectivity testing
  - Error tracking and reporting

- **[__init__.py](evaluation/__init__.py)**
  - Package initialization
  - Function exports

---

### `/monitoring` - System Monitoring
Performance metrics and monitoring infrastructure

#### Files:
- **[metrics.py](monitoring/metrics.py)** (180+ lines)
  - Metrics collection system
  - Performance monitoring class
  - Statistics aggregation
  - Metrics export functionality
  - Request tracking
  - Cache performance monitoring

- **[__init__.py](monitoring/__init__.py)**
  - Package initialization
  - Global instance exports

---

### `/dataset` - Training Data
Domain-specific instruction dataset

#### Files:
- **[instructions.json](dataset/instructions.json)**
  - Operating systems Q&A pairs
  - Used for LoRA fine-tuning
  - ~150+ instruction examples

---

### `/logs` - Application Logs (Runtime Directory)
Generated during execution

#### Files (Generated):
- **app.log** - API and application logs
- **evaluation.log** - Evaluation script logs
- **streamlit.log** - Streamlit logs

---

### `/models` - Model Weights (Runtime Directory)
LoRA-adapted model weights

#### Files (Generated):
- **checkpoint-*/** - Training checkpoints
- **adapter_config.json** - LoRA configuration
- **adapter_model.bin** - LoRA weights

---

### `/evaluation_results` - Evaluation Reports (Runtime Directory)
Generated evaluation results

#### Files (Generated):
- **evaluation_report_*.json** - Detailed results
- **evaluation_report_*.md** - Markdown reports

---

## 🔧 Command Reference

### Quick Start
```bash
./setup.sh              # Run setup (Linux/Mac)
setup.bat              # Run setup (Windows)
make help              # Show all commands
make install           # Install dependencies
make env               # Create .env file
```

### Development
```bash
make api               # Start API server (port 8000)
make frontend          # Start Streamlit (port 8501)
make run               # Run both (requires 2 terminals)
make train             # Train/fine-tune model
make evaluate          # Run evaluation suite
```

### Testing & Monitoring
```bash
make test              # Run pytest tests
make logs              # View application logs
curl http://localhost:8000/health         # Check API health
curl http://localhost:8000/metrics        # Get metrics
```

### Docker
```bash
make docker-build      # Build Docker image
make docker-run        # Start Docker containers
make docker-stop       # Stop Docker containers
docker-compose logs -f # View Docker logs
```

### Code Quality
```bash
make format            # Format code with black
make lint              # Run flake8 linting
make clean             # Clean cache and logs
```

---

## 📋 File Descriptions by Category

### Main Documentation (5 files)
1. **README.md** - Complete project documentation
2. **LAB9_SUMMARY.md** - Lab 9 enhancements summary
3. **DEPLOYMENT.md** - Deployment procedures
4. **TESTING.md** - Testing guide
5. **CONTRIBUTORS.md** - Team contributions

### Application Code (7 files)
1. **app/api.py** - FastAPI backend
2. **app/streamlit_app.py** - Streamlit frontend
3. **app/config.py** - Configuration management
4. **app/utils.py** - Utility functions
5. **app/__init__.py** - Package init
6. **training/train_lora.py** - Model training
7. **training/__init__.py** - Training package init

### Evaluation & Monitoring (4 files)
1. **evaluation/evaluate.py** - Evaluation suite
2. **evaluation/__init__.py** - Evaluation package init
3. **monitoring/metrics.py** - Metrics system
4. **monitoring/__init__.py** - Monitoring package init

### Configuration (5 files)
1. **.env.example** - Environment template
2. **requirements.txt** - Dependencies
3. **Dockerfile** - API container image
4. **Dockerfile.streamlit** - Streamlit container image
5. **docker-compose.yml** - Multi-container setup

### Development Tools (4 files)
1. **Makefile** - Development commands
2. **setup.sh** - Linux/Mac setup
3. **setup.bat** - Windows setup
4. **.gitignore** - Git configuration

### Data (1 file)
1. **dataset/instructions.json** - Training data

---

## 🎯 Lab 9 Enhancement Features

### ✅ Application Improvements
- [ ] Check README.md § "Enhanced Application Workflow"
- [ ] Review app/streamlit_app.py for UI features
- [ ] See DEPLOYMENT.md § "Running the Application"

### ✅ Monitoring & Evaluation
- [ ] Check monitoring/metrics.py for implementation
- [ ] See evaluation/evaluate.py for test suite
- [ ] Review README.md § "Evaluation & Metrics"

### ✅ Logging & Debugging
- [ ] Review app/api.py for logging implementation
- [ ] See app/config.py for logging configuration
- [ ] Check TESTING.md § "Debug Logging"

### ✅ Deployment Ready
- [ ] Check Dockerfile and docker-compose.yml
- [ ] Review DEPLOYMENT.md for cloud options
- [ ] See Makefile for build automation

---

## 🚀 Getting Started (Quick Guide)

### 1. Setup Environment
```bash
# Clone repository
git clone <repo-url>
cd lab_9_repo

# Run setup script
./setup.sh              # Linux/Mac
# or
setup.bat              # Windows
```

### 2. Configure Application
```bash
# Review and update .env file
nano .env              # Edit configuration
```

### 3. Start Application
```bash
# Option A: Using Make (Recommended)
make run

# Option B: Manual
# Terminal 1:
python -m uvicorn app.api:app --reload

# Terminal 2:
streamlit run app/streamlit_app.py
```

### 4. Access Application
- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 5. Run Evaluation
```bash
make evaluate
# or
python evaluation/evaluate.py
```

---

## 🔍 Key Implementation Details

### API Endpoints
See [app/api.py](app/api.py) for implementation:
- `POST /ask` - Generate response to question
- `GET /health` - Check API health
- `GET /metrics` - Get performance metrics
- `GET /cache-stats` - Get cache statistics
- `POST /clear-cache` - Clear response cache
- `POST /reset-metrics` - Reset metrics
- `GET /config` - Get configuration (debug)

### Streamlit Features
See [app/streamlit_app.py](app/streamlit_app.py) for implementation:
- Multi-tab interface (Chat, Metrics, History, About)
- Query history tracking
- Real-time metrics dashboard
- Cache management
- Configuration panel
- Example questions

### Configuration Options
See [.env.example](.env.example) and [app/config.py](app/config.py):
- Model configuration (model name, path)
- API settings (host, port, timeout)
- Logging levels and files
- Response parameters (max length, temperature)
- Caching and performance settings

### Monitoring & Metrics
See [monitoring/metrics.py](monitoring/metrics.py):
- Request tracking
- Inference time measurement
- Cache statistics
- Error counting
- Uptime tracking

### Evaluation System
See [evaluation/evaluate.py](evaluation/evaluate.py):
- 10+ test questions
- Quality metrics calculation
- Performance benchmarking
- Report generation (JSON + Markdown)

---

## 📊 File Statistics

### Code Files
- Python Files: 11
- Total Lines of Python: 2,500+
- Test Coverage: Evaluation suite included
- Documentation: Comprehensive

### Configuration Files
- Environment: 1 template
- Docker: 3 files (Dockerfile, Dockerfile.streamlit, docker-compose.yml)
- Build: 1 Makefile
- Development: 2 setup scripts

### Documentation Files
- Main guides: 5 files (README, LAB9_SUMMARY, DEPLOYMENT, TESTING, CONTRIBUTORS)
- Index: This file
- In-code: Docstrings throughout

---

## 🔐 Security & Best Practices

### Environment Configuration
- Store sensitive data in .env file
- Never commit .env to version control
- Use .env.example for templates
- Support for different environments

### Code Quality
- PEP 8 compliant
- Type hints throughout
- Comprehensive docstrings
- Error handling implemented
- Logging configured

### Logging
- Structured logging with timestamps
- Multiple log levels
- File persistence
- Request tracking
- Error context

---

## 📞 Support & Troubleshooting

### Finding Help
1. **For Setup Issues:** See setup.sh or setup.bat
2. **For Deployment:** See DEPLOYMENT.md
3. **For Testing:** See TESTING.md
4. **For Contributions:** See CONTRIBUTORS.md
5. **For General Info:** See README.md
6. **For Lab 9 Details:** See LAB9_SUMMARY.md

### Common Tasks
- Start development: `make run`
- View logs: `make logs` or `tail -f logs/app.log`
- Run evaluation: `make evaluate` or `python evaluation/evaluate.py`
- Deploy with Docker: `make docker-run`
- View metrics: `curl http://localhost:8000/metrics`
- Check health: `curl http://localhost:8000/health`

### Quick References
- API Documentation: http://localhost:8000/docs (when running)
- Streamlit Help: Run with `streamlit run --help`
- Make Commands: `make help`
- Configuration: Review `.env` file

---

## 🎓 Lab 9 Submission Files

### Required Documents
- ✅ README.md - Project documentation
- ✅ LAB9_SUMMARY.md - Enhancement summary
- ✅ CONTRIBUTORS.md - Team contributions
- ✅ DEPLOYMENT.md - Deployment guide
- ✅ TESTING.md - Testing guide

### Code Files
- ✅ app/ - Application code
- ✅ training/ - Model training
- ✅ evaluation/ - Evaluation suite
- ✅ monitoring/ - Monitoring system

### Configuration Files
- ✅ Dockerfile - Container image
- ✅ docker-compose.yml - Multi-container setup
- ✅ requirements.txt - Dependencies
- ✅ Makefile - Build automation
- ✅ .env.example - Configuration template

---

## 📅 Project Timeline

- **Phase 1:** Base project development
- **Phase 2:** Initial prototype
- **Lab 6-8:** Iterative improvements
- **Lab 9:** Production enhancements (THIS SUBMISSION)
  - ✅ Application workflow improvements
  - ✅ Monitoring and evaluation
  - ✅ Logging and debugging
  - ✅ Deployment configuration
- **Research-A-Thon:** Further development and competition

---

## 🎯 Next Steps After Lab 9

### Short-term
1. Review evaluation reports in `evaluation_results/`
2. Monitor metrics in Streamlit dashboard
3. Check logs for any issues
4. Test Docker deployment

### Medium-term
1. Deploy to cloud platform
2. Add authentication if needed
3. Implement advanced caching
4. Optimize performance

### Long-term
1. Scale to production
2. Add load balancing
3. Implement user analytics
4. Continuous monitoring

---

## 📝 Version Information

- **Project Version:** 2.0.0
- **Lab 9 Status:** ✅ Complete
- **Python Version Required:** 3.8+
- **Course:** CS 5542 - AI Systems
- **Semester:** Spring 2026
- **Last Updated:** March 2026

---

## ✨ Summary

This Lab 9 submission includes:
- **3,000+ lines** of new and enhanced code
- **5 comprehensive** documentation files
- **Complete Docker** deployment setup
- **Automated setup** scripts (bash and batch)
- **Full monitoring** and evaluation infrastructure
- **Production-ready** configuration management

The application is now ready for:
1. ✅ Demonstration to instructors
2. ✅ Deployment to production
3. ✅ Further development
4. ✅ Research-A-Thon competition

---

**For any questions, refer to the appropriate documentation file listed above.**

**Start here:** [README.md](README.md)

**Deploy here:** [DEPLOYMENT.md](DEPLOYMENT.md)

**Test here:** [TESTING.md](TESTING.md)

**Lab 9 details:** [LAB9_SUMMARY.md](LAB9_SUMMARY.md)

---

*End of Index*