#!/bin/bash
# Setup script for Energy Bill Predictor

echo "🔧 Setting up Energy Bill Predictor..."
echo ""

# Create virtual environment
echo "1️⃣  Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "2️⃣  Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Generate training data
echo "3️⃣  Generating synthetic training data..."
python -m src.data_generator

# Train model
echo "4️⃣  Training Random Forest model..."
python -m src.model_trainer

# Test system
echo "5️⃣  Testing prediction system..."
python test_prediction.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 To start the web service, run:"
echo "   ./run_server.sh"
echo ""
echo "   Or manually:"
echo "   source venv/bin/activate"
echo "   python app/app.py"
echo ""

