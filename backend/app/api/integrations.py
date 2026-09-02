from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, TenantIntegration
from app.schemas import TenantIntegrationCreate, TenantIntegrationResponse
from app.security import encrypt_credential, generate_api_key
from app.api.auth import get_current_user, get_current_user_optional
from app.services.odoo_service import OdooService

router = APIRouter(prefix="/integrations", tags=["Tenant Integrations"])

@router.get("", response_model=TenantIntegrationResponse)
async def get_integration(current_user: User = Depends(get_current_user_optional), db: AsyncSession = Depends(get_db)):
    stmt = select(TenantIntegration).where(TenantIntegration.user_id == current_user.id)
    res = await db.execute(stmt)
    integration = res.scalars().first()

    if not integration:
        integration = TenantIntegration(
            user_id=current_user.id,
            api_key=generate_api_key(),
            google_sheets_urls=[]
        )
        db.add(integration)
        await db.commit()
        await db.refresh(integration)

    return TenantIntegrationResponse(
        id=integration.id,
        user_id=integration.user_id,
        odoo_url=integration.odoo_url,
        odoo_db=integration.odoo_db,
        odoo_username=integration.odoo_username,
        has_odoo_password=bool(integration.odoo_encrypted_password),
        google_sheets_urls=integration.google_sheets_urls or [],
        api_key=integration.api_key,
        sync_interval_seconds=integration.sync_interval_seconds,
        updated_at=integration.updated_at
    )

@router.post("", response_model=TenantIntegrationResponse)
async def update_integration(
    payload: TenantIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TenantIntegration).where(TenantIntegration.user_id == current_user.id)
    res = await db.execute(stmt)
    integration = res.scalars().first()

    if not integration:
        integration = TenantIntegration(user_id=current_user.id, api_key=generate_api_key())
        db.add(integration)

    if payload.odoo_url is not None:
        integration.odoo_url = payload.odoo_url
    if payload.odoo_db is not None:
        integration.odoo_db = payload.odoo_db
    if payload.odoo_username is not None:
        integration.odoo_username = payload.odoo_username
    if payload.odoo_password:
        integration.odoo_encrypted_password = encrypt_credential(payload.odoo_password)
    if payload.google_sheets_urls is not None:
        integration.google_sheets_urls = payload.google_sheets_urls
    if payload.sync_interval_seconds:
        integration.sync_interval_seconds = payload.sync_interval_seconds

    await db.commit()
    await db.refresh(integration)

    return TenantIntegrationResponse(
        id=integration.id,
        user_id=integration.user_id,
        odoo_url=integration.odoo_url,
        odoo_db=integration.odoo_db,
        odoo_username=integration.odoo_username,
        has_odoo_password=bool(integration.odoo_encrypted_password),
        google_sheets_urls=integration.google_sheets_urls or [],
        api_key=integration.api_key,
        sync_interval_seconds=integration.sync_interval_seconds,
        updated_at=integration.updated_at
    )

@router.post("/regenerate-api-key", response_model=TenantIntegrationResponse)
async def regenerate_api_key(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(TenantIntegration).where(TenantIntegration.user_id == current_user.id)
    res = await db.execute(stmt)
    integration = res.scalars().first()

    if not integration:
        raise HTTPException(status_code=404, detail="Integration profile not found")

    integration.api_key = generate_api_key()
    await db.commit()
    await db.refresh(integration)

    return TenantIntegrationResponse(
        id=integration.id,
        user_id=integration.user_id,
        odoo_url=integration.odoo_url,
        odoo_db=integration.odoo_db,
        odoo_username=integration.odoo_username,
        has_odoo_password=bool(integration.odoo_encrypted_password),
        google_sheets_urls=integration.google_sheets_urls or [],
        api_key=integration.api_key,
        sync_interval_seconds=integration.sync_interval_seconds,
        updated_at=integration.updated_at
    )
