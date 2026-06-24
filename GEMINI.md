# Guía de Desarrollo para Agentes: BaristaPRO

¡Hola, próximo agente! 👋 Estás trabajando en **BaristaPRO**, una solución para baristas compuesta por una aplicación de escritorio, un servidor backend y una aplicación móvil. Esta guía te pondrá al día rápidamente con el estado actual del proyecto, la arquitectura, y las convenciones a seguir.

## 📁 Estructura del Proyecto

El repositorio está dividido en 3 partes principales:

1. **Desktop App (Raíz / `ui` / `logic`)**: Aplicación de escritorio original. Usa `CustomTkinter` para la UI. Anteriormente usaba `SQLite` local, pero actualmente está **en desuso** a favor de la nube.
2. **Backend (`/backend`)**: Servidor API construido con `FastAPI` y base de datos `PostgreSQL`. Está desplegado en Oracle Cloud mediante Docker.
3. **Mobile App (`/mobile_app`)**: Aplicación cliente desarrollada con `React Native` (Expo) para iOS/Android/Web.

## 🧠 Estado de Desarrollo Actual

Hasta el último punto de guardado, se ha logrado lo siguiente:

- Se ha migrado y sincronizado el sistema de usuarios, granos y extracciones del servidor backend a la aplicación móvil.
- **Integración de IA en la Nube**: Los modelos predictivos de Machine Learning (`FlavorPredictor` y `ShotAdvisor`) que antes solo existían en la app de escritorio se han trasladado con éxito al backend (`backend/ai`).
- La aplicación móvil ahora permite invocar predicciones de sabor ("✨ Predecir Sabor") sobre los granos existentes (enviando el `bean_id` al backend para cargar el contexto completo, incluidas las notas y fechas de tueste) y obtener sugerencias de marcaje del molino/receta ("✨ Consultar Shot Advisor") desde `AddExtractionScreen`.

## 📌 Reglas y Convenciones Importantes

1. **Base de Datos Unificada (PostgreSQL)**: 
   - Tanto la aplicación de **escritorio** como la aplicación **móvil** (a través de la API) se conectan a la misma base de datos *PostgreSQL* remota. La base de datos local antigua en SQLite (`barista_pro.db`) está totalmente **en desuso**.
2. **Despliegue del Servidor**:
   - Siempre que modifiques el código dentro de `backend/`, **debes redesplegar** el servidor. 
   - Usa el script `deploy.ps1` en la raíz (ej. `.\deploy.ps1`). Este script sincroniza el código vía `scp` a la instancia de Oracle Cloud y ejecuta un `docker-compose up --build -d` para reconstruir la imagen de la API y aplicar los cambios.
3. **Modelos de Inteligencia Artificial (.joblib)**:
   - Los modelos pre-entrenados del escritorio (`flavor_predictor.joblib` y `shot_advisor.joblib`) se encuentran en la carpeta raíz `models/`. 
   - Para que el backend los use, deben copiarse manualmente al servidor o enviarlos si el escritorio los re-entrena. Recientemente se han cargado las últimas versiones directamente a `~/barista_backend/backend/ai/` en el servidor.
4. **React Native (Expo)**:
   - Para evitar bloqueos graves y crashes de la librería `react-navigation` en Expo Web, la navegación móvil *no usa menús de pestañas (Tab.Navigator) habituales*. 
   - Usamos en su lugar un componente custom **`BottomNavBar.js`** que debes instanciar manualmente al final de cada pantalla, y se usa la navegación de tipo pila (`Stack.Navigator`). **NO uses Bottom Tab Navigators de `react-navigation`**.

## 🚀 Siguientes Pasos (Roadmap)

Al retomar el desarrollo, podrías considerar abordar los siguientes puntos pendientes:

1. **Generación de la APK/AAB**:
   - Compilar la app de Expo para Android (o iOS) para publicarla en la Play Store o instalarla de forma nativa.
2. **Mejoras del UI/UX Móvil**:
   - Validar y testear los colores corporativos y garantizar que todos los inputs e interfaces respetan el tema oscuro con detalles en el color principal (morado).
3. **Traducción y Configuración de Perfil**:
   - Completar las pantallas de Preferencias y Perfil en el móvil para que coincidan con la profundidad que ofrece el escritorio.

¡Disfruta desarrollando! ☕
