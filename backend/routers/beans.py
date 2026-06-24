from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user
from ..ai.flavor_predictor import flavor_predictor

router = APIRouter()

@router.post("/predict_flavor", response_model=schemas.FlavorPredictionResponse)
def predict_flavor(req: schemas.FlavorPredictionRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        flavor_predictor.load()
        
        target = None
        if req.bean_id:
            db_bean = db.query(models.Bean).filter(models.Bean.id == req.bean_id, models.Bean.user_id == current_user.id).first()
            if db_bean:
                target = db_bean
        
        if not target:
            target = {
                "variety": req.variety,
                "process": req.process,
                "origin_country": req.origin_country,
                "altitude_masl": req.altitude_masl,
                "days_since_roast": req.days_since_roast,
                "notes": req.notes
            }

        res = flavor_predictor.predict(target)
        if not res:
            raise HTTPException(status_code=500, detail="Flavor predictor model not available")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.BeanResponse])
def read_beans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    beans = db.query(models.Bean).filter(models.Bean.user_id == current_user.id).offset(skip).limit(limit).all()
    return beans

@router.post("/", response_model=schemas.BeanResponse)
def create_bean(bean: schemas.BeanCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_bean = models.Bean(**bean.model_dump(), user_id=current_user.id)
    db.add(db_bean)
    db.commit()
    db.refresh(db_bean)
    return db_bean

@router.get("/{bean_id}", response_model=schemas.BeanResponse)
def read_bean(bean_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bean = db.query(models.Bean).filter(models.Bean.id == bean_id, models.Bean.user_id == current_user.id).first()
    if bean is None:
        raise HTTPException(status_code=404, detail="Bean not found")
    return bean

@router.put("/{bean_id}", response_model=schemas.BeanResponse)
def update_bean(bean_id: int, bean_update: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bean = db.query(models.Bean).filter(models.Bean.id == bean_id, models.Bean.user_id == current_user.id).first()
    if not bean:
        raise HTTPException(status_code=404, detail="Bean not found")
    for key, value in bean_update.items():
        if hasattr(bean, key):
            setattr(bean, key, value)
    db.commit()
    db.refresh(bean)
    return bean

@router.delete("/{bean_id}")
def delete_bean(bean_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bean = db.query(models.Bean).filter(models.Bean.id == bean_id, models.Bean.user_id == current_user.id).first()
    if not bean:
        raise HTTPException(status_code=404, detail="Bean not found")
    db.delete(bean)
    db.commit()
    return {"ok": True}

# --- Bean Batches ---
@router.get("/{bean_id}/batches", response_model=List[schemas.BeanBatchResponse])
def read_bean_batches(bean_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bean = db.query(models.Bean).filter(models.Bean.id == bean_id, models.Bean.user_id == current_user.id).first()
    if not bean:
        raise HTTPException(status_code=404, detail="Bean not found")
    return bean.batches

@router.post("/{bean_id}/batches", response_model=schemas.BeanBatchResponse)
def create_bean_batch(bean_id: int, batch: schemas.BeanBatchCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bean = db.query(models.Bean).filter(models.Bean.id == bean_id, models.Bean.user_id == current_user.id).first()
    if not bean:
        raise HTTPException(status_code=404, detail="Bean not found")
    
    db_batch = models.BeanBatch(**batch.model_dump())
    db_batch.bean_id = bean_id 
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch
