import os
from pathlib import Path

def patch_v3():
    # 1. AI Widgets
    content = Path('ui/ai_widgets.py').read_text(encoding='utf-8')
    if 'from utils.theme import ' in content and ' L,' not in content:
        content = content.replace('from utils.theme import COLORS, FONTS, CORNER_RADIUS', 'from utils.theme import COLORS, FONTS, CORNER_RADIUS, L')
    
    content = content.replace('text="✨ IA: Análisis y Ajuste Sugerido / AI: Analysis & Suggested Adjustment"', 'text=L("ai_analysis")')
    content = content.replace('text="Entrenando modelo… / Training model…"', 'text=L("ai_training")')
    content = content.replace('text=f"Score actual predicho / Predicted score:  "', 'text=L("ai_curr_pred")')
    content = content.replace('text=f"{icon} Diagnóstico Sensorial / Sensory Diagnostic"', 'text=f"{icon} {L(\'ai_sensory_diag\')}"')
    content = content.replace('text="✓ No se sugieren más ajustes matemáticos. / No further mathematical adjustments suggested."', 'text=L("ai_no_adj")')
    content = content.replace('text="Receta Óptima Sugerida / Suggested Optimal Recipe:"', 'text=L("ai_opt_recipe")')
    content = content.replace('text=f"Score estimado / Estimated score:  ⭐ {sugg_score:.1f}  (+{sugg_score - base_score:.1f})"', 'text=f"{L(\'ai_est_score\')}: ⭐ {sugg_score:.1f} (+{sugg_score - base_score:.1f})"')
    content = content.replace('text="✨  Perfil Predicho por IA / AI Flavor Prediction"', 'text=L("ai_flavor_pred")')
    content = content.replace('text="Sin predicción disponible. / No prediction available."', 'text=L("ai_no_pred")')
    content = content.replace('text="⚠ Estimación IA · basada en variedad, proceso y altitud / AI estimate · based on variety, process & altitude"', 'text=L("ai_estimate_hint")')
    content = content.replace('text="Guardar en Catálogo / Save to Catalog"', 'text=L("ai_save_cat")')
    content = content.replace('text=f"{cluster[\'icon\']}  {cluster[\'label_es\']} / {cluster[\'label_en\']}"', 'text=f"{cluster[\'icon\']}  {L(cluster[\'label_en\'].lower().replace(\' \', \'_\'))}"')
    Path('ui/ai_widgets.py').write_text(content, encoding='utf-8')

    # 2. Dashboard Headers
    content = Path('ui/dashboard.py').read_text(encoding='utf-8')
    content = content.replace('"🌱 Granos en Ventana Óptima / Peak Window Beans"', 'L("dash_peak_beans")')
    content = content.replace('"★ Última Receta Óptima / Last Optimal Recipe"', 'L("dash_last_opt")')
    content = content.replace('"⚠️ Alertas de Mantenimiento / Maintenance Alerts"', 'L("dash_maint_alerts")')
    content = content.replace('"⚙️ Vida de Muelas / Burr Life"', 'L("dash_burrs")')
    content = content.replace('"No hay lotes registrados aún. / No batches registered yet."', 'L("dash_no_batches")')
    content = content.replace('"Aún no has marcado una receta como óptima. / No optimal recipe marked yet."', 'L("dash_no_optimal")')
    content = content.replace('"✓ Todo en orden. / All maintenance up to date."', 'L("dash_maint_ok")')
    Path('ui/dashboard.py').write_text(content, encoding='utf-8')

    # 3. Equipment Arrays
    content = Path('ui/equipment.py').read_text(encoding='utf-8')
    content = content.replace('["Machine / Máquina", "Grinder / Molino", "Other / Otro"]', '[L("eq_machine"), L("eq_grinder"), L("eq_other")]')
    content = content.replace('"Machine / Máquina"', 'L("eq_machine")')
    content = content.replace('"Grinder / Molino"', 'L("eq_grinder")')
    
    # We will just patch the raw dict strings
    content = content.replace('("Backflush Químico / Chemical Backflush", 7)', '(L("task_chem_backflush"), 7)')
    content = content.replace('("Backflush con agua / Water Backflush", 1)', '(L("task_water_backflush"), 1)')
    content = content.replace('("Descalcificación / Descaling", 90)', '(L("task_descaling"), 90)')
    content = content.replace('("Cambio de filtro de agua / Water Filter", 180)', '(L("task_water_filter"), 180)')
    content = content.replace('("Limpieza cabezal / Group Head Clean", 1)', '(L("task_group_clean"), 1)')
    content = content.replace('("Limpieza de muelas / Burr Cleaning", 30)', '(L("task_burr_clean"), 30)')
    content = content.replace('("Limpieza general / General Cleaning", 7)', '(L("task_gen_clean"), 7)')
    content = content.replace('("Calibración / Calibration Check", 90)', '(L("task_calibration"), 90)')
    Path('ui/equipment.py').write_text(content, encoding='utf-8')
    
    # Update LABELS in theme.py
    new_labels = {
        "ai_analysis": ("✨ IA: Análisis y Ajuste Sugerido", "✨ AI: Analysis & Suggested Adjustment"),
        "ai_training": ("Entrenando modelo…", "Training model…"),
        "ai_curr_pred": ("Score actual predicho: ", "Predicted score: "),
        "ai_sensory_diag": ("Diagnóstico Sensorial", "Sensory Diagnostic"),
        "ai_no_adj": ("✓ No se sugieren más ajustes matemáticos.", "✓ No further mathematical adjustments suggested."),
        "ai_opt_recipe": ("Receta Óptima Sugerida:", "Suggested Optimal Recipe:"),
        "ai_est_score": ("Score estimado", "Estimated score"),
        "ai_flavor_pred": ("✨  Perfil Predicho por IA", "✨ AI Flavor Prediction"),
        "ai_no_pred": ("Sin predicción disponible.", "No prediction available."),
        "ai_estimate_hint": ("⚠ Estimación IA · basada en variedad, proceso y altitud", "⚠ AI estimate · based on variety, process & altitude"),
        "ai_save_cat": ("Guardar en Catálogo", "Save to Catalog"),
        "dash_peak_beans": ("🌱 Granos en Ventana Óptima", "🌱 Peak Window Beans"),
        "dash_last_opt": ("★ Última Receta Óptima", "★ Last Optimal Recipe"),
        "dash_maint_alerts": ("⚠️ Alertas de Mantenimiento", "⚠️ Maintenance Alerts"),
        "dash_burrs": ("⚙️ Vida de Muelas", "⚙️ Burr Life"),
        "dash_no_batches": ("No hay lotes registrados aún.", "No batches registered yet."),
        "dash_no_optimal": ("Aún no has marcado una receta como óptima.", "No optimal recipe marked yet."),
        "dash_maint_ok": ("✓ Todo en orden.", "✓ All maintenance up to date."),
        "eq_machine": ("Máquina", "Machine"),
        "eq_grinder": ("Molino", "Grinder"),
        "eq_other": ("Otro", "Other"),
        "task_chem_backflush": ("Backflush Químico", "Chemical Backflush"),
        "task_water_backflush": ("Backflush con agua", "Water Backflush"),
        "task_descaling": ("Descalcificación", "Descaling"),
        "task_water_filter": ("Cambio de filtro de agua", "Water Filter"),
        "task_group_clean": ("Limpieza cabezal", "Group Head Clean"),
        "task_burr_clean": ("Limpieza de muelas", "Burr Cleaning"),
        "task_gen_clean": ("Limpieza general", "General Cleaning"),
        "task_calibration": ("Calibración", "Calibration Check"),
        "balanced": ("Equilibrado", "Balanced"),
        "sweet": ("Dulce", "Sweet"),
        "acidic": ("Ácido", "Acidic"),
        "bitter": ("Amargo", "Bitter")
    }

    from utils.theme import LABELS
    with open("utils/theme.py", "r", encoding="utf-8") as f:
        theme_content = f.read()

    # Find the end of LABELS dictionary
    end_idx = theme_content.find("}\n\nimport os")
    if end_idx == -1:
        end_idx = theme_content.find("}\n\nimport json")

    lines = []
    for k, (es, en) in new_labels.items():
        if f'"{k}":' not in theme_content:
            lines.append(f'    "{k}": {{"es": "{es}", "en": "{en}"}},')
    
    if lines:
        new_theme = theme_content[:end_idx] + "\n" + "\n".join(lines) + "\n" + theme_content[end_idx:]
        with open("utils/theme.py", "w", encoding="utf-8") as f:
            f.write(new_theme)

if __name__ == "__main__":
    patch_v3()
    print("Success")
