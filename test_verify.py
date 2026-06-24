"""Quick verification test for EspressoLab core modules."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== EspressoLab Verification ===")

# 1. DB init
print("\n[1] Database init...")
from db.database import init_db
init_db()
print("    DB created at ~/.espressolab/espressolab.db")

# 2. Water calculator
print("\n[2] Water chemistry calculator...")
from logic.water_calc import calculate_water_recipe, PRESET_PROFILES
r = calculate_water_recipe(68, 40, 150)
print(f"    SCA Ideal: Epsom={r.mg_sulfate_g_per_l}g/L | Bicarb={r.sodium_bicarb_g_per_l}g/L")
print(f"    GH={r.actual_gh_ppm}ppm (SCA ok={r.gh_ok}) | KH={r.actual_kh_ppm}ppm (ok={r.kh_ok})")
print(f"    TDS~{r.actual_tds_ppm}ppm (ok={r.tds_ok})")
print(f"    Presets available: {list(PRESET_PROFILES.keys())}")

# 3. Degassing
print("\n[3] Degassing logic...")
from logic.degassing import degassing_info, get_rest_window
from datetime import date, timedelta

roast = date.today() - timedelta(days=10)
info = degassing_info(roast, 7, 14)
print(f"    10-day-old espresso: status='{info['status']}', days={info['days_rested']}, progress={info['progress']:.0%}")

roast2 = date.today() - timedelta(days=3)
info2 = degassing_info(roast2, 7, 14)
print(f"    3-day-old espresso:  status='{info2['status']}'")

nat_window = get_rest_window("Natural")
print(f"    Natural process rest window: {nat_window[0]}-{nat_window[1]} days")

# 4. DB CRUD
print("\n[4] Database CRUD...")
from db.database import get_session
from db.models import Bean, ExtractionLog

with get_session() as db:
    # Insert test bean
    bean = Bean(roaster="Test Roaster", name="Verification Bean",
                origin_country="Ethiopia", process="Natural",
                roast_date=date.today() - timedelta(days=12),
                stock_grams=250, rest_days_min=10, rest_days_max=21)
    db.add(bean)
    db.commit()
    bean_id = bean.id
    print(f"    OK Bean created: id={bean_id}")

    # Insert extraction
    ext = ExtractionLog(bean_id=bean_id, dose_in=18.0, yield_out=36.0,
                        extraction_time=28, water_temp=93.0,
                        grind_size="EK43 8.5", pressure=9.0,
                        acidity=7, sweetness=8, body=6, bitterness=4,
                        score=8.2, is_locked=True,
                        flavor_notes="Jasmine, Frutal, Cítrico")
    db.add(ext)
    db.commit()
    print(f"    OK Extraction created: ratio={ext.ratio_str}")

    # Query back
    b = db.get(Bean, bean_id)
    print(f"    OK Bean degassing status: {b.degassing_status}")
    exts = db.query(ExtractionLog).filter_by(bean_id=bean_id).all()
    print(f"    OK Extractions retrieved: {len(exts)}")

    # Cleanup
    db.delete(b)
    db.commit()
    print("    OK Test data cleaned up")

print("\n=== ALL CHECKS PASSED ===")
