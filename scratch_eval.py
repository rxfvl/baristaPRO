import pandas as pd
import numpy as np
import sys
import os

from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_validate

sys.path.append(r"c:\Users\minec\Desktop\baristaPRO")

from logic.ai.flavor_predictor import bean_to_features

def evaluate_models():
    print("Cargando dataset...")
    df = pd.read_csv(r"c:\Users\minec\Desktop\baristaPRO\archive\arabica_data_cleaned.csv")
    
    # Filtrar columnas y limpiar
    df = df.dropna(subset=['Country.of.Origin', 'Processing.Method', 'Variety', 'altitude_mean_meters', 'Acidity', 'Sweetness', 'Body'])
    
    X_features = []
    y_targets = []
    
    print(f"Total registros limpios: {len(df)}")
    
    for _, row in df.iterrows():
        try:
            feats = bean_to_features(
                variety=row['Variety'],
                process=row['Processing.Method'],
                country=row['Country.of.Origin'],
                altitude=float(row['altitude_mean_meters']),
                days=14.0 # Default since CQI doesn't have it
            )
            # Acidity, Sweetness, Body (we omit bitterness for now as CQI doesn't map cleanly)
            targets = [float(row['Acidity']), float(row['Sweetness']), float(row['Body'])]
            
            X_features.append(feats)
            y_targets.append(targets)
        except Exception as e:
            continue
            
    X = np.array(X_features)
    y = np.array(y_targets)
    
    # 1. MLP (Red Neuronal) - Configuración actual de BaristaPRO
    mlp_model = Pipeline([
        ("scaler", StandardScaler()),
        ("mlp", MLPRegressor(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            max_iter=1000,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=30,
        )),
    ])
    
    # 2. Random Forest Regressor - Propuesto
    rf_model = Pipeline([
        ("scaler", StandardScaler()), # RF doesn't strictly need it, but good for comparison
        ("rf", RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))
    ])
    
    print("Evaluando Red Neuronal (MLP) mediante 5-Fold CV...")
    mlp_scores = cross_validate(mlp_model, X, y, cv=5, scoring='neg_mean_squared_error', return_train_score=False)
    mlp_mse = -np.mean(mlp_scores['test_score'])
    
    print("Evaluando Random Forest Regressor mediante 5-Fold CV...")
    rf_scores = cross_validate(rf_model, X, y, cv=5, scoring='neg_mean_squared_error', return_train_score=False)
    rf_mse = -np.mean(rf_scores['test_score'])
    
    print("-" * 30)
    print("RESULTADOS (Error Cuadrático Medio - MSE, menor es mejor):")
    print(f"Red Neuronal (MLPRegressor): {mlp_mse:.4f}")
    print(f"Random Forest Regressor:     {rf_mse:.4f}")
    
    if rf_mse < mlp_mse:
        print("\nConclusión: Random Forest es MEJOR (tiene menor error) para este dataset real.")
    else:
        print("\nConclusión: La Red Neuronal (MLP) es MEJOR (tiene menor error) para este dataset real.")

if __name__ == "__main__":
    evaluate_models()
