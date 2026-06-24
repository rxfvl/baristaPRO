from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    Integer, Float, String, Text, Boolean,
    Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    """User account for Authentication and Data Isolation."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(50))
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    beans: Mapped[List["Bean"]] = relationship("Bean", back_populates="user", cascade="all, delete-orphan")
    water_recipes: Mapped[List["WaterRecipe"]] = relationship("WaterRecipe", back_populates="user", cascade="all, delete-orphan")
    equipments: Mapped[List["Equipment"]] = relationship("Equipment", back_populates="user", cascade="all, delete-orphan")
    catalog_options: Mapped[List["CatalogOption"]] = relationship("CatalogOption", back_populates="user", cascade="all, delete-orphan")


class CatalogOption(Base):
    """Saved values for dropdowns so they don't disappear when beans are deleted."""
    __tablename__ = "catalog_options"

    id:       Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:  Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False) # roaster, country, region, farm, variety, process
    name:     Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="catalog_options")


class Bean(Base):
    """Coffee bean catalog entry."""
    __tablename__ = "beans"

    id:                 Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:            Mapped[int]            = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    roaster:            Mapped[str]            = mapped_column(String(200), nullable=False)
    name:               Mapped[str]            = mapped_column(String(200), nullable=False)
    origin_country:     Mapped[Optional[str]]  = mapped_column(String(100))
    origin_region:      Mapped[Optional[str]]  = mapped_column(String(100))
    origin_farm:        Mapped[Optional[str]]  = mapped_column(String(100))
    variety:            Mapped[Optional[str]]  = mapped_column(String(100))
    process:            Mapped[Optional[str]]  = mapped_column(String(80))
    altitude_masl:      Mapped[Optional[int]]  = mapped_column(Integer)
    notes:              Mapped[Optional[str]]  = mapped_column(Text)
    created_at:         Mapped[datetime]       = mapped_column(DateTime, default=func.now())
    
    # AI predicted expected profile
    expected_acidity:   Mapped[Optional[float]] = mapped_column(Float)
    expected_sweetness: Mapped[Optional[float]] = mapped_column(Float)
    expected_body:      Mapped[Optional[float]] = mapped_column(Float)
    expected_bitterness:Mapped[Optional[float]] = mapped_column(Float)

    user: Mapped["User"] = relationship("User", back_populates="beans")
    batches: Mapped[List["BeanBatch"]] = relationship(
        "BeanBatch", back_populates="bean", cascade="all, delete-orphan"
    )


class BeanBatch(Base):
    """A specific roast or purchase of a coffee bean."""
    __tablename__ = "bean_batches"

    id:             Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    bean_id:        Mapped[int]            = mapped_column(Integer, ForeignKey("beans.id"), nullable=False)
    roast_date:     Mapped[Optional[date]] = mapped_column(Date)
    rest_days_min:  Mapped[int]            = mapped_column(Integer, default=7)
    rest_days_max:  Mapped[int]            = mapped_column(Integer, default=14)
    stock_grams:    Mapped[float]          = mapped_column(Float, default=0.0)
    created_at:     Mapped[datetime]       = mapped_column(DateTime, default=func.now())
    is_archived:    Mapped[bool]           = mapped_column(Boolean, default=False)

    bean: Mapped["Bean"] = relationship("Bean", back_populates="batches")
    
    extractions: Mapped[List["ExtractionLog"]] = relationship(
        "ExtractionLog", back_populates="bean_batch", cascade="all, delete-orphan"
    )

    @property
    def days_since_roast(self) -> Optional[int]:
        if self.roast_date:
            return (date.today() - self.roast_date).days
        return None

    @property
    def degassing_status(self) -> str:
        """Returns: 'resting', 'peak', 'declining', 'stale', 'unknown'"""
        days = self.days_since_roast
        if days is None:
            return "unknown"
        if days < self.rest_days_min:
            return "resting"
        if days <= self.rest_days_max:
            return "peak"
        if days <= self.rest_days_max + 14:
            return "declining"
        return "stale"

    @property
    def degassing_progress(self) -> float:
        """0.0 to 1.0 progress toward rest_days_min."""
        days = self.days_since_roast
        if days is None or self.rest_days_min == 0:
            return 0.0
        return min(days / self.rest_days_min, 1.0)


