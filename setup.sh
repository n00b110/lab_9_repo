#!/bin/bash

# Domain Adapted AI Assistant - Setup Script
# Lab 9 Enhancement
# This script automates the setup process for local development

set -e

echo "=================================================="
echo "Domain Adapted AI Assistant - Setup Script"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3.8+ is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Skipping virtual environment creation"
        SKIP_VENV=true
    fi
fi

# Create virtual environment
if [ "$SKIP_VENV" != "true" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p models
mkdir -p evaluation_results
echo -e "${GREEN}✓ Directories created${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}Note: Update .env with your settings if needed${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
python -c "import fastapi; import streamlit; import torch; import transformers" 2>/dev/null && \
    echo -e "${GREEN}✓ All core dependencies verified${NC}" || \
    echo -e "${RED}✗ Some dependencies failed to import${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment (if not already activated):"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the application:"
echo "   Option A (Recommended): make run"
echo "   Option B (Manual):"
echo "     Terminal 1: python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000"
echo "     Terminal 2: streamlit run app/streamlit_app.py --server.port 8501"
echo ""
echo "3. Access the application:"
echo "   Frontend: http://localhost:8501"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "4. For more commands, run: make help"
echo ""
