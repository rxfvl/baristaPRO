from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, EmailStr

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Bean Schemas ---
class BeanBase(BaseModel):
    roaster: str
    name: str
    origin_country: Optional[str] = None
    origin_region: Optional[str] = None
    origin_farm: Optional[str] = None
    variety: Optional[str] = None
    process: Optional[str] = None
    altitude_masl: Optional[int] = None
    notes: Optional[str] = None
    
    expected_acidity: Optional[float] = None
    expected_sweetness: Optional[float] = None
    expected_body: Optional[float] = None
    expected_bitterness: Optional[float] = None

class BeanCreate(BeanBase):
    pass

class BeanResponse(BeanBase):
    id: int
    user_id: int
    created_at: datetime
    batches: List['BeanBatchResponse'] = []
    class Config:
        from_attributes = True

# --- Bean Batch Schemas ---
class BeanBatchBase(BaseModel):
    bean_id: int
    roast_date: Optional[date] = None
    rest_days_min: int = 7
    rest_days_max: int = 14
    stock_grams: float = 0.0
    is_archived: bool = False

class BeanBatchCreate(BeanBatchBase):
    pass

class BeanBatchResponse(BeanBatchBase):
    id: int
    created_at: datetime
    degassing_status: str
    degassing_progress: float
    days_since_roast: Optional[int]
    bean: Optional['BeanResponse'] = None
    class Config:
        from_attributes = True

# --- Extraction Log Schemas ---
class ExtractionLogBase(BaseModel):
    bean_batch_id: Optional[int] = None
    equipment_id: Optional[int] = None
    dose_in: float = 18.0
    yield_out: float = 36.0
    extraction_time: int = 27
    water_temp: float = 93.0
    grind_size: Optional[str] = None
    pressure: float = 9.0
    pre_infusion_time: float = 0.0
    
    acidity: int = 5
    sweetness: int = 5
    body: int = 5
    bitterness: int = 5
    flavor_notes: Optional[str] = None
    score: float = 7.0
    is_locked: bool = False
    notes: Optional[str] = None
    
    tds: Optional[float] = None
    ey: Optional[float] = None
    image_path: Optional[str] = None

class ExtractionLogCreate(ExtractionLogBase):
    pass

class ExtractionLogResponse(ExtractionLogBase):
    id: int
    timestamp: datetime
    ratio: float
    ratio_str: str
    bean_batch: Optional['BeanBatchResponse'] = None
    class Config:
        from_attributes = True

# --- Resolve Forward References ---
# Pydantic requires resolving forward references when using nested models
BeanBatchResponse.model_rebuild()
ExtractionLogResponse.model_rebuild()

# --- Water Recipe Schemas ---
class WaterRecipeBase(BaseModel):
    name: str
    target_gh_ppm: float = 68.0
    target_kh_ppm: float = 40.0
    target_tds_ppm: int = 150
    mg_sulfate_g_per_l: float = 0.0
    sodium_bicarb_g_per_l: float = 0.0
    calcium_chloride_g_per_l: float = 0.0
    notes: Optional[str] = None

class WaterRecipeCreate(WaterRecipeBase):
    pass

class WaterRecipeResponse(WaterRecipeBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Equipment Schemas ---
class EquipmentBase(BaseModel):
    type: str = "Machine"
    brand: str
    model: str
    purchase_date: Optional[date] = None
    total_kg_ground: float = 0.0
    burr_change_interval_kg: float = 500.0
    last_burr_change_date: Optional[date] = None
    notes: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentResponse(EquipmentBase):
    id: int
    user_id: int
    burr_life_percent: float
    kg_until_burr_change: float
    class Config:
        from_attributes = True

# --- Maintenance Task Schemas ---
class MaintenanceTaskBase(BaseModel):
    equipment_id: int
    task_name: str
    frequency_days: int = 7
    last_done_date: Optional[date] = None
    next_due_date: Optional[date] = None
    notes: Optional[str] = None

class MaintenanceTaskCreate(MaintenanceTaskBase):
    pass

class MaintenanceTaskResponse(MaintenanceTaskBase):
    id: int
    is_overdue: bool
    is_urgent: bool
    days_until_due: Optional[int]
    class Config:
        from_attributes = True

# --- Catalog Option Schemas ---
class CatalogOptionBase(BaseModel):
    category: str
    name: str

class CatalogOptionCreate(CatalogOptionBase):
    pass

class CatalogOptionResponse(CatalogOptionBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

# --- AI Prediction Schemas ---
class FlavorPredictionRequest(BaseModel):
    bean_id: Optional[int] = None
    variety: Optional[str] = "Unknown"
    process: Optional[str] = "Unknown"
    origin_country: Optional[str] = "Unknown"
    altitude_masl: Optional[float] = 1200.0
    days_since_roast: Optional[float] = 14.0
    notes: Optional[str] = ""

class FlavorPredictionResponse(BaseModel):
    acidity: float
    sweetness: float
    body: float
    bitterness: float
    confidence: str

class ShotAdvisorRequest(BaseModel):
    dose_in: float
    yield_out: float
    extraction_time: float
    water_temp: float = 93.0
    pressure: float = 9.0
    pre_infusion_time: float = 0.0
    acidity: int = 5
    sweetness: int = 5
    body: int = 5
    bitterness: int = 5

class ShotAdvisorResponse(BaseModel):
    predicted_score: float
    suggested_params: Optional[dict] = None
    deltas: Optional[dict] = None
    suggested_score: Optional[float] = None
    diagnostic: Optional[str] = None
