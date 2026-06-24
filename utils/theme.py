# utils/theme.py — Design tokens for EspressoLab
# All colors, fonts, and style constants in one place.

COLORS = {
    "bg_primary":    "#0D0D0D",
    "bg_secondary":  "#161616",
    "bg_card":       "#1E1E1E",
    "bg_card_hover": "#262626",
    "bg_input":      "#242424",
    "accent":        "#C8873A",
    "accent_hover":  "#DFA050",
    "accent_dark":   "#7A4E1A",
    "success":       "#4CAF6E",
    "success_dim":   "#1E3D28",
    "warning":       "#E8A838",
    "warning_dim":   "#3D2E0E",
    "danger":        "#E05C5C",
    "danger_dim":    "#3D1010",
    "info":          "#5B9BD5",
    "text_primary":  "#F0EDE8",
    "text_secondary":"#BDB8B2",
    "text_muted":    "#7A7570",
    "border":        "#2A2A2A",
    "border_focus":  "#C8873A",
    "surface":       "#2A2A2A",
    "sidebar_bg":    "#111111",
    "sidebar_hover": "#1E1E1E",
    "sidebar_active":"#C8873A",
}

FONTS = {
    "display":  ("Segoe UI", 32, "bold"),
    "h2":       ("Segoe UI", 24, "bold"),
    "heading":  ("Segoe UI", 20, "bold"),
    "subhead":  ("Segoe UI", 16, "bold"),
    "body":     ("Segoe UI", 14, "normal"),
    "small":    ("Segoe UI", 12, "normal"),
    "button":   ("Segoe UI", 14, "bold"),
    "label":    ("Segoe UI", 13, "normal"),
    "mono":     ("Consolas", 14, "normal"),
    "caption":  ("Segoe UI", 11, "normal"),
}

CORNER_RADIUS = {
    "card":   12,
    "button": 8,
    "input":  6,
    "badge":  20,
}

PADDING = {
    "card":   16,
    "section":24,
    "element":8,
}

SIDEBAR_WIDTH = 260

