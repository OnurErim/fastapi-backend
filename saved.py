from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import UserModel
from models.announcement_model import AnnouncementModel
from schemas import AnnouncementResponse

router = APIRouter(
    prefix="/saved-announcements",
    tags=["Saved (Test)"],
    include_in_schema=False  
)


def get_dummy_user(db: Session = Depends(get_db)) -> UserModel:
    user = db.query(UserModel).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return user


@router.post("/{announcement_id}", status_code=status.HTTP_200_OK)
def save_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_dummy_user)
):
    announcement = db.query(AnnouncementModel).filter_by(id=announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Duyuru bulunamadı.")

    if announcement in current_user.saved_announcements:
        raise HTTPException(status_code=400, detail="Zaten kaydedilmiş.")

    current_user.saved_announcements.append(announcement)
    db.commit()
    return {"message": "Duyuru kaydedildi."}


@router.delete("/{announcement_id}", status_code=status.HTTP_200_OK)
def unsave_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_dummy_user)
):
    announcement = db.query(AnnouncementModel).filter_by(id=announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Duyuru bulunamadı.")

    if announcement not in current_user.saved_announcements:
        raise HTTPException(status_code=400, detail="Zaten kaydedilmemiş.")

    current_user.saved_announcements.remove(announcement)
    db.commit()
    return {"message": "Duyuru kayıttan silindi."}


@router.get("/", response_model=List[AnnouncementResponse])
def list_saved_announcements(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_dummy_user)
):
    return current_user.saved_announcements