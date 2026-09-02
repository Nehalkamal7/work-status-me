from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, TenantIntegration
from app.services.sync_engine import SyncEngine
from app.api.auth import get_current_user_optional

router = APIRouter(prefix="/sync", tags=["Data Sync"])

@router.post("/now")
async def trigger_manual_sync(current_user: User = Depends(get_current_user_optional), db: AsyncSession = Depends(get_db)):
    stmt = select(TenantIntegration).where(TenantIntegration.user_id == current_user.id)
    res = await db.execute(stmt)
    integration = res.scalars().first()

    if not integration:
        integration = TenantIntegration(user_id=current_user.id, google_sheets_urls=[])
        db.add(integration)
        await db.commit()
        await db.refresh(integration)

    count = await SyncEngine.sync_tenant(db, integration)
    return {
        "status": "success",
        "synced_records_count": count,
        "timestamp": integration.updated_at
    }
