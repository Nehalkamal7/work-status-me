import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime, Date, JSON, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    integrations: Mapped[list["TenantIntegration"]] = relationship("TenantIntegration", back_populates="user", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    whatsapp_messages: Mapped[list["WhatsAppMessage"]] = relationship("WhatsAppMessage", back_populates="user", cascade="all, delete-orphan")
    whatsapp_summaries: Mapped[list["WhatsAppSummary"]] = relationship("WhatsAppSummary", back_populates="user", cascade="all, delete-orphan")

class TenantIntegration(Base):
    __tablename__ = "tenant_integrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Odoo Configuration
    odoo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    odoo_db: Mapped[str | None] = mapped_column(String(100), nullable=True)
    odoo_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    odoo_encrypted_password: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    
    # Google Sheets Configuration (List of sheet URLs and tab specs)
    google_sheets_urls: Mapped[dict | list] = mapped_column(JSON, default=list)
    
    # Chrome Extension Authentication API Key
    api_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    
    sync_interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="integrations")

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    source: Mapped[str] = mapped_column(String(50), default="MANUAL") # ODOO, GOOGLE_SHEETS, MANUAL, COMBINED
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True) # e.g. AA60843 or S02338
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(100), default="analysis") # stage: analysis, design, programming, testing, delivery, maintenance
    
    current_progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    weekly_target_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    last_weekly_percentage_submitted: Mapped[float] = mapped_column(Float, default=0.0)
    
    last_sync_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_metadata: Mapped[dict | list] = mapped_column(JSON, default=dict)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")

class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    group_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False) # deduplication

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="whatsapp_messages")

class WhatsAppSummary(Base):
    __tablename__ = "whatsapp_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    group_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_action_items: Mapped[list | dict] = mapped_column(JSON, default=list)
    identified_risks: Mapped[list | dict] = mapped_column(JSON, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="whatsapp_summaries")
