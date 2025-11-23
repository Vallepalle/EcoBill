import pandas as pd
import numpy as np
from src.model_trainer import EnergyBillModelTrainer

class EnergyBillPredictor:
    """Make predictions using trained model"""
    
    def __init__(self, model_dir='models'):
        self.trainer = EnergyBillModelTrainer()
        self.trainer.load_model(model_dir)
    
    def predict(self, input_data):
        """
        Predict energy bill
        
        Args:
            input_data: dict or DataFrame with features
        
        Returns:
            dict with prediction and insights
        """
        if isinstance(input_data, dict):
            df = pd.DataFrame([input_data])
        else:
            df = input_data.copy()
        
        # Prepare features
        X = self.trainer.prepare_features(df, fit=False)
        
        # Make prediction
        prediction = self.trainer.model.predict(X)[0]
        
        # Get prediction interval (using standard deviation of trees)
        tree_predictions = np.array([tree.predict(X)[0] 
                                     for tree in self.trainer.model.estimators_])
        std = np.std(tree_predictions)
        lower_bound = prediction - 1.96 * std
        upper_bound = prediction + 1.96 * std
        
        # Generate insights
        insights = self.generate_insights(df.iloc[0], prediction)
        
        return {
            'predicted_bill': round(prediction, 2),
            'confidence_interval': {
                'lower': round(max(0, lower_bound), 2),
                'upper': round(upper_bound, 2)
            },
            'insights': insights
        }
    
    def generate_insights(self, input_data, predicted_bill):
        """Generate actionable insights"""
        insights = []
        
        # Temperature-based insights
        if input_data['avg_temp_f'] > 85:
            insights.append({
                'factor': 'High Temperature',
                'impact': 'Increasing',
                'description': f'Temperature of {input_data["avg_temp_f"]}°F increases cooling costs',
                'recommendation': 'Use programmable thermostats and ceiling fans to reduce AC usage'
            })
        elif input_data['avg_temp_f'] < 40:
            insights.append({
                'factor': 'Low Temperature',
                'impact': 'Increasing',
                'description': f'Temperature of {input_data["avg_temp_f"]}°F increases heating costs',
                'recommendation': 'Improve insulation and use smart heating schedules'
            })
        
        # Usage-based insights
        kwh_per_sqft = input_data['avg_energy_kwh'] / input_data['square_feet']
        if kwh_per_sqft > 1.5:
            insights.append({
                'factor': 'High Energy Intensity',
                'impact': 'Increasing',
                'description': f'Using {kwh_per_sqft:.2f} kWh per sq ft (above average)',
                'recommendation': 'Consider energy audit and upgrade to LED lights'
            })
        
        # Rate-based insights
        if input_data['energy_rate_per_kwh'] > 0.18:
            insights.append({
                'factor': 'High Energy Rate',
                'impact': 'Increasing',
                'description': f'Rate of ${input_data["energy_rate_per_kwh"]}/kWh is above national average',
                'recommendation': 'Check if time-of-use rates are available in your area'
            })
        
        # House type insights
        if input_data['house_type'] in ['House', 'Large House']:
            insights.append({
                'factor': 'Large Home',
                'impact': 'Increasing',
                'description': f'{input_data["house_type"]} ({input_data["square_feet"]} sq ft) requires more energy',
                'recommendation': 'Zone heating/cooling and upgrade to energy-efficient appliances'
            })
        
        return insights
    
    def batch_predict(self, input_df):
        """Predict for multiple inputs"""
        results = []
        for idx, row in input_df.iterrows():
            result = self.predict(row.to_dict())
            result['input'] = row.to_dict()
            results.append(result)
        return results

if __name__ == "__main__":
    # Example prediction
    predictor = EnergyBillPredictor()
    
    sample_input = {
        'city': 'New York',
        'state': 'NY',
        'house_type': 'Apartment',
        'month': 7,
        'avg_temp_f': 82.5,
        'humidity': 65.0,
        'heating_degree_days': 0,
        'cooling_degree_days': 525,
        'avg_energy_kwh': 850,
        'square_feet': 1000,
        'num_occupants': 2,
        'energy_rate_per_kwh': 0.18
    }
    
    result = predictor.predict(sample_input)
    print(f"\n💰 Predicted Bill: ${result['predicted_bill']}")
    print(f"📊 Confidence Interval: ${result['confidence_interval']['lower']} - ${result['confidence_interval']['upper']}")

