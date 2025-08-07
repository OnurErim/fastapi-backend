from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    func
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from database import Base
from models.announcement_model import saved_announcements

class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(100), nullable=False)

    role = Column(SqlEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.USER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    phone = Column(String(20), nullable=False, default="")
    linkedin = Column(String(255), nullable=False, default="")
    institution = Column(String(255), nullable=False, default="")
    profession = Column(String(100), nullable=False, default="")
    sectors = Column(ARRAY(String), nullable=False, default=[])

    saved_announcements = relationship(
        "AnnouncementModel",
        secondary=saved_announcements,
        back_populates="saved_by_users",
        lazy="joined"
    )

    password_entry = relationship(
        "PasswordModel",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan"
    )

class PasswordModel(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    last_changed = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("UserModel", back_populates="password_entry")