import pandas as pd
from logic.ai.flavor_predictor import flavor_predictor

# Initialise model
flavor_predictor.load()
if not flavor_predictor._trained:
    flavor_predictor.train(None)

# Create test dataset of real-world specialty coffee archetypes
dataset = [
    {
        "name": "Ethiopia Yirgacheffe",
        "roaster": "Onyx Coffee Lab",
        "variety": "Heirloom",
        "process": "Lavado / Washed",
        "origin_country": "Ethiopia",
        "altitude_masl": 2000,
        "days_since_roast": 14,
        "notes": "jazmín, limón, té negro, bergamota, floral", # jasmine, lemon, black tea, bergamot, floral
        "expected_profile": "High Acidity, Low Body, Floral/Citric"
    },
    {
        "name": "Brazil Cerrado Mineiro",
        "roaster": "Square Mile",
        "variety": "Mundo Novo",
        "process": "Natural",
        "origin_country": "Brazil",
        "altitude_masl": 1100,
        "days_since_roast": 21,
        "notes": "chocolate negro, avellana, caramelo, dulce", # dark chocolate, hazelnut, caramel, sweet
        "expected_profile": "Low Acidity, High Sweetness, Full Body"
    },
    {
        "name": "Colombia Huila El Bombo",
        "roaster": "Sey Coffee",
        "variety": "Caturra",
        "process": "Lavado / Washed",
        "origin_country": "Colombia",
        "altitude_masl": 1750,
        "days_since_roast": 10,
        "notes": "manzana roja, panela, limpio, redondo", # red apple, panela (raw sugar), clean, round
        "expected_profile": "Balanced, Med-High Sweetness, Clean"
    },
    {
        "name": "Costa Rica Tarrazu",
        "roaster": "Intelligentsia",
        "variety": "Catuai",
        "process": "Honey",
        "origin_country": "Costa Rica",
        "altitude_masl": 1500,
        "days_since_roast": 15,
        "notes": "miel, vainilla, almendra, suave", # honey, vanilla, almond, smooth
        "expected_profile": "High Sweetness, Medium Body, Smooth"
    },
    {
        "name": "Panama Boquete Hacienda La Esmeralda",
        "roaster": "George Howell",
        "variety": "Gesha / Geisha",
        "process": "Lavado / Washed",
        "origin_country": "Panama",
        "altitude_masl": 1650,
        "days_since_roast": 12,
        "notes": "jazmín, melocotón, miel, brillante, floral", # jasmine, peach, honey, bright, floral
        "expected_profile": "Very High Acidity, High Sweetness, Low Body"
    },
    {
        "name": "Sumatra Mandheling",
        "roaster": "Stumptown",
        "variety": "Typica",
        "process": "Natural", # Wet-hulled usually, mapping to natural/earthy
        "origin_country": "Indonesia",
        "altitude_masl": 1300,
        "days_since_roast": 25,
        "notes": "terroso, madera, tabaco, chocolate oscuro, especias", # earthy, wood, tobacco, dark chocolate, spice
        "expected_profile": "Low Acidity, Very High Body, Earthy/Bitter"
    }
]

print("=== EVALUATION OF FLAVOR PREDICTOR AGAINST REAL-WORLD BEANS ===")
print("-" * 80)

results = []
for bean in dataset:
    pred = flavor_predictor.predict(bean)
    results.append({
        "Café": f"{bean['name']} ({bean['origin_country']})",
        "Variedad": bean['variety'],
        "Proceso": bean['process'],
        "Notas": bean['notes'],
        "Acidez": pred['acidity'],
        "Dulzor": pred['sweetness'],
        "Cuerpo": pred['body'],
        "Amargor": pred['bitterness']
    })
    
    print(f"[Bean] {bean['name']} ({bean['roaster']})")
    print(f"   Origen: {bean['origin_country']} | {bean['altitude_masl']}m | {bean['process']} | {bean['variety']}")
    print(f"   Notas de cata: {bean['notes']}")
    print(f"   Expectativa: {bean['expected_profile']}")
    print(f"   Predicción IA:")
    print(f"      Acidez:  {pred['acidity']:<4} {'*' * int(pred['acidity'])}")
    print(f"      Dulzor:  {pred['sweetness']:<4} {'*' * int(pred['sweetness'])}")
    print(f"      Cuerpo:  {pred['body']:<4} {'*' * int(pred['body'])}")
    print(f"      Amargor: {pred['bitterness']:<4} {'*' * int(pred['bitterness'])}")
    print("-" * 80)

df = pd.DataFrame(results)
df.to_csv("test_dataset_results.csv", index=False)
print("Resultados exportados a test_dataset_results.csv")
