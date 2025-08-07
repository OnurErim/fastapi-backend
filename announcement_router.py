from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from models.announcement_model import AnnouncementModel
from models.user_model import UserModel
from schemas import (
    AnnouncementResponse,
    AnnouncementCreateRequest,
    AnnouncementUpdateRequest
)
from security import get_current_user, get_current_admin_user

router = APIRouter(prefix="/announcements")
limiter = Limiter(key_func=get_remote_address)

# -------------------------------
# 🔵 GENEL DUYURULAR (Token gerekmez)
# -------------------------------

@router.get("/all", response_model=List[AnnouncementResponse], tags=["Public Announcements"])
@limiter.limit("10/minute")
def list_all_announcements(request: Request, db: Session = Depends(get_db)):
    return db.query(AnnouncementModel).order_by(AnnouncementModel.created_at.desc()).all()

@router.get("/active", response_model=List[AnnouncementResponse], tags=["Public Announcements"])
@limiter.limit("10/minute")
def list_active_announcements(request: Request, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return (
        db.query(AnnouncementModel)
        .filter(AnnouncementModel.application_deadline > now)
        .order_by(AnnouncementModel.created_at.desc())
        .all()
    )

@router.get("/passive", response_model=List[AnnouncementResponse], tags=["Public Announcements"])
@limiter.limit("10/minute")
def list_passive_announcements(request: Request, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    return (
        db.query(AnnouncementModel)
        .filter(AnnouncementModel.application_deadline <= now)
        .order_by(AnnouncementModel.created_at.desc())
        .all()
    )

# -------------------------------
# 🔴 ADMIN DUYURU İŞLEMLERİ (Token + Yetki)
# -------------------------------

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED, tags=["Admin Announcements"])
@limiter.limit("5/minute")
def create_announcement(
    request: Request,
    data: AnnouncementCreateRequest,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    announcement = AnnouncementModel(**data.model_dump())
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement

@router.patch("/{announcement_guid}", response_model=AnnouncementResponse, tags=["Admin Announcements"])
@limiter.limit("5/minute")
def update_announcement(
    request: Request,
    announcement_guid: UUID,
    data: AnnouncementUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    announcement = db.query(AnnouncementModel).filter_by(guid=announcement_guid).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Güncellenecek duyuru bulunamadı.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(announcement, field, value)

    db.commit()
    db.refresh(announcement)
    return announcement

@router.delete("/{announcement_guid}", status_code=status.HTTP_200_OK, tags=["Admin Announcements"])
@limiter.limit("5/minute")
def delete_announcement(
    request: Request,
    announcement_guid: UUID,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin_user)
):
    announcement = db.query(AnnouncementModel).filter_by(guid=announcement_guid).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Silinecek duyuru bulunamadı.")

    db.delete(announcement)
    db.commit()
    return {"message": "Duyuru silindi."}

# -------------------------------
# 🟡 KULLANICI DUYURULARI (Token zorunlu)
# -------------------------------

@router.get("/by-sector", response_model=List[AnnouncementResponse], tags=["User Announcements"])
@limiter.limit("10/minute")
def list_announcements_by_user_sector(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return (
        db.query(AnnouncementModel)
        .filter(AnnouncementModel.sectors.overlap(current_user.sectors))
        .order_by(AnnouncementModel.created_at.desc())
        .all()
    )

# -------------------------------
# 🟣 KAYDEDİLEN DUYURULAR (Token zorunlu)
# -------------------------------

@router.post("/{announcement_guid}/save", status_code=status.HTTP_200_OK, tags=["Saved Announcements"])
@limiter.limit("10/minute")
def save_announcement(
    request: Request,
    announcement_guid: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    announcement = db.query(AnnouncementModel).filter_by(guid=announcement_guid).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Duyuru bulunamadı.")

    if announcement in current_user.saved_announcements:
        raise HTTPException(status_code=400, detail="Bu duyuru zaten kaydedilmiş.")

    current_user.saved_announcements.append(announcement)
    db.commit()
    return {"message": "Duyuru başarıyla kaydedildi."}

@router.get("/saved", response_model=List[AnnouncementResponse], tags=["Saved Announcements"])
@limiter.limit("10/minute")
def list_saved_announcements(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return sorted(
        current_user.saved_announcements,
        key=lambda a: a.created_at,
        reverse=True
    )

@router.delete("/{announcement_guid}/unsave", status_code=status.HTTP_200_OK, tags=["Saved Announcements"])
@limiter.limit("10/minute")
def unsave_announcement(
    request: Request,
    announcement_guid: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    announcement = db.query(AnnouncementModel).filter_by(guid=announcement_guid).first()
    if not announcement or announcement not in current_user.saved_announcements:
        raise HTTPException(status_code=404, detail="Kaldırılacak duyuru bulunamadı.")

    current_user.saved_announcements.remove(announcement)
    db.commit()
    return {"message": "Duyuru kaydı kaldırıldı."}