from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class RelationType(str, enum.Enum):
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:N"
    MANY_TO_MANY = "N:M"


class DataModel(Base):
    __tablename__ = "data_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    schema_json = Column(Text, nullable=False)  # JSON schema definition
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", backref="data_models")
    upload_history = relationship("UploadHistory", back_populates="data_model", cascade="all, delete-orphan")
    source_relationships = relationship(
        "DataRelationship",
        foreign_keys="DataRelationship.source_model_id",
        back_populates="source_model",
        cascade="all, delete-orphan"
    )
    target_relationships = relationship(
        "DataRelationship",
        foreign_keys="DataRelationship.target_model_id",
        back_populates="target_model",
        cascade="all, delete-orphan"
    )


class DataRelationship(Base):
    __tablename__ = "data_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_model_id = Column(Integer, ForeignKey("data_models.id", ondelete="CASCADE"), nullable=False)
    target_model_id = Column(Integer, ForeignKey("data_models.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(RelationType), nullable=False)
    config = Column(Text, nullable=True)  # JSON config with field mappings
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    source_model = relationship("DataModel", foreign_keys=[source_model_id], back_populates="source_relationships")
    target_model = relationship("DataModel", foreign_keys=[target_model_id], back_populates="target_relationships")
