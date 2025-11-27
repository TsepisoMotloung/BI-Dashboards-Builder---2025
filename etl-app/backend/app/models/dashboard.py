from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    layout = Column(Text, nullable=True)  # JSON layout configuration
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", back_populates="dashboards", foreign_keys=[created_by])
    tabs = relationship("DashboardTab", back_populates="dashboard", cascade="all, delete-orphan", order_by="DashboardTab.order")
    permissions = relationship("DashboardPermission", back_populates="dashboard", cascade="all, delete-orphan")


class DashboardTab(Base):
    __tablename__ = "dashboard_tabs"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    config = Column(Text, nullable=True)  # JSON configuration

    # Relationships
    dashboard = relationship("Dashboard", back_populates="tabs")
    visualizations = relationship("Visualization", back_populates="tab", cascade="all, delete-orphan", order_by="Visualization.order")


class Visualization(Base):
    __tablename__ = "visualizations"

    id = Column(Integer, primary_key=True, index=True)
    tab_id = Column(Integer, ForeignKey("dashboard_tabs.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # bar, line, pie, scatter, etc.
    config = Column(Text, nullable=False)  # JSON configuration
    query = Column(Text, nullable=True)  # SQL or data query
    order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tab = relationship("DashboardTab", back_populates="visualizations")


class DashboardPermission(Base):
    __tablename__ = "dashboard_permissions"

    dashboard_id = Column(Integer, ForeignKey("dashboards.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permissions_json = Column(Text, nullable=False)  # JSON permissions (view, edit, etc.)

    # Relationships
    dashboard = relationship("Dashboard", back_populates="permissions")
    role = relationship("Role", back_populates="dashboard_permissions")