class ExtractionLog(Base):
    """Single espresso extraction / recipe log entry."""
    __tablename__ = "extraction_logs"

    id:               Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    bean_batch_id:    Mapped[Optional[int]]  = mapped_column(Integer, ForeignKey("bean_batches.id"), nullable=True)
    timestamp:        Mapped[datetime]       = mapped_column(DateTime, default=func.now())
    dose_in:          Mapped[float]          = mapped_column(Float, default=18.0)
    yield_out:        Mapped[float]          = mapped_column(Float, default=36.0)
    extraction_time:  Mapped[int]            = mapped_column(Integer, default=27)
    water_temp:       Mapped[float]          = mapped_column(Float, default=93.0)
    grind_size:       Mapped[Optional[str]]  = mapped_column(String(80))
    pressure:         Mapped[float]          = mapped_column(Float, default=9.0)
    pre_infusion_time:Mapped[float]          = mapped_column(Float, default=0.0)
    # Sensory (1–10)
    acidity:          Mapped[int]            = mapped_column(Integer, default=5)
    sweetness:        Mapped[int]            = mapped_column(Integer, default=5)
    body:             Mapped[int]            = mapped_column(Integer, default=5)
    bitterness:       Mapped[int]            = mapped_column(Integer, default=5)
    flavor_notes:     Mapped[Optional[str]]  = mapped_column(Text)
    score:            Mapped[float]          = mapped_column(Float, default=7.0)
    is_locked:        Mapped[bool]           = mapped_column(Boolean, default=False)
    notes:            Mapped[Optional[str]]  = mapped_column(Text)
    
    # Advanced fields
    equipment_id:     Mapped[Optional[int]]  = mapped_column(Integer, ForeignKey("equipment.id"), nullable=True)
    tds:              Mapped[Optional[float]] = mapped_column(Float)
    ey:               Mapped[Optional[float]] = mapped_column(Float)
    image_path:       Mapped[Optional[str]]  = mapped_column(String(255))

    bean_batch: Mapped[Optional["BeanBatch"]] = relationship("BeanBatch", back_populates="extractions")
    equipment:  Mapped[Optional["Equipment"]] = relationship("Equipment")

    @property
    def ratio(self) -> float:
        if self.dose_in and self.dose_in > 0:
            return round(self.yield_out / self.dose_in, 2)
        return 0.0

    @property
    def ratio_str(self) -> str:
        return f"1:{self.ratio:.1f}"


class WaterRecipe(Base):
    """Saved water mineral recipe."""
    __tablename__ = "water_recipes"

    id:                       Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:                  Mapped[int]            = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name:                     Mapped[str]            = mapped_column(String(200), nullable=False)
    target_gh_ppm:            Mapped[float]          = mapped_column(Float, default=68.0)
    target_kh_ppm:            Mapped[float]          = mapped_column(Float, default=40.0)
    target_tds_ppm:           Mapped[int]            = mapped_column(Integer, default=150)
    mg_sulfate_g_per_l:       Mapped[float]          = mapped_column(Float, default=0.0)
    sodium_bicarb_g_per_l:    Mapped[float]          = mapped_column(Float, default=0.0)
    calcium_chloride_g_per_l: Mapped[float]          = mapped_column(Float, default=0.0)
    notes:                    Mapped[Optional[str]]  = mapped_column(Text)
    created_at:               Mapped[datetime]       = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="water_recipes")


class Equipment(Base):
    """Espresso machine or grinder entry."""
    __tablename__ = "equipment"

    id:                      Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:                 Mapped[int]            = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type:                    Mapped[str]            = mapped_column(String(50), default="Machine")  # Machine / Grinder
    brand:                   Mapped[str]            = mapped_column(String(100), nullable=False)
    model:                   Mapped[str]            = mapped_column(String(100), nullable=False)
    purchase_date:           Mapped[Optional[date]] = mapped_column(Date)
    total_kg_ground:         Mapped[float]          = mapped_column(Float, default=0.0)
    burr_change_interval_kg: Mapped[float]          = mapped_column(Float, default=500.0)
    last_burr_change_date:   Mapped[Optional[date]] = mapped_column(Date)
    notes:                   Mapped[Optional[str]]  = mapped_column(Text)

    user: Mapped["User"] = relationship("User", back_populates="equipments")
    maintenance_tasks: Mapped[List["MaintenanceTask"]] = relationship(
        "MaintenanceTask", back_populates="equipment", cascade="all, delete-orphan"
    )

    @property
    def burr_life_percent(self) -> float:
        if self.burr_change_interval_kg > 0:
            return min(self.total_kg_ground / self.burr_change_interval_kg, 1.0)
        return 0.0

    @property
    def kg_until_burr_change(self) -> float:
        remaining = self.burr_change_interval_kg - self.total_kg_ground
        return max(remaining, 0.0)


class MaintenanceTask(Base):
    """Recurring maintenance task tied to a piece of equipment."""
    __tablename__ = "maintenance_tasks"

    id:              Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id:    Mapped[int]            = mapped_column(Integer, ForeignKey("equipment.id"), nullable=False)
    task_name:       Mapped[str]            = mapped_column(String(200), nullable=False)
    frequency_days:  Mapped[int]            = mapped_column(Integer, default=7)
    last_done_date:  Mapped[Optional[date]] = mapped_column(Date)
    next_due_date:   Mapped[Optional[date]] = mapped_column(Date)
    notes:           Mapped[Optional[str]]  = mapped_column(Text)

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="maintenance_tasks")

    def mark_done(self):
        from datetime import timedelta
        self.last_done_date = date.today()
        self.next_due_date = date.today() + timedelta(days=self.frequency_days)

    @property
    def is_overdue(self) -> bool:
        if self.next_due_date:
            return date.today() > self.next_due_date
        return False

    @property
    def is_urgent(self) -> bool:
        from datetime import timedelta
        if self.next_due_date:
            return date.today() >= (self.next_due_date - timedelta(days=3))
        return False

    @property
    def days_until_due(self) -> Optional[int]:
        if self.next_due_date:
            return (self.next_due_date - date.today()).days
        return None
