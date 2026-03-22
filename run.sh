#!/bin/bash
# IRIS Quick Start Script

echo "=============================="
echo "  IRIS — AI Job Portal"
echo "=============================="

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "ERROR: Python 3 not found. Install from https://python.org"
  exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install deps
echo "Installing dependencies..."
pip install -r requirements.txt -q

# Copy .env if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "Created .env from .env.example (configure SMTP for email)"
fi

echo ""
echo "Starting IRIS on http://localhost:5000"
echo "Demo: admin@iris.com / Admin@1234"
echo ""
python app.py
