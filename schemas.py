from typing import List, Optional, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo, ConfigDict, constr
from enum import Enum
import re

# 🔒 Regex zinciri
REGEX = {
    "name": r"^[a-zA-ZçÇğĞıİöÖşŞüÜ\s]+$",
    "phone": r"^\+?\d{10,15}$",
    "institution": r"^[\w\sçÇğĞıİöÖşŞüÜ\-&]+$",
    "linkedin": r"^https:\/\/(www\.)?linkedin\.com\/.+$",
    "url": r"^https?:\/\/[^?\s]+$",
    "description": r"^.{1,1000}$",
    "password": r"^(?=.*[A-Z])(?=.*\d).{8,}$"
}

FORBIDDEN_URL_PARTS = ["docs", "redoc", "openapi.json", "?", "&"]

# 🎭 Rol enum
class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"

# 🔐 Token şemaları
class TokenData(BaseModel):
    sub: str
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    model_config = ConfigDict(from_attributes=True)

# 📝 Kayıt ve giriş
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    confirm_password: str

    @field_validator("full_name")
    def validate_full_name(cls, v: str) -> str:
        if not re.match(REGEX["name"], v):
            raise ValueError("Tam ad sadece harf ve boşluk içermelidir.")
        return v

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if not re.match(REGEX["password"], v):
            raise ValueError("Şifre en az 8 karakter olmalı, 1 büyük harf ve 1 rakam içermelidir.")
        return v

    @field_validator("confirm_password")
    def validate_match(cls, v: str, info: ValidationInfo) -> str:
        if v != info.data.get("password"):
            raise ValueError("Şifreler birbiriyle eşleşmelidir.")
        return v

    model_config = ConfigDict(from_attributes=False)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=False)

# 🔑 Şifre değiştirme
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    def validate_new(cls, v: str) -> str:
        if not re.match(REGEX["password"], v):
            raise ValueError("Yeni şifre en az 8 karakter olmalı, 1 büyük harf ve 1 rakam içermelidir.")
        return v

    @field_validator("confirm_new_password")
    def validate_new_match(cls, v: str, info: ValidationInfo) -> str:
        if v != info.data.get("new_password"):
            raise ValueError("Yeni şifreler birbiriyle eşleşmelidir.")
        return v

    model_config = ConfigDict(from_attributes=False)

# 👤 Profil tamamlama ve güncelleme
class ProfileCompleteRequest(BaseModel):
    full_name: str
    sectors: List[str]
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    institution: Optional[str] = None
    profession: Optional[str] = None

    @field_validator("full_name")
    def validate_full_name(cls, v: str) -> str:
        if not re.match(REGEX["name"], v):
            raise ValueError("Tam ad sadece harf ve boşluk içermelidir.")
        return v

    @field_validator("phone")
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(REGEX["phone"], v):
            raise ValueError("Telefon numarası geçerli formatta olmalıdır. Örn: +905xxxxxxxxx")
        return v

    @field_validator("linkedin")
    def validate_linkedin(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(REGEX["linkedin"], v):
            raise ValueError("LinkedIn bağlantısı geçerli bir URL olmalıdır.")
        return v

    @field_validator("institution")
    def validate_institution(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(REGEX["institution"], v):
            raise ValueError("Kurum adı geçerli karakterler içermelidir.")
        return v

    model_config = ConfigDict(from_attributes=False)

class ProfileUpdateRequest(ProfileCompleteRequest):
    full_name: Optional[str] = None
    sectors: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=False)

# 📢 Duyuru oluşturma ve güncelleme
class AnnouncementCreateRequest(BaseModel):
    title: str
    description: str
    announcement_date: datetime
    application_deadline: datetime
    image_url: str
    link: str
    eligible_institution: List[str]
    project_duration: str
    budget_support: str
    application_language: str
    sectors: List[str]

    @field_validator("title")
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Başlık en az 3 karakter olmalıdır.")
        return v

    @field_validator("description")
    def validate_description(cls, v: str) -> str:
        if not re.match(REGEX["description"], v):
            raise ValueError("Açıklama 1 ile 1000 karakter arasında olmalıdır.")
        return v

    @field_validator("image_url", "link")
    def validate_url(cls, v: str) -> str:
        if any(part in v for part in FORBIDDEN_URL_PARTS):
            raise ValueError("Geçersiz veya güvenli olmayan bağlantı girildi.")
        return v

    model_config = ConfigDict(from_attributes=False)

class AnnouncementUpdateRequest(AnnouncementCreateRequest):
    title: Optional[str] = None
    description: Optional[str] = None
    announcement_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    image_url: Optional[str] = None
    link: Optional[str] = None
    eligible_institution: Optional[List[str]] = None
    project_duration: Optional[str] = None
    budget_support: Optional[str] = None
    application_language: Optional[str] = None
    sectors: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=False)

# 📄 Duyuru çıktıları
class AnnouncementSummary(BaseModel):
    guid: UUID
    title: str
    application_deadline: datetime
    model_config = ConfigDict(from_attributes=True)

class AnnouncementResponse(BaseModel):
    guid: UUID
    title: str
    description: str
    announcement_date: datetime
    application_deadline: datetime
    image_url: str
    link: str
    eligible_institution: List[str]
    project_duration: str
    budget_support: str
    application_language: str
    sectors: List[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# 👤 Kullanıcı çıktısı
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    linkedin: str
    institution: str
    profession: str
    sectors: List[str]
    saved_announcements: List[AnnouncementSummary] = []
    model_config = ConfigDict(from_attributes=True)

# 🏷️ Sektör çıktısı
class SectorItem(BaseModel):
    nace_code: str
    name: str
    model_config = ConfigDict(from_attributes=True)