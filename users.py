from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import UserModel
from schemas import (
    UserResponse,
    ProfileCompleteRequest,
    ProfileUpdateRequest,
    PasswordChangeRequest
)
from dependencies import get_current_user
from security import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.post("/profile/complete", response_model=UserResponse)
def complete_profile(
    data: ProfileCompleteRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    current_user.full_name   = data.full_name
    current_user.sectors     = data.sectors
    current_user.phone       = data.phone
    current_user.linkedin    = data.linkedin
    current_user.institution = data.institution
    current_user.profession  = data.profession

    db.commit()
    db.refresh(current_user)
    return current_user


@router.patch("/profile/update", response_model=UserResponse)
def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    for field in [
        "full_name", "sectors", "phone",
        "linkedin", "institution", "profession"
    ]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.patch("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Eski şifre yanlış."
        )

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Şifre başarıyla değiştirildi"}


@router.get("/", response_model=List[UserResponse], include_in_schema=False)
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()