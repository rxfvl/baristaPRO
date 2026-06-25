# BaristaPRO ☕

BaristaPRO es una solución integral para entusiastas y profesionales del café. Permite llevar un registro detallado del inventario de granos, extraer el máximo potencial de cada café a través del análisis de datos y perfiles de sabor, y asistir al barista en tiempo real mediante Inteligencia Artificial.

El ecosistema BaristaPRO está compuesto por 3 componentes principales:

## 1. Aplicación Móvil (`/mobile_app`)
Aplicación desarrollada en React Native (Expo) que permite a los baristas llevar el control de sus extracciones y registrar nuevos granos desde cualquier lugar.
- **Tecnologías:** React Native, Expo.
- **Funcionalidades:** Multi-idioma (i18n), Registro de granos y lotes, Dial-In Journal, Consulta de IA.

## 2. Servidor Backend (`/backend`)
API REST centralizada que conecta las aplicaciones y procesa las peticiones de Inteligencia Artificial.
- **Tecnologías:** FastAPI, PostgreSQL, Scikit-Learn.
- **Despliegue:** Preparado para Docker (`docker-compose.yml`) y Oracle Cloud.
- **Modelos de IA:** Los modelos `.joblib` se ejecutan aquí, proporcionando predicciones de sabor y sugerencias de extracción (Shot Advisor).

## 3. Aplicación de Escritorio (`/ui`, `/logic`)
La aplicación original de escritorio de BaristaPRO, construida para análisis profundo y gestión avanzada en un monitor grande.
- **Tecnologías:** Python, CustomTkinter, Pandas.
- **Funcionalidades:** Laboratorio de Agua, Simulador de Desgasificación, Gestión completa de inventario.

## 🧠 Modelos de Inteligencia Artificial
BaristaPRO incorpora dos modelos de Machine Learning (Random Forest) entrenados con datos sintéticos y reales de cata:

- **Flavor Predictor (`flavor_predictor.joblib`):** Analiza un grano (origen, altitud, proceso, nivel de tueste) y predice su perfil sensorial esperado en radar (Acidez, Dulzor, Cuerpo, Notas frutales/florales/chocolate).
- **Shot Advisor (`shot_advisor.joblib`):** *Sensory-Driven AI*. Analiza tu última receta de extracción (dosis, yield, molienda) junto con tu evaluación sensorial (si estaba ácido, amargo o aguado), y te devuelve instrucciones precisas de barista (ej. "Afina la molienda" o "Acorta el yield") para buscar el "Sweet Spot".

---
*Developed for coffee lovers.*
