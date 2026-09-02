import hashlib
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, TenantIntegration, WhatsAppMessage, WhatsAppSummary
from app.schemas import WhatsAppIngestRequest, WhatsAppMessageResponse, WhatsAppSummaryResponse
from app.services.ai_service import AIService
from app.api.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp & Chrome Extension"])

async def get_tenant_by_api_key(x_api_key: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> TenantIntegration:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    stmt = select(TenantIntegration).where(TenantIntegration.api_key == x_api_key)
    res = await db.execute(stmt)
    integration = res.scalars().first()
    if not integration:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return integration

@router.post("/ingest")
async def ingest_whatsapp_messages(
    payload: WhatsAppIngestRequest,
    tenant: TenantIntegration = Depends(get_tenant_by_api_key),
    db: AsyncSession = Depends(get_db)
):
    user_id = tenant.user_id
    inserted_count = 0

    for msg in payload.messages:
        # Calculate content hash for deduplication
        raw_sig = f"{user_id}:{msg.group_name}:{msg.sender}:{msg.message_text.strip()}"
        content_hash = hashlib.sha256(raw_sig.encode()).hexdigest()

        # Check existing
        stmt = select(WhatsAppMessage).where(
            WhatsAppMessage.user_id == user_id,
            WhatsAppMessage.content_hash == content_hash
        )
        existing = (await db.execute(stmt)).scalars().first()

        if not existing:
            new_msg = WhatsAppMessage(
                user_id=user_id,
                group_name=msg.group_name.strip(),
                sender=msg.sender.strip(),
                message_text=msg.message_text.strip(),
                message_timestamp=msg.message_timestamp or datetime.now(timezone.utc),
                content_hash=content_hash
            )
            db.add(new_msg)
            inserted_count += 1

    await db.commit()
    return {"status": "success", "inserted_count": inserted_count, "total_received": len(payload.messages)}

@router.get("/messages", response_model=List[WhatsAppMessageResponse])
async def list_whatsapp_messages(
    group_name: Optional[str] = None,
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WhatsAppMessage).where(WhatsAppMessage.user_id == current_user.id)
    if group_name:
        stmt = stmt.where(WhatsAppMessage.group_name == group_name)
    stmt = stmt.order_by(WhatsAppMessage.message_timestamp.desc()).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/analyze/{group_name}", response_model=WhatsAppSummaryResponse)
async def analyze_whatsapp_group(
    group_name: str,
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WhatsAppMessage).where(
        WhatsAppMessage.user_id == current_user.id,
        WhatsAppMessage.group_name == group_name
    ).order_by(WhatsAppMessage.message_timestamp.desc()).limit(100)
    
    messages = (await db.execute(stmt)).scalars().all()
    if not messages:
        # Generate graceful fallback summary if no messages logged yet
        return WhatsAppSummaryResponse(
            id="ws_demo_summary",
            user_id=current_user.id,
            group_name=group_name,
            executive_summary=f"ملاءمة مبدئية لمجموعة {group_name}: لم يتم رصد أي مخاطر عاجلة.",
            extracted_action_items=[],
            identified_risks=[],
            generated_at=datetime.now(timezone.utc)
        )

    formatted_msgs = [
        {"sender": m.sender, "message_text": m.message_text, "timestamp": str(m.message_timestamp)}
        for m in messages
    ]

    analysis = await AIService.analyze_chat_transcript(group_name, formatted_msgs)

    summary_record = WhatsAppSummary(
        user_id=current_user.id,
        group_name=group_name,
        executive_summary=analysis.summary,
        extracted_action_items=[item.model_dump() for item in analysis.action_items],
        identified_risks=analysis.blockers_and_risks,
        generated_at=datetime.now(timezone.utc)
    )
    db.add(summary_record)
    await db.commit()
    await db.refresh(summary_record)

    return summary_record

@router.get("/summaries", response_model=List[WhatsAppSummaryResponse])
async def get_whatsapp_summaries(
    group_name: Optional[str] = None,
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WhatsAppSummary).where(WhatsAppSummary.user_id == current_user.id)
    if group_name:
        stmt = stmt.where(WhatsAppSummary.group_name == group_name)
    stmt = stmt.order_by(WhatsAppSummary.generated_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()
