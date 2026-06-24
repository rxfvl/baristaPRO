import requests
import json
import os
from pathlib import Path

# Load settings from a config file or env in the future, for now hardcoded default
BASE_URL = os.getenv("API_BASE_URL", "http://79.72.62.76:8000/api")
TOKEN_FILE = Path.home() / ".espressolab" / "token.json"

class Dict2Obj:
    """Recursively converts a dictionary to an object with dot-notation access."""
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, (list, tuple)):
                setattr(self, k, [Dict2Obj(x) if isinstance(x, dict) else x for x in v])
            elif isinstance(v, dict):
                setattr(self, k, Dict2Obj(v))
            else:
                # Handle dates for specific known columns
                if k.endswith("_date") or k == "timestamp" or k == "created_at":
                    try:
                        # try to parse as datetime or date
                        if "T" in str(v):
                            from datetime import datetime
                            # FastAPI uses ISO format
                            setattr(self, k, datetime.fromisoformat(str(v)))
                        else:
                            from datetime import date
                            setattr(self, k, date.fromisoformat(str(v)))
                        continue
                    except:
                        pass
                setattr(self, k, v)

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = self._load_token()
        if self.token:
            self._set_auth_header(self.token)

    def _load_token(self):
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("access_token")
            except:
                return None
        return None

    def _save_token(self, token):
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump({"access_token": token}, f)

    def _set_auth_header(self, token):
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def is_authenticated(self):
        return self.token is not None

    def login(self, email, password):
        # OAuth2 password flow expects form data
        resp = self.session.post(f"{BASE_URL}/auth/login", data={
            "username": email,
            "password": password
        })
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            self.token = token
            self._save_token(token)
            self._set_auth_header(token)
            return True, "Success"
        return False, resp.json().get("detail", "Login failed")

    def register(self, email, password):
        resp = self.session.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password
        })
        if resp.status_code == 200:
            return True, "Registration successful. Please login."
        return False, resp.json().get("detail", "Registration failed")

    def logout(self):
        self.token = None
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

    # --- User Profile API ---
    def get_me(self):
        resp = self.session.get(f"{BASE_URL}/users/me")
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def update_profile(self, nickname: str):
        resp = self.session.put(f"{BASE_URL}/users/me", json={"nickname": nickname})
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def update_password(self, old_password: str, new_password: str):
        resp = self.session.put(f"{BASE_URL}/users/me/password", json={
            "old_password": old_password,
            "new_password": new_password
        })
        if resp.status_code == 200:
            return True, "Success"
        return False, resp.json().get("detail", "Error")

    def upload_avatar(self, file_path: str):
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "image/jpeg"
        
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            resp = self.session.post(f"{BASE_URL}/users/me/avatar", files=files)
        
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    # --- Beans API ---
    def get_beans(self):
        resp = self.session.get(f"{BASE_URL}/beans/")
        return [Dict2Obj(d) for d in resp.json()] if resp.status_code == 200 else []

    def create_bean(self, bean_data):
        resp = self.session.post(f"{BASE_URL}/beans/", json=bean_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def update_bean(self, bean_id, bean_data):
        resp = self.session.put(f"{BASE_URL}/beans/{bean_id}", json=bean_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def delete_bean(self, bean_id: int):
        resp = self.session.delete(f"{BASE_URL}/beans/{bean_id}")
        return resp.status_code in (200, 204)

    # --- Bean Batches API ---
    def get_bean_batches(self, bean_id):
        resp = self.session.get(f"{BASE_URL}/beans/{bean_id}/batches")
        return [Dict2Obj(d) for d in resp.json()] if resp.status_code == 200 else []

    def create_bean_batch(self, bean_id, batch_data):
        resp = self.session.post(f"{BASE_URL}/beans/{bean_id}/batches", json=batch_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def archive_bean_batch(self, bean_id, batch_id):
        # Need to create this endpoint or handle it with update
        pass

    # --- Extraction Logs API ---
    def get_extractions(self, bean_id=None, limit=50):
        url = f"{BASE_URL}/extractions/"
        if bean_id:
            url += f"?bean_id={bean_id}&limit={limit}"
        else:
            url += f"?limit={limit}"
        resp = self.session.get(url)
        return [Dict2Obj(d) for d in resp.json()] if resp.status_code == 200 else []

    def delete_extraction(self, extraction_id: int):
        resp = self.session.delete(f"{BASE_URL}/extractions/{extraction_id}")
        return resp.status_code in (200, 204)

    def create_extraction(self, extraction_data):
        resp = self.session.post(f"{BASE_URL}/extractions/", json=extraction_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    # --- Equipment API ---
    def get_equipment(self):
        resp = self.session.get(f"{BASE_URL}/equipment/")
        return [Dict2Obj(d) for d in resp.json()] if resp.status_code == 200 else []

    def create_equipment(self, equip_data):
        resp = self.session.post(f"{BASE_URL}/equipment/", json=equip_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def delete_equipment(self, equip_id):
        resp = self.session.delete(f"{BASE_URL}/equipment/{equip_id}")
        return resp.status_code == 200

    def add_kg_ground(self, equip_id, kg):
        resp = self.session.put(f"{BASE_URL}/equipment/{equip_id}/add_kg", params={"kg": kg})
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    # --- Maintenance Tasks API ---
    def get_maintenance_tasks(self):
        resp = self.session.get(f"{BASE_URL}/equipment/maintenance/")
        return [Dict2Obj(d) for d in resp.json()] if resp.status_code == 200 else []

    def create_maintenance_task(self, task_data):
        resp = self.session.post(f"{BASE_URL}/equipment/maintenance/", json=task_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def mark_maintenance_task_done(self, task_id):
        resp = self.session.put(f"{BASE_URL}/equipment/maintenance/{task_id}/done")
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    # --- Water Recipes API ---
    def get_water_recipes(self):
        resp = self.session.get(f"{BASE_URL}/water/")
        return [Dict2Obj(d) for d in resp.json()] if resp.status_code == 200 else []

    def create_water_recipe(self, recipe_data):
        resp = self.session.post(f"{BASE_URL}/water/", json=recipe_data)
        return Dict2Obj(resp.json()) if resp.status_code == 200 else None

    def delete_water_recipe(self, recipe_id):
        resp = self.session.delete(f"{BASE_URL}/water/{recipe_id}")
        return resp.status_code == 200

# Singleton instance for the app to use
api = APIClient()
