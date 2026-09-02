import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select
from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.models import User, TenantIntegration, Project
from app.security import hash_password, generate_api_key
from app.services.scheduler import scheduler
from app.api import auth, integrations, projects, whatsapp, sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_initial_demo_data():
    """Seeds realistic default projects matching the reference executive status board."""
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == "demo@enterprise.com")
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user:
            user = User(
                email="demo@enterprise.com",
                hashed_password=hash_password("admin123456")
            )
            db.add(user)
            await db.flush()

            integration = TenantIntegration(
                user_id=user.id,
                api_key="ws_live_demo_enterprise_key_2026_x99",
                google_sheets_urls=[
                    "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"
                ]
            )
            db.add(integration)

            # Sample realistic dataset from reference dashboard
            seed_projects = [
                {
                    "external_id": "S01145 · AA2110",
                    "name": "تطبيق سيف الفرحان",
                    "status": "analysis",
                    "source": "ODOO + Google Sheets",
                    "raw_metadata": {
                        "owner": "مطلوب تدخلي كـ PM",
                        "stale_days": 13,
                        "latest_notes": "20 أغسطس · 11:58ص: تم إرسال ملف التحليل بعد التعديلات، والعمل متوقف حاليًا على مراجعة العميل وردّه."
                    }
                },
                {
                    "external_id": "AA60843",
                    "name": "تطبيق محمد أبو ثنين ومحمد الربيعان",
                    "status": "design",
                    "source": "Google Sheets",
                    "raw_metadata": {
                        "owner": "مع الفريق التقني/المصمم",
                        "expected_delivery": "2026-11-27",
                        "actual_delivery": "2026-12-31",
                        "delay_days": 34,
                        "latest_notes": "اجتماع متابعة بخصوص التصميم"
                    }
                },
                {
                    "external_id": "S02665 · AA67663",
                    "name": "يور كاشير — مريم الجهني",
                    "status": "design",
                    "source": "ODOO + Google Sheets",
                    "raw_metadata": {
                        "owner": "مع الفريق التقني/المصمم",
                        "stale_days": 13,
                        "latest_notes": "20 أغسطس · 12:09م: تم توثيق محضر الاجتماع الأخير."
                    }
                },
                {
                    "external_id": "AA60523",
                    "name": "فرج آل مطلق",
                    "status": "design",
                    "source": "Google Sheets",
                    "raw_metadata": {
                        "owner": "بانتظار العميل",
                        "latest_notes": "تم إرسال التصميم وفي انتظار رد العميل"
                    }
                },
                {
                    "external_id": "S02338 · AA60265",
                    "name": "شركة أودال — تفاعلي",
                    "status": "programming",
                    "source": "ODOO + Google Sheets",
                    "raw_metadata": {
                        "owner": "بانتظار العميل",
                        "stale_days": 13,
                        "expected_delivery": "2026-10-29",
                        "actual_delivery": "2026-11-26",
                        "delay_days": 28,
                        "latest_notes": "20 أغسطس · 10:36ص: تم اعتماد التصميم وبدأت مرحلة البرمجة بمدة تقديرية 70 يوم عمل."
                    }
                },
                {
                    "external_id": "AA63801",
                    "name": "تطبيق Wash Up",
                    "status": "programming",
                    "source": "Google Sheets",
                    "raw_metadata": {
                        "owner": "مع الفريق التقني/المصمم",
                        "expected_delivery": "2026-09-03",
                        "actual_delivery": "2026-10-05",
                        "delay_days": 32,
                        "latest_notes": "التواصل والمتابعة على البريد"
                    }
                },
                {
                    "external_id": "S02288 · AA57068",
                    "name": "ReValue — تطبيق",
                    "status": "programming",
                    "source": "ODOO + Google Sheets",
                    "raw_metadata": {
                        "owner": "مع الفريق التقني/المصمم",
                        "stale_days": 15,
                        "expected_delivery": "2026-09-27",
                        "actual_delivery": "2026-11-02",
                        "delay_days": 36,
                        "latest_notes": "18 أغسطس · 3:09م: تم إعداد بريد العمل وبيئة الاستضافة وإبلاغ الفريق."
                    }
                },
                {
                    "external_id": "2107",
                    "name": "تطبيق - نقلي",
                    "status": "programming",
                    "source": "Google Sheets",
                    "raw_metadata": {
                        "owner": "مع الفريق التقني/المصمم",
                        "expected_delivery": "2026-09-23",
                        "actual_delivery": "2026-12-20",
                        "delay_days": 88,
                        "latest_notes": "المشروع مستقر ولا توجد ملاحظة عاجلة مسجلة في الشيت."
                    }
                },
                {
                    "external_id": "AA58377",
                    "name": "تطبيق أنعام مكة",
                    "status": "programming",
                    "source": "Google Sheets",
                    "raw_metadata": {
                        "owner": "بانتظار العميل",
                        "expected_delivery": "2026-08-30",
                        "actual_delivery": "2026-09-17",
                        "delay_days": 18,
                        "latest_notes": "تم اعتماد التصميم وبدء البرمجة"
                    }
                }
            ]

            for sp in seed_projects:
                p = Project(
                    user_id=user.id,
                    external_id=sp["external_id"],
                    name=sp["name"],
                    status=sp["status"],
                    source=sp["source"],
                    raw_metadata=sp["raw_metadata"]
                )
                db.add(p)

            await db.commit()
            logger.info("Database initialized with seed demo dataset.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await seed_initial_demo_data()
    scheduler.start()
    yield
    scheduler.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(whatsapp.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")

# Static frontend dist mounting
dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return None
        index_file = os.path.join(dist_path, "index.html")
        return FileResponse(index_file)
else:
    @app.get("/")
    async def root():
        return {
            "status": "online",
            "service": settings.APP_NAME,
            "docs": "/docs"
        }
