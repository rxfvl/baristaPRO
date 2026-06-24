from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user
from ..ai.shot_advisor import advisor

router = APIRouter()

@router.post("/advise", response_model=schemas.ShotAdvisorResponse)
def advise_shot(req: schemas.ShotAdvisorRequest, current_user: models.User = Depends(get_current_user)):
    try:
        advisor.load()
        req_dict = req.model_dump()
        res = advisor.suggest(req_dict)
        if not res:
            raise HTTPException(status_code=500, detail="Shot advisor model not available")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.ExtractionLogResponse])
def read_extractions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # To ensure the extraction belongs to the user, we join with BeanBatch -> Bean -> User
    extractions = db.query(models.ExtractionLog).join(
        models.BeanBatch, models.ExtractionLog.bean_batch_id == models.BeanBatch.id
    ).join(
        models.Bean, models.BeanBatch.bean_id == models.Bean.id
    ).filter(
        models.Bean.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return extractions

@router.post("/", response_model=schemas.ExtractionLogResponse)
def create_extraction(extraction: schemas.ExtractionLogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Validate that the bean_batch belongs to the user
    if extraction.bean_batch_id:
        batch = db.query(models.BeanBatch).join(models.Bean).filter(
            models.BeanBatch.id == extraction.bean_batch_id,
            models.Bean.user_id == current_user.id
        ).first()
        if not batch:
            raise HTTPException(status_code=403, detail="Not authorized to use this bean batch")
            
    db_ext = models.ExtractionLog(**extraction.model_dump())
    db.add(db_ext)
    db.commit()
    db.refresh(db_ext)
    return db_ext
