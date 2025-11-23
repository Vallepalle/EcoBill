import pandas as pd
import numpy as np
from datetime import datetime
import random

class SyntheticDataGenerator:
    """Generate synthetic energy bill data for training"""
    
    def __init__(self, n_samples=10000, random_state=42):
        self.n_samples = n_samples
        np.random.seed(random_state)
        random.seed(random_state)
        
        # Define possible values
        self.cities = {
            'New York': {'state': 'NY', 'base_rate': 0.18, 'climate': 'cold'},
            'Los Angeles': {'state': 'CA', 'base_rate': 0.22, 'climate': 'moderate'},
            'Chicago': {'state': 'IL', 'base_rate': 0.14, 'climate': 'cold'},
            'Houston': {'state': 'TX', 'base_rate': 0.12, 'climate': 'hot'},
            'Phoenix': {'state': 'AZ', 'base_rate': 0.13, 'climate': 'hot'},
            'Miami': {'state': 'FL', 'base_rate': 0.11, 'climate': 'hot'},
            'Seattle': {'state': 'WA', 'base_rate': 0.10, 'climate': 'moderate'},
            'Boston': {'state': 'MA', 'base_rate': 0.21, 'climate': 'cold'},
            'Denver': {'state': 'CO', 'base_rate': 0.12, 'climate': 'moderate'},
            'Atlanta': {'state': 'GA', 'base_rate': 0.13, 'climate': 'moderate'}
        }
        
        self.house_types = {
            'Apartment': {'size_range': (500, 1200), 'efficiency': 1.0},
            'Condo': {'size_range': (800, 1600), 'efficiency': 1.1},
            'Townhouse': {'size_range': (1200, 2200), 'efficiency': 1.2},
            'House': {'size_range': (1500, 3500), 'efficiency': 1.3},
            'Large House': {'size_range': (3000, 5000), 'efficiency': 1.5}
        }
        
        # Monthly weather patterns
        self.monthly_temp = {
            'cold': [28, 32, 42, 54, 65, 74, 79, 77, 69, 57, 45, 33],
            'moderate': [45, 48, 52, 58, 64, 71, 75, 74, 70, 62, 54, 47],
            'hot': [62, 65, 70, 76, 82, 88, 92, 91, 87, 80, 71, 64]
        }
    
    def generate_data(self):
        """Generate synthetic dataset"""
        data = []
        
        for _ in range(self.n_samples):
            # Random selections
            city = random.choice(list(self.cities.keys()))
            city_info = self.cities[city]
            house_type = random.choice(list(self.house_types.keys()))
            house_info = self.house_types[house_type]
            month = random.randint(1, 12)
            
            # House characteristics
            square_feet = random.randint(*house_info['size_range'])
            num_occupants = random.randint(1, min(6, int(square_feet / 500)))
            
            # Weather data
            climate = city_info['climate']
            base_temp = self.monthly_temp[climate][month - 1]
            avg_temp_f = base_temp + random.uniform(-5, 5)
            humidity = random.uniform(30, 90)
            
            # Degree days (simplified)
            heating_degree_days = max(0, (65 - avg_temp_f) * 30)
            cooling_degree_days = max(0, (avg_temp_f - 65) * 30)
            
            # Energy consumption calculation
            base_usage = square_feet * 0.8  # Base load
            heating_usage = heating_degree_days * square_feet * 0.05
            cooling_usage = cooling_degree_days * square_feet * 0.04
            occupant_usage = num_occupants * 100
            
            avg_energy_kwh = (base_usage + heating_usage + cooling_usage + 
                            occupant_usage) * house_info['efficiency']
            avg_energy_kwh += random.uniform(-100, 100)  # Add noise
            avg_energy_kwh = max(200, avg_energy_kwh)  # Minimum usage
            
            # Energy rate with seasonal variation
            energy_rate = city_info['base_rate']
            if month in [6, 7, 8]:  # Summer peak
                energy_rate *= 1.2
            elif month in [12, 1, 2]:  # Winter peak
                energy_rate *= 1.1
            
            # Calculate bill
            monthly_bill = avg_energy_kwh * energy_rate
            monthly_bill += random.uniform(-20, 20)  # Add noise
            monthly_bill = max(50, monthly_bill)  # Minimum bill
            
            data.append({
                'city': city,
                'state': city_info['state'],
                'house_type': house_type,
                'month': month,
                'avg_temp_f': round(avg_temp_f, 1),
                'humidity': round(humidity, 1),
                'heating_degree_days': round(heating_degree_days, 1),
                'cooling_degree_days': round(cooling_degree_days, 1),
                'avg_energy_kwh': round(avg_energy_kwh, 1),
                'square_feet': square_feet,
                'num_occupants': num_occupants,
                'energy_rate_per_kwh': round(energy_rate, 3),
                'monthly_energy_bill': round(monthly_bill, 2)
            })
        
        return pd.DataFrame(data)
    
    def save_data(self, filepath='data/synthetic_data.csv'):
        """Generate and save dataset"""
        df = self.generate_data()
        df.to_csv(filepath, index=False)
        print(f"✅ Generated {len(df)} samples and saved to {filepath}")
        print(f"\nDataset Summary:")
        print(df.describe())
        return df

if __name__ == "__main__":
    generator = SyntheticDataGenerator(n_samples=10000)
    df = generator.save_data()