# Bilingual label dictionary (ES / EN)
LABELS = {
    # Navigation
    "nav_dashboard":    {"es": "Dashboard",      "en": "Dashboard"},
    "nav_beans":        {"es": "Granos",          "en": "Beans"},
    "nav_journal":      {"es": "Bitácora",        "en": "Journal"},
    "nav_water":        {"es": "Agua",            "en": "Water Lab"},
    "nav_equipment":    {"es": "Equipo",          "en": "Equipment"},
    "nav_settings":     {"es": "Ajustes",         "en": "Settings"},
    "settings":         {"es": "Ajustes",         "en": "Settings"},

    # Bean fields
    "bean_roaster":     {"es": "Tostador",        "en": "Roaster"},
    "bean_name":        {"es": "Nombre del Café", "en": "Coffee Name"},
    "bean_country":     {"es": "País",            "en": "Country"},
    "bean_region":      {"es": "Región",          "en": "Region"},
    "bean_farm":        {"es": "Finca",           "en": "Farm"},
    "bean_variety":     {"es": "Variedad",        "en": "Variety"},
    "bean_process":     {"es": "Proceso",         "en": "Process"},
    "bean_altitude":    {"es": "Altura (msnm)",   "en": "Altitude (masl)"},
    "bean_roast_date":  {"es": "Fecha Tueste",    "en": "Roast Date"},
    "bean_stock":       {"es": "Stock (g)",       "en": "Stock (g)"},
    "bean_rest_days":   {"es": "Días Reposo",     "en": "Rest Days"},

    # Extraction
    "ext_dose":         {"es": "Dosis (g)",       "en": "Dose (g)"},
    "ext_yield":        {"es": "Rendimiento (g)",  "en": "Yield (g)"},
    "ext_ratio":        {"es": "Ratio",           "en": "Ratio"},
    "ext_time":         {"es": "Tiempo (s)",      "en": "Time (s)"},
    "ext_temp":         {"es": "Temperatura (°C)","en": "Temp (°C)"},
    "ext_grind":        {"es": "Molida",          "en": "Grind"},
    "ext_pressure":     {"es": "Presión (bar)",   "en": "Pressure (bar)"},
    "ext_preinfusion":  {"es": "Pre-infusión (s)","en": "Pre-infusion (s)"},
    "ext_acidity":      {"es": "Acidez",          "en": "Acidity"},
    "ext_sweetness":    {"es": "Dulzor",          "en": "Sweetness"},
    "ext_body":         {"es": "Cuerpo",          "en": "Body"},
    "ext_bitterness":   {"es": "Amargor",         "en": "Bitterness"},
    "ext_notes":        {"es": "Notas de cata",   "en": "Flavor Notes"},
    "ext_score":        {"es": "Puntuación",      "en": "Score"},
    "ext_locked":       {"es": "Receta Óptima ★", "en": "Optimal Recipe ★"},

    # Water
    "water_gh":         {"es": "Dureza General (ppm)", "en": "General Hardness (ppm)"},
    "water_kh":         {"es": "Alcalinidad (ppm)",    "en": "Alkalinity (ppm)"},
    "water_tds":        {"es": "TDS (ppm)",            "en": "TDS (ppm)"},
    "water_epsom":      {"es": "Sulfato Mg (g/L)",     "en": "Mg Sulfate (g/L)"},
    "water_bicarb":     {"es": "Bicarbonato Na (g/L)", "en": "Na Bicarbonate (g/L)"},
    "water_cacl2":      {"es": "Cloruro Ca (g/L)",     "en": "Ca Chloride (g/L)"},

    # Equipment
    "equip_type":       {"es": "Tipo",            "en": "Type"},
    "equip_brand":      {"es": "Marca",           "en": "Brand"},
    "equip_model":      {"es": "Modelo",          "en": "Model"},
    "equip_burr_life":  {"es": "Vida Muelas",     "en": "Burr Life"},
    "equip_kg_ground":  {"es": "Kg Molidos",      "en": "Kg Ground"},

    # Common
    "save":             {"es": "Guardar / Save",  "en": "Save"},
    "cancel":           {"es": "Cancelar",        "en": "Cancel"},
    "delete":           {"es": "Eliminar",        "en": "Delete"},
    "edit":             {"es": "Editar",          "en": "Edit"},
    "add_new":          {"es": "Agregar",         "en": "Add New"},
    "export_pdf":       {"es": "Exportar PDF",    "en": "Export PDF"},
    "no_data":          {"es": "Sin datos aún",   "en": "No data yet"},

    "dash_clusters": {"es": "🔬 Grupos de Extracción (IA)", "en": "🔬 Extraction Clusters (AI)"},
    "dash_overdue": {"es": "VENCIDO", "en": "OVERDUE"},
    "dash_in_days": {"es": "En {} día(s)", "en": "In {} day(s)"},
    "dash_burr_life": {"es": "% vida utilizada", "en": "% burr life used"},
    "dash_clusters_err": {"es": "Clusters no disponibles", "en": "Clusters unavailable"},
    "journal_title": {"es": "Bitácora de Calibración", "en": "Dial-In Journal"},
    "journal_subtitle": {"es": "Registra y analiza cada extracción", "en": "Log and analyze every extraction"},
    "search": {"es": "Buscar…", "en": "Search…"},
    "no_bean": {"es": "(Sin café)", "en": "(No bean)"},
    "no_equip": {"es": "(Sin equipo)", "en": "(No equip)"},
    "select_flavors": {"es": "Selecciona sabores", "en": "Click to select"},
    "no_history": {"es": "Sin historial disponible", "en": "No history available"},
    "first_shot": {"es": "Primera extracción para este café", "en": "First shot for this bean"},
    "err_numeric": {"es": "Verifica los valores numéricos", "en": "Check numeric fields"},
    "training_ai": {"es": "⚙️ Entrenando IA con tu nuevo puntaje...", "en": "⚙️ Training AI..."},
    "del_shot": {"es": "¿Eliminar esta extracción?", "en": "Delete this extraction?"},
    "eq_title": {"es": "Gestión de Equipo", "en": "Equipment"},
    "eq_subtitle": {"es": "Máquinas, molinos y mantenimiento", "en": "Machines, grinders & maintenance"},
    "add_eq": {"es": "+ Agregar Equipo", "en": "+ Add Equipment"},
    "reg_eq": {"es": "Equipos Registrados", "en": "Registered Equipment"},
    "burr_life": {"es": "⚙ Vida de Muelas:", "en": "⚙ Burr Life:"},
    "add_kg": {"es": "Añadir kg molidos:", "en": "Add kg ground:"},
    "maint_cal": {"es": "Calendario de Mantenimiento", "en": "Maintenance Calendar"},
    "in_days": {"es": "En {}d", "en": "In {}d"},
    "never": {"es": "Nunca", "en": "Never"},
    "del_eq": {"es": "¿Eliminar este equipo y sus tareas?", "en": "Delete equipment and its tasks?"},
    "err_num2": {"es": "Ingresa un número válido", "en": "Enter a valid number"},
    "eq_type": {"es": "Tipo", "en": "Type"},
    "eq_brand": {"es": "Marca *", "en": "Brand *"},
    "eq_model": {"es": "Modelo *", "en": "Model *"},
    "only_grinder": {"es": "(Solo si es molino)", "en": "(Grinder only)"},
    "add_def_tasks": {"es": "Agregar tareas predeterminadas", "en": "Add default tasks"},
    "err_brand": {"es": "Marca y Modelo son obligatorios", "en": "Brand and Model required"},
    "new_task": {"es": "Nueva Tarea", "en": "New Task"},
    "task_name": {"es": "Tarea", "en": "Task name"},
    "freq_days": {"es": "Frecuencia (días)", "en": "Frequency (days)"},
    "err_name": {"es": "El nombre es obligatorio", "en": "Name is required"},
    "water_title": {"es": "Laboratorio de Agua", "en": "Water Lab"},
    "water_sub": {"es": "Crea tu receta mineral perfecta para espresso", "en": "Build your perfect mineral water recipe"},
    "base_prof": {"es": "Perfil Base", "en": "Base Profile"},
    "target_param": {"es": "Parámetros Objetivo", "en": "Target Parameters"},
    "gh_hard": {"es": "GH — Dureza General (ppm)", "en": "GH — General Hardness (ppm)"},
    "kh_alk": {"es": "KH — Alcalinidad (ppm)", "en": "KH — Alkalinity (ppm)"},
    "vol_prep": {"es": "Volumen a preparar (L):", "en": "Volume to prepare (L):"},
    "inc_cacl2": {"es": "Incluir Cloruro de Calcio (CaCl₂)", "en": "Include Calcium Chloride (CaCl₂)"},
    "calc_btn": {"es": "⚗️ Calcular", "en": "⚗️ Calculate"},
    "result_lbl": {"es": "Resultado", "en": "Result"},
    "save_recipe": {"es": "💾 Guardar Receta", "en": "💾 Save Recipe"},
    "saved_recipes": {"es": "Recetas Guardadas", "en": "Saved Recipes"},
    "custom_preset": {"es": "Personalizado", "en": "Custom"},
    "del_recipe": {"es": "¿Eliminar esta receta de agua?", "en": "Delete this water recipe?"},
    "recipe_name": {"es": "Nombre de la receta:", "en": "Recipe name:"},
    "no_beans_yet": {"es": "No hay granos registrados. Agrega tu primer café.", "en": "No beans yet. Add your first coffee."},
    "del_bean": {"es": "¿Eliminar este café? Esto también eliminará todos sus lotes y extracciones.", "en": "Delete this bean? This will also remove all its batches and extractions."},
    "add_batch": {"es": "Añadir Lote", "en": "Add Batch"},
    "err_date": {"es": "Fecha inválida. Use YYYY-MM-DD", "en": "Invalid date. Use YYYY-MM-DD"},
    "err_num_batch": {"es": "Valores numéricos inválidos", "en": "Invalid numeric values"},
    "archive_batch": {"es": "¿Archivar este lote?", "en": "Archive this batch?"},
    "cat_coffee": {"es": "Catálogo de Café", "en": "Bean Catalog"},
    "err_roaster_name": {"es": "Tostador y Nombre son obligatorios.", "en": "Roaster and Name are required."},

    "ai_analysis": {"es": "✨ IA: Análisis y Ajuste Sugerido", "en": "✨ AI: Analysis & Suggested Adjustment"},
    "ai_training": {"es": "Entrenando modelo…", "en": "Training model…"},
    "ai_curr_pred": {"es": "Score actual predicho: ", "en": "Predicted score: "},
    "ai_sensory_diag": {"es": "Diagnóstico Sensorial", "en": "Sensory Diagnostic"},
    "ai_no_adj": {"es": "✓ No se sugieren más ajustes matemáticos.", "en": "✓ No further mathematical adjustments suggested."},
    "ai_opt_recipe": {"es": "Receta Óptima Sugerida:", "en": "Suggested Optimal Recipe:"},
    "ai_est_score": {"es": "Score estimado", "en": "Estimated score"},
    "ai_flavor_pred": {"es": "✨  Perfil Predicho por IA", "en": "✨ AI Flavor Prediction"},
    "ai_no_pred": {"es": "Sin predicción disponible.", "en": "No prediction available."},
    "ai_estimate_hint": {"es": "⚠ Estimación IA · basada en variedad, proceso y altitud", "en": "⚠ AI estimate · based on variety, process & altitude"},
    "ai_save_cat": {"es": "Guardar en Catálogo", "en": "Save to Catalog"},
    "dash_peak_beans": {"es": "🌱 Granos en Ventana Óptima", "en": "🌱 Peak Window Beans"},
    "dash_last_opt": {"es": "★ Última Receta Óptima", "en": "★ Last Optimal Recipe"},
    "dash_maint_alerts": {"es": "⚠️ Alertas de Mantenimiento", "en": "⚠️ Maintenance Alerts"},
    "dash_burrs": {"es": "⚙️ Vida de Muelas", "en": "⚙️ Burr Life"},
    "dash_no_batches": {"es": "No hay lotes registrados aún.", "en": "No batches registered yet."},
    "dash_no_optimal": {"es": "Aún no has marcado una receta como óptima.", "en": "No optimal recipe marked yet."},
    "dash_maint_ok": {"es": "✓ Todo en orden.", "en": "✓ All maintenance up to date."},
    "eq_machine": {"es": "Máquina", "en": "Machine"},
    "eq_grinder": {"es": "Molino", "en": "Grinder"},
    "eq_other": {"es": "Otro", "en": "Other"},
    "task_chem_backflush": {"es": "Backflush Químico", "en": "Chemical Backflush"},
    "task_water_backflush": {"es": "Backflush con agua", "en": "Water Backflush"},
    "task_descaling": {"es": "Descalcificación", "en": "Descaling"},
    "task_water_filter": {"es": "Cambio de filtro de agua", "en": "Water Filter"},
    "task_group_clean": {"es": "Limpieza cabezal", "en": "Group Head Clean"},
    "task_burr_clean": {"es": "Limpieza de muelas", "en": "Burr Cleaning"},
    "task_gen_clean": {"es": "Limpieza general", "en": "General Cleaning"},
    "task_calibration": {"es": "Calibración", "en": "Calibration Check"},
    "balanced": {"es": "Equilibrado", "en": "Balanced"},
    "sweet": {"es": "Dulce", "en": "Sweet"},
    "proc_washed":      {"es": "Lavado", "en": "Washed"},
    "proc_natural":     {"es": "Natural", "en": "Natural"},
    "proc_honey":       {"es": "Honey", "en": "Honey"},
    "proc_anaerobic":   {"es": "Anaeróbico", "en": "Anaerobic"},
    "proc_carbonic":    {"es": "Carbónico", "en": "Carbonic"},
    "proc_experimental":{"es": "Experimental", "en": "Experimental"},
    "proc_other":       {"es": "Otro", "en": "Other"},
    "bean":             {"es": "Café", "en": "Bean"},
    "actions":          {"es": "Acciones", "en": "Actions"},
    "batches":          {"es": "Lotes", "en": "Batches"},
    "profile":          {"es": "Perfil", "en": "Profile"},
    "ai_not_enough_data": {"es": "Registra al menos 6 extracciones para ver clusters.", "en": "Log at least 6 extractions to see clusters."},
    "star_shots":       {"es": "Shots Estelares", "en": "Star Shots"},
    "work_in_progress": {"es": "Shots en Proceso", "en": "Work in Progress"},
    "intense_profile":  {"es": "Perfil Intenso", "en": "Intense Profile"},
    "sweet_profile":    {"es": "Perfil Dulce", "en": "Sweet Profile"},
    "bright_&_acidic":  {"es": "Perfil Brillante", "en": "Bright & Acidic"},
    "full_&_creamy":    {"es": "Perfil Cremoso", "en": "Full & Creamy"},
    "long_extraction":  {"es": "Extracción Larga", "en": "Long Extraction"},
    "short_&_dense":    {"es": "Extracción Corta", "en": "Short & Dense"},
    "varied":           {"es": "Variado", "en": "Varied"},
    "new_shot":         {"es": "Nueva Extracción", "en": "New Shot"},
    "shot_detail":      {"es": "Detalle de Extracción", "en": "Shot Detail"},
    "duplicate":        {"es": "Duplicar", "en": "Duplicate"},
    "var_gesha":        {"es": "Gesha", "en": "Geisha"},
}

import os
import json
from pathlib import Path

def get_config_path() -> Path:
    config_dir = Path.home() / ".espressolab"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"

def load_lang() -> str:
    path = get_config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("lang", "es")
        except Exception:
            pass
    return "es"

def save_lang(lang: str):
    global ACTIVE_LANG
    ACTIVE_LANG = lang
    path = get_config_path()
    data = {}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["lang"] = lang
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)

ACTIVE_LANG = load_lang()

def get_label(key: str) -> str:
    """Return label in active language. Falls back to key if not found."""
    return LABELS.get(key, {}).get(ACTIVE_LANG, key)

def L(key: str) -> str:
    """Shorthand: returns localized string."""
    return get_label(key)
