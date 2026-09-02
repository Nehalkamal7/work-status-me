from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, TenantIntegration
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.security import hash_password, verify_password, create_access_token, decode_access_token, generate_api_key

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    user_id = payload["sub"]
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional), db: AsyncSession = Depends(get_db)) -> User:
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            stmt = select(User).where(User.id == user_id)
            res = await db.execute(stmt)
            user = res.scalars().first()
            if user:
                return user

    # Fallback to default demo user for public dashboard view
    stmt = select(User).where(User.email == "demo@enterprise.com")
    res = await db.execute(stmt)
    demo_user = res.scalars().first()
    if not demo_user:
        demo_user = User(
            email="demo@enterprise.com",
            hashed_password=hash_password("admin123456")
        )
        db.add(demo_user)
        await db.flush()
        integration = TenantIntegration(
            user_id=demo_user.id,
            api_key="ws_live_demo_enterprise_key_2026_x99",
            google_sheets_urls=[]
        )
        db.add(integration)
        await db.commit()
        await db.refresh(demo_user)
    return demo_user

@router.post("/register", response_model=TokenResponse)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password)
    )
    db.add(new_user)
    await db.flush()

    default_integration = TenantIntegration(
        user_id=new_user.id,
        api_key=generate_api_key(),
        google_sheets_urls=[]
    )
    db.add(default_integration)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"sub": new_user.id})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(new_user))

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
