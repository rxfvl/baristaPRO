from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[schemas.WaterRecipeResponse])
def read_water_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    recipes = db.query(models.WaterRecipe).filter(models.WaterRecipe.user_id == current_user.id).offset(skip).limit(limit).all()
    return recipes

@router.post("/", response_model=schemas.WaterRecipeResponse)
def create_water_recipe(recipe: schemas.WaterRecipeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_recipe = models.WaterRecipe(**recipe.model_dump(), user_id=current_user.id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe
