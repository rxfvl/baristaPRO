from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from pathlib import Path

from ..database import get_db
from ..models import User
from ..schemas import UserResponse, UserUpdate, PasswordUpdate
from ..auth_utils import get_password_hash, verify_password
from .auth import get_current_user

router = APIRouter()

# Directory to save profile pictures
STATIC_DIR = Path("/app/static/avatars")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.nickname is not None:
        current_user.nickname = user_update.nickname
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/password")
def update_password(
    passwords: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")
    
    current_user.hashed_password = get_password_hash(passwords.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.post("/me/avatar", response_model=UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure it's an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename to avoid caching issues
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = STATIC_DIR / filename
    
    # Remove old avatar if exists
    if current_user.profile_picture_url:
        old_file = Path("/app") / current_user.profile_picture_url.lstrip("/")
        if old_file.exists() and old_file.is_file():
            try:
                old_file.unlink()
            except Exception:
                pass

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    current_user.profile_picture_url = f"/static/avatars/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user
