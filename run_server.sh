#!/bin/bash
# Quick start script to run the Energy Bill Predictor web service

echo "🔌 Starting Energy Bill Predictor Web Service..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run Flask app
python app/app.py

