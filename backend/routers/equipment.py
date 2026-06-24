from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.EquipmentResponse])
def read_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    equip = db.query(models.Equipment).filter(models.Equipment.user_id == current_user.id).offset(skip).limit(limit).all()
    return equip

@router.post("/", response_model=schemas.EquipmentResponse)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_equip = models.Equipment(**equipment.model_dump(), user_id=current_user.id)
    db.add(db_equip)
    db.commit()
    db.refresh(db_equip)
    return db_equip

@router.delete("/{equip_id}")
def delete_equipment(equip_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    equip = db.query(models.Equipment).filter(models.Equipment.id == equip_id, models.Equipment.user_id == current_user.id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipment not found")
    db.delete(equip)
    db.commit()
    return {"ok": True}

@router.put("/{equip_id}/add_kg")
def add_kg_ground(equip_id: int, kg: float, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    equip = db.query(models.Equipment).filter(models.Equipment.id == equip_id, models.Equipment.user_id == current_user.id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipment not found")
    equip.total_kg_ground += kg
    db.commit()
    db.refresh(equip)
    return equip

# --- Maintenance Tasks ---
@router.get("/maintenance/", response_model=List[schemas.MaintenanceTaskResponse])
def get_maintenance_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Get all maintenance tasks for equipment owned by user
    tasks = db.query(models.MaintenanceTask).join(models.Equipment).filter(models.Equipment.user_id == current_user.id).all()
    return tasks

@router.post("/maintenance/", response_model=schemas.MaintenanceTaskResponse)
def create_maintenance_task(task: schemas.MaintenanceTaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify equipment belongs to user
    equip = db.query(models.Equipment).filter(models.Equipment.id == task.equipment_id, models.Equipment.user_id == current_user.id).first()
    if not equip:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db_task = models.MaintenanceTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/maintenance/{task_id}/done")
def mark_task_done(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.MaintenanceTask).join(models.Equipment).filter(models.MaintenanceTask.id == task_id, models.Equipment.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.mark_done()
    db.commit()
    db.refresh(task)
    return task
