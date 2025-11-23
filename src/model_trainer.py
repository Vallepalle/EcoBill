import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import json

class EnergyBillModelTrainer:
    """Train Random Forest model for energy bill prediction"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = None
        self.categorical_features = ['city', 'state', 'house_type']
        self.numerical_features = [
            'month', 'avg_temp_f', 'humidity', 'heating_degree_days',
            'cooling_degree_days', 'avg_energy_kwh', 'square_feet',
            'num_occupants', 'energy_rate_per_kwh'
        ]
    
    def load_data(self, filepath='data/synthetic_data.csv'):
        """Load training data"""
        self.df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(self.df)} samples from {filepath}")
        return self.df
    
    def engineer_features(self, df):
        """Create additional features"""
        df = df.copy()
        
        # Seasonal features (cyclical encoding)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Per-capita metrics
        df['kwh_per_occupant'] = df['avg_energy_kwh'] / df['num_occupants']
        df['kwh_per_sqft'] = df['avg_energy_kwh'] / df['square_feet']
        
        # Temperature extremes
        df['is_extreme_cold'] = (df['avg_temp_f'] < 40).astype(int)
        df['is_extreme_hot'] = (df['avg_temp_f'] > 85).astype(int)
        
        # Total degree days
        df['total_degree_days'] = df['heating_degree_days'] + df['cooling_degree_days']
        
        # Estimated base cost
        df['estimated_cost'] = df['avg_energy_kwh'] * df['energy_rate_per_kwh']
        
        return df
    
    def prepare_features(self, df, fit=True):
        """Encode categorical and scale numerical features"""
        df = self.engineer_features(df)
        X = df.copy()
        
        # Encode categorical features
        for col in self.categorical_features:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                X[col] = self.label_encoders[col].fit_transform(X[col])
            else:
                X[col] = self.label_encoders[col].transform(X[col])
        
        # Define all feature columns
        feature_cols = (self.categorical_features + self.numerical_features + 
                       ['month_sin', 'month_cos', 'kwh_per_occupant', 'kwh_per_sqft',
                        'is_extreme_cold', 'is_extreme_hot', 'total_degree_days',
                        'estimated_cost'])
        
        if fit:
            self.feature_names = feature_cols
        
        X = X[feature_cols]
        
        # Scale numerical features
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def train(self, test_size=0.2, random_state=42):
        """Train the Random Forest model"""
        print("\n🔧 Preparing features...")
        X = self.prepare_features(self.df, fit=True)
        y = self.df['monthly_energy_bill'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        print(f"📊 Training set: {len(X_train)} samples")
        print(f"📊 Test set: {len(X_test)} samples")
        
        # Train model
        print("\n🤖 Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
            verbose=1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        print("\n📈 Evaluating model...")
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        metrics = {
            'train': {
                'mae': mean_absolute_error(y_train, train_pred),
                'rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                'r2': r2_score(y_train, train_pred),
                'mape': np.mean(np.abs((y_train - train_pred) / y_train)) * 100
            },
            'test': {
                'mae': mean_absolute_error(y_test, test_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                'r2': r2_score(y_test, test_pred),
                'mape': np.mean(np.abs((y_test - test_pred) / y_test)) * 100
            }
        }
        
        self.print_metrics(metrics)
        self.metrics = metrics
        
        return metrics
    
    def print_metrics(self, metrics):
        """Print evaluation metrics"""
        print("\n" + "="*60)
        print("MODEL PERFORMANCE METRICS")
        print("="*60)
        
        for dataset in ['train', 'test']:
            print(f"\n{dataset.upper()} SET:")
            print(f"  Mean Absolute Error (MAE):  ${metrics[dataset]['mae']:.2f}")
            print(f"  Root Mean Squared Error:     ${metrics[dataset]['rmse']:.2f}")
            print(f"  R² Score:                    {metrics[dataset]['r2']:.4f}")
            print(f"  Mean Absolute % Error:       {metrics[dataset]['mape']:.2f}%")
        
        print("\n" + "="*60)
    
    def get_feature_importance(self, top_n=10):
        """Get feature importance"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        print(f"\n🔍 Top {top_n} Most Important Features:")
        print("-" * 50)
        for i, idx in enumerate(indices, 1):
            print(f"{i:2d}. {self.feature_names[idx]:25s} {importances[idx]:.4f}")
        
        return list(zip([self.feature_names[i] for i in indices], 
                       importances[indices]))
    
    def save_model(self, model_dir='models'):
        """Save trained model and preprocessing objects"""
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(model_dir, 'random_forest_model.pkl')
        joblib.dump(self.model, model_path)
        print(f"✅ Model saved to {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        print(f"✅ Scaler saved to {scaler_path}")
        
        # Save label encoders
        encoders_path = os.path.join(model_dir, 'label_encoders.pkl')
        joblib.dump(self.label_encoders, encoders_path)
        print(f"✅ Label encoders saved to {encoders_path}")
        
        # Save feature names and metrics
        metadata = {
            'feature_names': self.feature_names,
            'categorical_features': self.categorical_features,
            'numerical_features': self.numerical_features,
            'metrics': self.metrics
        }
        metadata_path = os.path.join(model_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved to {metadata_path}")
    
    def load_model(self, model_dir='models'):
        """Load trained model and preprocessing objects"""
        model_path = os.path.join(model_dir, 'random_forest_model.pkl')
        self.model = joblib.load(model_path)
        
        scaler_path = os.path.join(model_dir, 'scaler.pkl')
        self.scaler = joblib.load(scaler_path)
        
        encoders_path = os.path.join(model_dir, 'label_encoders.pkl')
        self.label_encoders = joblib.load(encoders_path)
        
        metadata_path = os.path.join(model_dir, 'metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.feature_names = metadata['feature_names']
        self.categorical_features = metadata['categorical_features']
        self.numerical_features = metadata['numerical_features']
        
        print("✅ Model and preprocessing objects loaded successfully")

if __name__ == "__main__":
    # Train the model
    trainer = EnergyBillModelTrainer()
    trainer.load_data()
    trainer.train()
    trainer.get_feature_importance()
    trainer.save_model()

