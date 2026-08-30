from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.database import Base
from backend.app.models.asset import Asset


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    asset_id = Column(
        Integer,
        ForeignKey("assets.id"),
        nullable=False,
        index=True,
    )

    document_type = Column(
        String(50),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    mime_type = Column(
        String(100),
        nullable=True,
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    asset = relationship(
        Asset,
        backref="documents",
    )