import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base
from app.security import hash_password, verify_password, encrypt_credential, decrypt_credential, generate_api_key
from app.services.ai_service import AIService
from app.services.sheets_service import SheetsService

@pytest.mark.asyncio
async def test_security_crypto():
    pwd = "SecretPassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

    plain_cred = "OdooAdminPassword2026"
    encrypted = encrypt_credential(plain_cred)
    decrypted = decrypt_credential(encrypted)
    assert decrypted == plain_cred

    api_key = generate_api_key()
    assert api_key.startswith("ws_live_")

@pytest.mark.asyncio
async def test_google_sheet_regex_parser():
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=123456"
    extracted = SheetsService.extract_sheet_info(url)
    assert extracted is not None
    assert extracted["spreadsheet_id"] == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    assert extracted["gid"] == "123456"

@pytest.mark.asyncio
async def test_ai_rule_based_fallback():
    messages = [
        {"sender": "أحمد المصمم", "message_text": "يرجى مراجعة وتعديل تصاميم التطبيق عاجل"},
        {"sender": "خالد المهندس", "message_text": "هناك مشكلة وتأخير في ربط API الداشبورد"}
    ]
    summary = await AIService.analyze_chat_transcript("تطبيق سيف الفرحان", messages)
    assert summary is not None
    assert len(summary.action_items) > 0
    assert len(summary.blockers_and_risks) > 0

@pytest.mark.asyncio
async def test_root_and_auth_endpoints():
    # Initialize DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    unique_email = f"test_{uuid.uuid4().hex[:6]}@enterprise.com"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register user
        reg_res = await ac.post("/api/v1/auth/register", json={"email": unique_email, "password": "password123"})
        assert reg_res.status_code == 200
        token = reg_res.json()["access_token"]
        assert token is not None

        # Fetch projects list
        headers = {"Authorization": f"Bearer {token}"}
        proj_res = await ac.get("/api/v1/projects", headers=headers)
        assert proj_res.status_code == 200

        # Fetch metrics summary
        metrics_res = await ac.get("/api/v1/projects/metrics-summary", headers=headers)
        assert metrics_res.status_code == 200
        assert "delayed_projects_count" in metrics_res.json()
