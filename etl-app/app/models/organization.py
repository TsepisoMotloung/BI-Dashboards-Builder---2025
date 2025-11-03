from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class OrgUnitType(str, enum.Enum):
    COMPANY = "company"
    DIVISION = "division"
    DEPARTMENT = "department"
    TEAM = "team"


class OrganizationalUnit(Base):
    __tablename__ = "organizational_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(OrgUnitType), nullable=False)
    parent_id = Column(Integer, ForeignKey("organizational_units.id", ondelete="CASCADE"), nullable=True)
    path = Column(Text, nullable=True)  # Materialized path for hierarchy
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    parent = relationship("OrganizationalUnit", remote_side=[id], backref="children")
    user_organizational_units = relationship("UserOrganizationalUnit", back_populates="org_unit", cascade="all, delete-orphan")


class UserOrganizationalUnit(Base):
    __tablename__ = "user_organizational_units"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    org_unit_id = Column(Integer, ForeignKey("organizational_units.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="user_organizational_units")
    org_unit = relationship("OrganizationalUnit", back_populates="user_organizational_units")
