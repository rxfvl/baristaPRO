import sys
import pandas as pd
import numpy as np

sys.path.append(r"c:\Users\minec\Desktop\baristaPRO")

from logic.ai.flavor_predictor import flavor_predictor

def verify():
    print("Iniciando entrenamiento del Flavor Predictor...")
    # Pasamos un dataframe dummy de usuario para que no falle la comprobacion
    dummy_real = pd.DataFrame({
        "variety": ["Gesha / Geisha", "Bourbon", "Caturra"],
        "process": ["Washed", "Natural", "Honey"],
        "origin_country": ["Panama", "Brazil", "Colombia"],
        "altitude_masl": [1800, 1100, 1500],
        "days_since_roast": [14, 10, 12],
        "notes": ["floral, jazmín, miel", "chocolate, cacao, pesado", "caramelo, equilibrado"],
        "acidity": [8, 3, 6],
        "sweetness": [8, 8, 7],
        "body": [4, 8, 6],
        "bitterness": [3, 6, 4]
    })
    
    flavor_predictor.train(dummy_real)
    print("Entrenamiento completado y guardado.")
    
    print("\n--- PRUEBAS DE PREDICCIÓN ---")
    
    # 1. Bean sin notas
    bean1 = {
        "variety": "Yellow Catuai",
        "process": "Natural",
        "origin_country": "Brazil",
        "altitude_masl": 1100,
        "days_since_roast": 10,
        "notes": ""
    }
    pred1 = flavor_predictor.predict(bean1)
    print("\nGrano 1 (Brasil Natural, SIN notas):")
    print(pred1)
    
    # 2. Mismo grano con notas de acidez (debería engañar un poco al modelo si aprendió NLP)
    bean2 = {
        "variety": "Yellow Catuai",
        "process": "Natural",
        "origin_country": "Brazil",
        "altitude_masl": 1100,
        "days_since_roast": 10,
        "notes": "cítrico, limón, brillante, alta acidez"
    }
    pred2 = flavor_predictor.predict(bean2)
    print("\nGrano 2 (Brasil Natural, CON notas críticas):")
    print(pred2)
    
    # 3. Grano etíope lavado floral
    bean3 = {
        "variety": "Heirloom",
        "process": "Washed",
        "origin_country": "Ethiopia",
        "altitude_masl": 2100,
        "days_since_roast": 14,
        "notes": "floral, jazmín, té de melocotón"
    }
    pred3 = flavor_predictor.predict(bean3)
    print("\nGrano 3 (Etiopía Lavado, CON notas florales):")
    print(pred3)

if __name__ == "__main__":
    verify()
