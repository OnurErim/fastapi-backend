from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
    func
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid

from database import Base

saved_announcements = Table(
    "saved_announcements",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("announcement_guid", UUID(as_uuid=True), ForeignKey("announcements.guid", ondelete="CASCADE"), primary_key=True)
)

class AnnouncementModel(Base):
    __tablename__ = "announcements"

    guid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    announcement_date = Column(DateTime(timezone=True), nullable=False)
    application_deadline = Column(DateTime(timezone=True), nullable=False)

    eligible_institution = Column(ARRAY(String), nullable=False)
    sectors = Column(ARRAY(String), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    image_url = Column(String, nullable=False, default="")
    link = Column(String, nullable=False, default="")
    project_duration = Column(String, nullable=False, default="")
    budget_support = Column(String, nullable=False, default="")
    application_language = Column(String, nullable=False, default="")

    saved_by_users = relationship(
        "UserModel",
        secondary=saved_announcements,
        back_populates="saved_announcements",
        lazy="joined"
    )