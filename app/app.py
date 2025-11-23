from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.predictor import EnergyBillPredictor
import pandas as pd
import json

app = Flask(__name__)

# Configuration data
CITIES = {
    'New York': {'state': 'NY', 'base_rate': 0.18},
    'Los Angeles': {'state': 'CA', 'base_rate': 0.22},
    'Chicago': {'state': 'IL', 'base_rate': 0.14},
    'Houston': {'state': 'TX', 'base_rate': 0.12},
    'Phoenix': {'state': 'AZ', 'base_rate': 0.13},
    'Miami': {'state': 'FL', 'base_rate': 0.11},
    'Seattle': {'state': 'WA', 'base_rate': 0.10},
    'Boston': {'state': 'MA', 'base_rate': 0.21},
    'Denver': {'state': 'CO', 'base_rate': 0.12},
    'Atlanta': {'state': 'GA', 'base_rate': 0.13}
}

HOUSE_TYPES = ['Apartment', 'Condo', 'Townhouse', 'House', 'Large House']

MONTHS = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

# Global predictor (will be initialized after model is trained)
predictor = None

def init_predictor():
    """Initialize predictor if model exists"""
    global predictor
    if predictor is None:
        try:
            predictor = EnergyBillPredictor()
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not load model: {e}")
            print("Please train the model first by running: python -m src.model_trainer")
            return False
    return True

@app.route('/')
def index():
    """Render main dashboard"""
    # Try to load metadata
    metadata = {'metrics': {'test': {'r2': 0, 'mae': 0, 'mape': 0}}}
    try:
        with open('models/metadata.json', 'r') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        pass
    
    return render_template('index.html', 
                         cities=sorted(CITIES.keys()),
                         house_types=HOUSE_TYPES,
                         months=MONTHS,
                         metrics=metadata.get('metrics', metadata['metrics']))

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request"""
    if not init_predictor():
        return jsonify({
            'status': 'error',
            'message': 'Model not trained yet. Please train the model first.'
        }), 503
    
    try:
        # Get form data
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Prepare input
        input_data = {
            'city': data['city'],
            'state': CITIES[data['city']]['state'],
            'house_type': data['house_type'],
            'month': int(data['month']),
            'avg_temp_f': float(data['avg_temp_f']),
            'humidity': float(data['humidity']),
            'heating_degree_days': float(data.get('heating_degree_days', 0)),
            'cooling_degree_days': float(data.get('cooling_degree_days', 0)),
            'avg_energy_kwh': float(data['avg_energy_kwh']),
            'square_feet': int(data['square_feet']),
            'num_occupants': int(data['num_occupants']),
            'energy_rate_per_kwh': float(data.get('energy_rate_per_kwh', 
                                                   CITIES[data['city']]['base_rate']))
        }
        
        # Make prediction
        result = predictor.predict(input_data)
        result['input'] = input_data
        result['status'] = 'success'
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get available cities"""
    return jsonify({
        'cities': [{'name': city, 'state': info['state'], 'rate': info['base_rate']} 
                   for city, info in CITIES.items()]
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get model statistics"""
    try:
        with open('models/metadata.json', 'r') as f:
            metadata = json.load(f)
        return jsonify(metadata)
    except FileNotFoundError:
        return jsonify({'error': 'Model not trained yet'}), 404

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Handle batch prediction"""
    if not init_predictor():
        return jsonify({
            'status': 'error',
            'message': 'Model not trained yet. Please train the model first.'
        }), 503
    
    try:
        data = request.get_json()
        df = pd.DataFrame(data['inputs'])
        results = predictor.batch_predict(df)
        return jsonify({
            'status': 'success',
            'predictions': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔌 ENERGY BILL PREDICTOR - Web Service")
    print("="*60)
    print("\n🌐 Starting server at http://localhost:5000")
    print("\n📝 Available endpoints:")
    print("   GET  /              - Main dashboard")
    print("   POST /predict       - Make prediction")
    print("   GET  /api/cities    - Get city list")
    print("   GET  /api/stats     - Get model stats")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

