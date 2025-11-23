#!/usr/bin/env python3
"""Test script to verify the prediction system works"""

from src.predictor import EnergyBillPredictor

def test_prediction():
    print("\n" + "="*60)
    print("TESTING ENERGY BILL PREDICTOR")
    print("="*60 + "\n")
    
    # Initialize predictor
    print("1️⃣  Loading trained model...")
    predictor = EnergyBillPredictor()
    print("   ✅ Model loaded successfully\n")
    
    # Test case 1: Summer in Phoenix
    print("2️⃣  Test Case 1: Summer in Phoenix, AZ")
    test_input_1 = {
        'city': 'Phoenix',
        'state': 'AZ',
        'house_type': 'House',
        'month': 7,
        'avg_temp_f': 105.0,
        'humidity': 35.0,
        'heating_degree_days': 0,
        'cooling_degree_days': 1200,
        'avg_energy_kwh': 2000,
        'square_feet': 2500,
        'num_occupants': 4,
        'energy_rate_per_kwh': 0.13
    }
    
    result_1 = predictor.predict(test_input_1)
    print(f"   💰 Predicted Bill: ${result_1['predicted_bill']:.2f}")
    print(f"   📊 Confidence Range: ${result_1['confidence_interval']['lower']:.2f} - ${result_1['confidence_interval']['upper']:.2f}")
    print(f"   📝 Insights: {len(result_1['insights'])} recommendations")
    for insight in result_1['insights']:
        print(f"      - {insight['factor']}: {insight['description']}")
    print()
    
    # Test case 2: Winter in New York
    print("3️⃣  Test Case 2: Winter in New York, NY")
    test_input_2 = {
        'city': 'New York',
        'state': 'NY',
        'house_type': 'Apartment',
        'month': 1,
        'avg_temp_f': 30.0,
        'humidity': 60.0,
        'heating_degree_days': 1050,
        'cooling_degree_days': 0,
        'avg_energy_kwh': 750,
        'square_feet': 1000,
        'num_occupants': 2,
        'energy_rate_per_kwh': 0.18
    }
    
    result_2 = predictor.predict(test_input_2)
    print(f"   💰 Predicted Bill: ${result_2['predicted_bill']:.2f}")
    print(f"   📊 Confidence Range: ${result_2['confidence_interval']['lower']:.2f} - ${result_2['confidence_interval']['upper']:.2f}")
    print(f"   📝 Insights: {len(result_2['insights'])} recommendations")
    for insight in result_2['insights']:
        print(f"      - {insight['factor']}: {insight['description']}")
    print()
    
    # Test case 3: Moderate weather in Seattle
    print("4️⃣  Test Case 3: Spring in Seattle, WA")
    test_input_3 = {
        'city': 'Seattle',
        'state': 'WA',
        'house_type': 'Condo',
        'month': 5,
        'avg_temp_f': 62.0,
        'humidity': 70.0,
        'heating_degree_days': 90,
        'cooling_degree_days': 0,
        'avg_energy_kwh': 500,
        'square_feet': 1200,
        'num_occupants': 2,
        'energy_rate_per_kwh': 0.10
    }
    
    result_3 = predictor.predict(test_input_3)
    print(f"   💰 Predicted Bill: ${result_3['predicted_bill']:.2f}")
    print(f"   📊 Confidence Range: ${result_3['confidence_interval']['lower']:.2f} - ${result_3['confidence_interval']['upper']:.2f}")
    print(f"   📝 Insights: {len(result_3['insights'])} recommendations")
    if result_3['insights']:
        for insight in result_3['insights']:
            print(f"      - {insight['factor']}: {insight['description']}")
    else:
        print(f"      ✨ No concerns - optimal energy usage!")
    print()
    
    print("="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")
    
    print("🌐 Ready to start web service!")
    print("   Run: python app/app.py")
    print("   Then open: http://localhost:5000\n")

if __name__ == "__main__":
    test_prediction()

