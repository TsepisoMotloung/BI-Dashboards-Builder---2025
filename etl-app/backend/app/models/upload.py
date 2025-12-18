from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class UploadStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class UploadHistory(Base):
    __tablename__ = "upload_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    model_id = Column(Integer, ForeignKey("data_models.id", ondelete="CASCADE"), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(Enum(UploadStatus), default=UploadStatus.PENDING, nullable=False)
    records_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    upload_metadata = Column(Text, nullable=True)  # JSON metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="upload_history")
    data_model = relationship("DataModel", back_populates="upload_history")
