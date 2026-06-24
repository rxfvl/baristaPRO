import os
import re
from pathlib import Path

def patch_i18n_regex():
    ui_files = list(Path('ui').glob('*.py'))
    
    # Let's write a robust script that replaces common patterns
    
    # 1. Bean Stash
    content = Path('ui/bean_stash.py').read_text(encoding='utf-8')
    content = content.replace('headers = ["Café / Coffee", "Tostador / Roaster", "Origen / Origin",\n                       "Proceso / Process", "Stock Total", "Acciones"]', 
                              'headers = [L("bean"), L("bean_roaster"), L("bean_country"), L("bean_process"), L("bean_stock"), L("actions")]')
    content = content.replace('f"✨ IA Perfil / Profile: Acidez {bean.expected_acidity:.1f}  |  Dulzor {bean.expected_sweetness:.1f}  |  Cuerpo {bean.expected_body:.1f}  |  Amargor {bean.expected_bitterness:.1f}"',
                              'f"✨ {L(\'dash_clusters\').split()[0]} {L(\'profile\', \'Perfil\')}: {L(\'ext_acidity\')} {bean.expected_acidity:.1f} | {L(\'ext_sweetness\')} {bean.expected_sweetness:.1f} | {L(\'ext_body\')} {bean.expected_body:.1f} | {L(\'ext_bitterness\')} {bean.expected_bitterness:.1f}"')
    content = content.replace('f"Lotes / Batches - {self.bean_name}"', 'f"{L(\'batches\', \'Lotes\')} - {self.bean_name}"')
    content = content.replace('text="Notas / Notes"', 'text=L("ext_notes")')
    Path('ui/bean_stash.py').write_text(content, encoding='utf-8')

    # 2. Dashboard
    content = Path('ui/dashboard.py').read_text(encoding='utf-8')
    if 'from utils.theme import ' in content and ' L,' not in content:
        content = content.replace('from utils.theme import COLORS, FONTS, CORNER_RADIUS', 'from utils.theme import COLORS, FONTS, CORNER_RADIUS, L')
    
    content = content.replace('"🔬 Grupos de Extracción / Extraction Clusters (IA)"', 'L("dash_clusters")')
    content = content.replace('f"Molida / Grind: {ext.grind_size}"', 'f"{L(\'ext_grind\')}: {ext.grind_size}"')
    content = content.replace('"VENCIDO / OVERDUE"', 'L("dash_overdue")')
    content = content.replace('f"En {task.days_until_due} día(s) / In {task.days_until_due} day(s)"', 'L("dash_in_days").format(task.days_until_due)')
    content = content.replace('f"{pct*100:.1f}% vida utilizada / burr life used"', 'f"{pct*100:.1f}% {L(\'dash_burr_life\')}"')
    content = content.replace('f"Clusters no disponibles / Clusters unavailable: {e}"', 'f"{L(\'dash_clusters_err\')}: {e}"')
    
    Path('ui/dashboard.py').write_text(content, encoding='utf-8')

    # 3. Dial In Journal
    content = Path('ui/dial_in_journal.py').read_text(encoding='utf-8')
    content = content.replace('text="Bitácora de Calibración / Dial-In Journal"', 'text=L("journal_title")')
    content = content.replace('text="Registra y analiza cada extracción / Log and analyze every extraction"', 'text=L("journal_subtitle")')
    content = content.replace('text="+ Nueva Extracción / New Shot"', 'text=L("new_shot")')
    content = content.replace('placeholder_text="Buscar / Search…"', 'placeholder_text=L("search")')
    content = content.replace('"Sin café / No bean"', 'L("no_bean")')
    content = content.replace('"(Sin café / No bean)"', 'L("no_bean")')
    content = content.replace('"(Sin equipo / No equip)"', 'L("no_equip")')
    content = content.replace('text="Selecciona sabores / Click to select"', 'text=L("select_flavors")')
    content = content.replace('text="Sin historial disponible / No history available"', 'text=L("no_history")')
    content = content.replace('text="Primera extracción para este café / First shot for this bean"', 'text=L("first_shot")')
    content = content.replace('"Verifica los valores numéricos / Check numeric fields"', 'L("err_numeric")')
    content = content.replace('text="⚙️  Entrenando IA con tu nuevo puntaje... / Training AI..."', 'text=L("training_ai")')
    content = content.replace('"¿Eliminar esta extracción? / Delete this extraction?"', 'L("del_shot")')
    content = content.replace('self.title("Exportar PDF / Export PDF")', 'self.title(L("export_pdf"))')
    Path('ui/dial_in_journal.py').write_text(content, encoding='utf-8')

    # 4. Equipment
    content = Path('ui/equipment.py').read_text(encoding='utf-8')
    if 'from utils.theme import ' in content and ' L,' not in content:
        content = content.replace('from utils.theme import COLORS, FONTS, CORNER_RADIUS', 'from utils.theme import COLORS, FONTS, CORNER_RADIUS, L')
    
    content = content.replace('text="Gestión de Equipo / Equipment"', 'text=L("eq_title")')
    content = content.replace('text="Máquinas, molinos y mantenimiento / Machines, grinders & maintenance"', 'text=L("eq_subtitle")')
    content = content.replace('text="+ Agregar Equipo / Add Equipment"', 'text=L("add_eq")')
    content = content.replace('text="Equipos Registrados / Registered Equipment"', 'text=L("reg_eq")')
    content = content.replace('text="⚙ Vida de Muelas / Burr Life:"', 'text=L("burr_life")')
    content = content.replace('f"{equip.total_kg_ground:.1f} / {equip.burr_change_interval_kg:.0f} kg ({pct*100:.1f}%)"', 'f"{equip.total_kg_ground:.1f} / {equip.burr_change_interval_kg:.0f} kg ({pct*100:.1f}%)"')
    content = content.replace('text="Añadir kg molidos / Add kg ground:"', 'text=L("add_kg")')
    content = content.replace('text="Calendario de Mantenimiento / Maintenance Calendar"', 'text=L("maint_cal")')
    content = content.replace('"VENCIDO / OVERDUE"', 'L("dash_overdue")')
    content = content.replace('f"En {days}d / In {days}d"', 'L("in_days").format(days)')
    content = content.replace('"Nunca / Never"', 'L("never")')
    content = content.replace('"¿Eliminar este equipo y sus tareas? / Delete equipment and its tasks?"', 'L("del_eq")')
    content = content.replace('"Ingresa un número válido / Enter a valid number"', 'L("err_num2")')
    content = content.replace('self.title("Agregar Equipo / Add Equipment")', 'self.title(L("add_eq"))')
    content = content.replace('text="Agregar Equipo / Add Equipment"', 'text=L("add_eq")')
    content = content.replace('text="Tipo / Type"', 'text=L("eq_type")')
    content = content.replace('"Marca / Brand *"', 'L("eq_brand")')
    content = content.replace('"Modelo / Model *"', 'L("eq_model")')
    content = content.replace('text="(Solo si es molino / Grinder only)"', 'text=L("only_grinder")')
    content = content.replace('text="Agregar tareas de mantenimiento predeterminadas / Add default tasks"', 'text=L("add_def_tasks")')
    content = content.replace('text="Notas / Notes"', 'text=L("ext_notes")')
    content = content.replace('text="Guardar / Save"', 'text=L("save")')
    content = content.replace('"Marca y Modelo son obligatorios / Brand and Model required"', 'L("err_brand")')
    content = content.replace('text="Nueva Tarea / New Task"', 'text=L("new_task")')
    content = content.replace('text="Tarea / Task name"', 'text=L("task_name")')
    content = content.replace('text="Frecuencia (días / days)"', 'text=L("freq_days")')
    content = content.replace('"El nombre es obligatorio / Name is required"', 'L("err_name")')
    Path('ui/equipment.py').write_text(content, encoding='utf-8')

    # 5. Water
    content = Path('ui/water_lab.py').read_text(encoding='utf-8')
    if 'from utils.theme import ' in content and ' L,' not in content:
        content = content.replace('from utils.theme import COLORS, FONTS, CORNER_RADIUS', 'from utils.theme import COLORS, FONTS, CORNER_RADIUS, L')
    
    content = content.replace('text="Laboratorio de Agua / Water Lab"', 'text=L("water_title")')
    content = content.replace('text="Crea tu receta mineral perfecta para espresso / Build your perfect mineral water recipe"', 'text=L("water_sub")')
    content = content.replace('text="Perfil Base / Base Profile"', 'text=L("base_prof")')
    content = content.replace('text="Parámetros Objetivo / Target Parameters"', 'text=L("target_param")')
    content = content.replace('"GH — Dureza General / Hardness (ppm)"', 'L("gh_hard")')
    content = content.replace('"KH — Alcalinidad / Alkalinity (ppm)"', 'L("kh_alk")')
    content = content.replace('text="Volumen a preparar / Volume to prepare (L):"', 'text=L("vol_prep")')
    content = content.replace('text="Incluir Cloruro de Calcio / Include Calcium Chloride (CaCl₂)"', 'text=L("inc_cacl2")')
    content = content.replace('text="⚗️ Calcular / Calculate"', 'text=L("calc_btn")')
    content = content.replace('text="Resultado / Result"', 'text=L("result_lbl")')
    content = content.replace('text="💾 Guardar Receta / Save Recipe"', 'text=L("save_recipe")')
    content = content.replace('text="Recetas Guardadas / Saved Recipes"', 'text=L("saved_recipes")')
    content = content.replace('"Personalizado / Custom"', 'L("custom_preset")')
    content = content.replace('"¿Eliminar esta receta de agua? / Delete this water recipe?"', 'L("del_recipe")')
    content = content.replace('text="Nombre de la receta / Recipe name:"', 'text=L("recipe_name")')
    content = content.replace('text="Guardar / Save"', 'text=L("save")')
    content = content.replace('text="Cancelar / Cancel"', 'text=L("cancel")')
    content = content.replace('"Ingresa un nombre / Enter a name"', 'L("err_name")')
    Path('ui/water_lab.py').write_text(content, encoding='utf-8')

    print("Success")

if __name__ == "__main__":
    patch_i18n_regex()
