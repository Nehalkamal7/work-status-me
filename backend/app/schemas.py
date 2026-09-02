from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Tenant Integration Schemas ---
class TenantIntegrationCreate(BaseModel):
    odoo_url: Optional[str] = None
    odoo_db: Optional[str] = None
    odoo_username: Optional[str] = None
    odoo_password: Optional[str] = None
    google_sheets_urls: Optional[List[str]] = Field(default_factory=list)
    sync_interval_seconds: Optional[int] = 60

class TenantIntegrationResponse(BaseModel):
    id: str
    user_id: str
    odoo_url: Optional[str] = None
    odoo_db: Optional[str] = None
    odoo_username: Optional[str] = None
    has_odoo_password: bool = False
    google_sheets_urls: List[str] = Field(default_factory=list)
    api_key: str
    sync_interval_seconds: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Project Schemas ---
class ProjectCreate(BaseModel):
    name: str
    external_id: Optional[str] = None
    source: Optional[str] = "MANUAL"
    status: Optional[str] = "analysis"
    current_progress_percentage: Optional[float] = 0.0
    weekly_target_percentage: Optional[float] = 0.0
    raw_metadata: Optional[dict] = Field(default_factory=dict)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    current_progress_percentage: Optional[float] = None
    weekly_target_percentage: Optional[float] = None
    last_weekly_percentage_submitted: Optional[float] = None
    raw_metadata: Optional[dict] = None

class ProjectResponse(BaseModel):
    id: str
    user_id: str
    source: str
    external_id: Optional[str] = None
    name: str
    status: str
    current_progress_percentage: float
    weekly_target_percentage: float
    last_weekly_percentage_submitted: float
    last_sync_timestamp: Optional[datetime] = None
    raw_metadata: dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

# --- Task Schemas ---
class TaskCreate(BaseModel):
    project_id: str
    title: str
    stage: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[datetime] = None
    progress_percentage: Optional[float] = 0.0

class TaskResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    title: str
    stage: Optional[str] = None
    assignee: Optional[str] = None
    deadline: Optional[datetime] = None
    progress_percentage: float
    model_config = ConfigDict(from_attributes=True)

# --- WhatsApp & Chrome Extension Ingestion Schemas ---
class SingleWhatsAppMessage(BaseModel):
    group_name: str
    sender: str
    message_text: str
    message_timestamp: Optional[datetime] = None

class WhatsAppIngestRequest(BaseModel):
    messages: List[SingleWhatsAppMessage]

class WhatsAppMessageResponse(BaseModel):
    id: str
    group_name: str
    sender: str
    message_text: str
    message_timestamp: datetime
    content_hash: str
    model_config = ConfigDict(from_attributes=True)

# --- AI Structured Pipeline Schemas ---
class ActionItem(BaseModel):
    task: str = Field(..., description="Action item description")
    owner: Optional[str] = Field(None, description="Person responsible")
    urgency: str = Field("Normal", description="High, Normal, or Low")

class ChatExecutiveSummary(BaseModel):
    summary: str = Field(..., description="High-level executive summary of the WhatsApp conversation")
    action_items: List[ActionItem] = Field(default_factory=list, description="Extracted actionable tasks")
    blockers_and_risks: List[str] = Field(default_factory=list, description="Identified risks, delays, or dependencies")
    confidence_score: float = Field(0.95, description="Confidence score from 0.0 to 1.0")

class WhatsAppSummaryResponse(BaseModel):
    id: str
    user_id: str
    group_name: str
    executive_summary: str
    extracted_action_items: List[dict]
    identified_risks: List[str]
    generated_at: datetime
    model_config = ConfigDict(from_attributes=True)
