import os
import re

THEME_PATH = "utils/theme.py"

def update_labels(new_labels):
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the end of LABELS dictionary
    end_idx = content.find("}\n\nimport os")
    if end_idx == -1:
        end_idx = content.find("}\n\nimport json")
    
    if end_idx == -1:
        print("Could not find end of LABELS dict")
        return

    # format new labels
    lines = []
    for k, (es, en) in new_labels.items():
        if f'"{k}":' not in content:
            lines.append(f'    "{k}": {{"es": "{es}", "en": "{en}"}},')
    
    if lines:
        new_content = content[:end_idx] + "\n" + "\n".join(lines) + "\n" + content[end_idx:]
        with open(THEME_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)

def patch_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # ensure import L is there
    if 'from utils.theme import ' in content and ' L,' not in content and ', L' not in content:
        content = content.replace('from utils.theme import COLORS, FONTS, CORNER_RADIUS', 'from utils.theme import COLORS, FONTS, CORNER_RADIUS, L, get_label')
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    new_labels = {
        # Dashboard
        "dash_clusters": ("🔬 Grupos de Extracción (IA)", "🔬 Extraction Clusters (AI)"),
        "dash_overdue": ("VENCIDO", "OVERDUE"),
        "dash_in_days": ("En {} día(s)", "In {} day(s)"),
        "dash_burr_life": ("% vida utilizada", "% burr life used"),
        "dash_clusters_err": ("Clusters no disponibles", "Clusters unavailable"),
        
        # Dial In Journal
        "journal_title": ("Bitácora de Calibración", "Dial-In Journal"),
        "journal_subtitle": ("Registra y analiza cada extracción", "Log and analyze every extraction"),
        "search": ("Buscar…", "Search…"),
        "no_bean": ("(Sin café)", "(No bean)"),
        "no_equip": ("(Sin equipo)", "(No equip)"),
        "select_flavors": ("Selecciona sabores", "Click to select"),
        "no_history": ("Sin historial disponible", "No history available"),
        "first_shot": ("Primera extracción para este café", "First shot for this bean"),
        "err_numeric": ("Verifica los valores numéricos", "Check numeric fields"),
        "training_ai": ("⚙️ Entrenando IA con tu nuevo puntaje...", "⚙️ Training AI..."),
        "del_shot": ("¿Eliminar esta extracción?", "Delete this extraction?"),
        "export_pdf": ("Exportar PDF", "Export PDF"),
        
        # Equipment
        "eq_title": ("Gestión de Equipo", "Equipment"),
        "eq_subtitle": ("Máquinas, molinos y mantenimiento", "Machines, grinders & maintenance"),
        "add_eq": ("+ Agregar Equipo", "+ Add Equipment"),
        "reg_eq": ("Equipos Registrados", "Registered Equipment"),
        "burr_life": ("⚙ Vida de Muelas:", "⚙ Burr Life:"),
        "add_kg": ("Añadir kg molidos:", "Add kg ground:"),
        "maint_cal": ("Calendario de Mantenimiento", "Maintenance Calendar"),
        "in_days": ("En {}d", "In {}d"),
        "never": ("Nunca", "Never"),
        "del_eq": ("¿Eliminar este equipo y sus tareas?", "Delete equipment and its tasks?"),
        "err_num2": ("Ingresa un número válido", "Enter a valid number"),
        "eq_type": ("Tipo", "Type"),
        "eq_brand": ("Marca *", "Brand *"),
        "eq_model": ("Modelo *", "Model *"),
        "only_grinder": ("(Solo si es molino)", "(Grinder only)"),
        "add_def_tasks": ("Agregar tareas predeterminadas", "Add default tasks"),
        "err_brand": ("Marca y Modelo son obligatorios", "Brand and Model required"),
        "new_task": ("Nueva Tarea", "New Task"),
        "task_name": ("Tarea", "Task name"),
        "freq_days": ("Frecuencia (días)", "Frequency (days)"),
        "err_name": ("El nombre es obligatorio", "Name is required"),
        
        # Water
        "water_title": ("Laboratorio de Agua", "Water Lab"),
        "water_sub": ("Crea tu receta mineral perfecta para espresso", "Build your perfect mineral water recipe"),
        "base_prof": ("Perfil Base", "Base Profile"),
        "target_param": ("Parámetros Objetivo", "Target Parameters"),
        "gh_hard": ("GH — Dureza General (ppm)", "GH — General Hardness (ppm)"),
        "kh_alk": ("KH — Alcalinidad (ppm)", "KH — Alkalinity (ppm)"),
        "vol_prep": ("Volumen a preparar (L):", "Volume to prepare (L):"),
        "inc_cacl2": ("Incluir Cloruro de Calcio (CaCl₂)", "Include Calcium Chloride (CaCl₂)"),
        "calc_btn": ("⚗️ Calcular", "⚗️ Calculate"),
        "result_lbl": ("Resultado", "Result"),
        "save_recipe": ("💾 Guardar Receta", "💾 Save Recipe"),
        "saved_recipes": ("Recetas Guardadas", "Saved Recipes"),
        "custom_preset": ("Personalizado", "Custom"),
        "del_recipe": ("¿Eliminar esta receta de agua?", "Delete this water recipe?"),
        "recipe_name": ("Nombre de la receta:", "Recipe name:"),
        
        # Bean Stash Extras
        "no_beans_yet": ("No hay granos registrados. Agrega tu primer café.", "No beans yet. Add your first coffee."),
        "del_bean": ("¿Eliminar este café? Esto también eliminará todos sus lotes y extracciones.", "Delete this bean? This will also remove all its batches and extractions."),
        "add_batch": ("Añadir Lote", "Add Batch"),
        "err_date": ("Fecha inválida. Use YYYY-MM-DD", "Invalid date. Use YYYY-MM-DD"),
        "err_num_batch": ("Valores numéricos inválidos", "Invalid numeric values"),
        "archive_batch": ("¿Archivar este lote?", "Archive this batch?"),
        "cat_coffee": ("Catálogo de Café", "Bean Catalog"),
        "err_roaster_name": ("Tostador y Nombre son obligatorios.", "Roaster and Name are required."),
    }
    
    update_labels(new_labels)
    
    # Now patch specific files
    
    # 1. Dashboard
    patch_file("ui/dashboard.py", [
        ('"🔬 Grupos de Extracción / Extraction Clusters (IA)"', 'L("dash_clusters")'),
        ('"VENCIDO / OVERDUE" if is_overdue', 'L("dash_overdue") if is_overdue'),
        ('else f"En {task.days_until_due} día(s) / In {task.days_until_due} day(s)"', 'else L("dash_in_days").format(task.days_until_due)'),
        ('text=f"{pct*100:.1f}% vida utilizada / burr life used"', 'text=f"{pct*100:.1f} {L(\'dash_burr_life\')}"'),
        ('text=f"Clusters no disponibles / Clusters unavailable: {e}"', 'text=f"{L(\'dash_clusters_err\')}: {e}"')
    ])
    
    # 2. Dial In Journal
    patch_file("ui/dial_in_journal.py", [
        ('text="Bitácora de Calibración / Dial-In Journal"', 'text=L("journal_title")'),
        ('text="Registra y analiza cada extracción / Log and analyze every extraction"', 'text=L("journal_subtitle")'),
        ('text="+ Nueva Extracción / New Shot"', 'text=f"+ {L(\'new_shot\')}"'),
        ('placeholder_text="Buscar / Search…"', 'placeholder_text=L("search")'),
        ('bean_name = "Sin café / No bean"', 'bean_name = L("no_bean")'),
        ('["(Sin café / No bean)"]', '[L("no_bean")]'),
        ('["(Sin equipo / No equip)"]', '[L("no_equip")]'),
        ('self._flavor_label.configure(text="Selecciona sabores / Click to select")', 'self._flavor_label.configure(text=L("select_flavors"))'),
        ('self._history_hint_label.configure(text="Sin historial disponible / No history available")', 'self._history_hint_label.configure(text=L("no_history"))'),
        ('self._history_hint_label.configure(text="Primera extracción para este café / First shot for this bean"', 'self._history_hint_label.configure(text=L("first_shot")'),
        ('messagebox.showerror("Error", "Verifica los valores numéricos / Check numeric fields")', 'messagebox.showerror("Error", L("err_numeric"))'),
        ('text="⚙️  Entrenando IA con tu nuevo puntaje... / Training AI..."', 'text=L("training_ai")'),
        ('messagebox.askyesno("Eliminar", "¿Eliminar esta extracción? / Delete this extraction?")', 'messagebox.askyesno("Eliminar", L("del_shot"))'),
        ('self.title("Exportar PDF / Export PDF")', 'self.title(L("export_pdf"))'),
        ('text="Selecciona un café para ver la última molienda usada"', 'text=L("no_history")'),
    ])
    
    # 3. Equipment
    patch_file("ui/equipment.py", [
        ('text="Gestión de Equipo / Equipment"', 'text=L("eq_title")'),
        ('text="Máquinas, molinos y mantenimiento / Machines, grinders & maintenance"', 'text=L("eq_subtitle")'),
        ('text="+ Agregar Equipo / Add Equipment"', 'text=L("add_eq")'),
        ('text="Equipos Registrados / Registered Equipment"', 'text=L("reg_eq")'),
        ('text="⚙ Vida de Muelas / Burr Life:"', 'text=L("burr_life")'),
        ('text="Añadir kg molidos / Add kg ground:"', 'text=L("add_kg")'),
        ('text="Calendario de Mantenimiento / Maintenance Calendar"', 'text=L("maint_cal")'),
        ('status_text = "VENCIDO / OVERDUE"', 'status_text = L("dash_overdue")'),
        ('status_text = f"En {days}d / In {days}d"', 'status_text = L("in_days").format(days)'),
        ('status_text = f"En {days}d / In {days}d" if days is not None else "—"', 'status_text = L("in_days").format(days) if days is not None else "—"'),
        ('last_done = task.last_done_date.strftime("%d/%m/%y") if task.last_done_date else "Nunca / Never"', 'last_done = task.last_done_date.strftime("%d/%m/%y") if task.last_done_date else L("never")'),
        ('messagebox.askyesno("Eliminar", "¿Eliminar este equipo y sus tareas? / Delete equipment and its tasks?")', 'messagebox.askyesno("Eliminar", L("del_eq"))'),
        ('messagebox.showerror("Error", "Ingresa un número válido / Enter a valid number")', 'messagebox.showerror("Error", L("err_num2"))'),
        ('self.title("Agregar Equipo / Add Equipment")', 'self.title(L("add_eq"))'),
        ('text="Agregar Equipo / Add Equipment"', 'text=L("add_eq")'),
        ('text="Tipo / Type"', 'text=L("eq_type")'),
        ('("brand",                   "Marca / Brand *",                      0, row)', '("brand",                   L("eq_brand"),                      0, row)'),
        ('("model",                   "Modelo / Model *",                     1, row)', '("model",                   L("eq_model"),                     1, row)'),
        ('text="(Solo si es molino / Grinder only)"', 'text=L("only_grinder")'),
        ('text="Agregar tareas de mantenimiento predeterminadas / Add default tasks"', 'text=L("add_def_tasks")'),
        ('text="Notas / Notes"', 'text=L("ext_notes")'),
        ('text="Guardar / Save"', 'text=L("save")'),
        ('text="Cancelar / Cancel"', 'text=L("cancel")'),
        ('messagebox.showerror("Error", "Marca y Modelo son obligatorios / Brand and Model required")', 'messagebox.showerror("Error", L("err_brand"))'),
        ('text="Nueva Tarea / New Task"', 'text=L("new_task")'),
        ('text="Tarea / Task name"', 'text=L("task_name")'),
        ('text="Frecuencia (días / days)"', 'text=L("freq_days")'),
        ('messagebox.showerror("Error", "El nombre es obligatorio / Name is required")', 'messagebox.showerror("Error", L("err_name"))'),
    ])
    
    # 4. Water Lab
    patch_file("ui/water_lab.py", [
        ('text="Laboratorio de Agua / Water Lab"', 'text=L("water_title")'),
        ('text="Crea tu receta mineral perfecta para espresso / Build your perfect mineral water recipe"', 'text=L("water_sub")'),
        ('text="Perfil Base / Base Profile"', 'text=L("base_prof")'),
        ('text="Parámetros Objetivo / Target Parameters"', 'text=L("target_param")'),
        ('"GH — Dureza General / Hardness (ppm)"', 'L("gh_hard")'),
        ('"KH — Alcalinidad / Alkalinity (ppm)"', 'L("kh_alk")'),
        ('text="Volumen a preparar / Volume to prepare (L):"', 'text=L("vol_prep")'),
        ('text="Incluir Cloruro de Calcio / Include Calcium Chloride (CaCl₂)"', 'text=L("inc_cacl2")'),
        ('text="⚗️ Calcular / Calculate"', 'text=L("calc_btn")'),
        ('text="Resultado / Result"', 'text=L("result_lbl")'),
        ('text="💾 Guardar Receta / Save Recipe"', 'text=L("save_recipe")'),
        ('text="Recetas Guardadas / Saved Recipes"', 'text=L("saved_recipes")'),
        ('self._preset_combo.set("Personalizado / Custom")', 'self._preset_combo.set(L("custom_preset"))'),
        ('messagebox.askyesno("Eliminar", "¿Eliminar esta receta de agua? / Delete this water recipe?")', 'messagebox.askyesno("Eliminar", L("del_recipe"))'),
        ('text="Nombre de la receta / Recipe name:"', 'text=L("recipe_name")'),
        ('text="Guardar / Save"', 'text=L("save")'),
        ('text="Cancelar / Cancel"', 'text=L("cancel")'),
        ('messagebox.showerror("Error", "Ingresa un nombre / Enter a name")', 'messagebox.showerror("Error", L("err_name"))'),
    ])
    
    # 5. Bean Stash extras
    patch_file("ui/bean_stash.py", [
        ('text="No hay granos registrados. Agrega tu primer café. /\\nNo beans yet. Add your first coffee."', 'text=L("no_beans_yet")'),
        ('text="The Bean Stash"', 'text=L("nav_beans")'),
        ('text="Catálogo de granos y lotes / Bean catalog & batches"', 'text=L("cat_coffee")'),
        ('messagebox.askyesno(\n            "Eliminar / Delete",\n            "¿Eliminar este café? Esto también eliminará todos sus lotes y extracciones.\\n"\n            "Delete this bean? This will also remove all its batches and extractions."\n        )', 'messagebox.askyesno("Eliminar", L("del_bean"))'),
        ('text="Añadir Lote / Add Batch"', 'text=L("add_batch")'),
        ('messagebox.showerror("Error", "Fecha inválida. Use YYYY-MM-DD")', 'messagebox.showerror("Error", L("err_date"))'),
        ('messagebox.showerror("Error", "Valores numéricos inválidos")', 'messagebox.showerror("Error", L("err_num_batch"))'),
        ('messagebox.askyesno("Archivar", "¿Archivar este lote?")', 'messagebox.askyesno("Archivar", L("archive_batch"))'),
        ('text="Catálogo de Café / Bean Catalog" if self.mode == "add" else "Editar Café / Edit Bean"', 'text=L("cat_coffee") if self.mode == "add" else L("edit")'),
        ('title = "Agregar Café / Add Bean" if mode == "add" else "Editar Café / Edit Bean"', 'title = L("add_new") if mode == "add" else L("edit")'),
        ('messagebox.showerror("Error", "Tostador y Nombre son obligatorios.\\nRoaster and Name are required.")', 'messagebox.showerror("Error", L("err_roaster_name"))'),
    ])
    
    print("Done patching.")

if __name__ == "__main__":
    main()
