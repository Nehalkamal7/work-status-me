import logging
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import TenantIntegration, Project, Task
from app.security import decrypt_credential
from app.services.odoo_service import OdooService
from app.services.sheets_service import SheetsService

logger = logging.getLogger(__name__)

class SyncEngine:
    @staticmethod
    def calculate_project_metrics(project: Project) -> dict:
        """Compute delay status, ownership tags, and copyable follow-up messages."""
        metadata = project.raw_metadata or {}
        stage = (project.status or "analysis").lower()
        
        expected_str = metadata.get("expected_delivery")
        actual_str = metadata.get("actual_delivery")
        owner_str = metadata.get("owner", "")

        # Delay computation
        is_delayed = False
        delay_days = 0
        
        # Check explicit delay string or date math
        if metadata.get("delay_days"):
            delay_days = int(metadata["delay_days"])
            is_delayed = delay_days > 0
        elif expected_str and actual_str:
            try:
                exp_dt = datetime.strptime(expected_str[:10], "%Y-%m-%d").date()
                act_dt = datetime.strptime(actual_str[:10], "%Y-%m-%d").date()
                if act_dt > exp_dt:
                    is_delayed = True
                    delay_days = (act_dt - exp_dt).days
            except Exception:
                pass

        # Ownership tag logic
        if "عميل" in owner_str or "client" in owner_str.lower() or stage in ["waiting_client", "بانتظار العميل"]:
            ownership_tag = "client" # بانتظار العميل
            ownership_text = "بانتظار العميل"
        elif "pm" in owner_str.lower() or "تدخل" in owner_str or "مدير" in owner_str:
            ownership_tag = "pm" # مطلوب تدخلي كـ PM
            ownership_text = "مطلوب تدخلي كـ PM"
        else:
            ownership_tag = "team" # مع الفريق التقني/المصمم
            ownership_text = "مع الفريق التقني/المصمم"

        # Ready-to-copy client follow-up message
        code_ref = project.external_id or project.id[:8]
        followup_message = (
            f"السلام عليكم، نود المتابعة بخصوص مشروع «{project.name}» ({code_ref}). "
            f"نرجو التكرم بموافاتنا بالرد أو الاعتماد المطلوب حتى نتمكن من استكمال الخطوة التالية وفق الجدول. شاكرين تعاونكم."
        )

        return {
            "is_delayed": is_delayed,
            "delay_days": delay_days,
            "ownership_tag": ownership_tag,
            "ownership_text": ownership_text,
            "followup_message": followup_message
        }

    @classmethod
    async def sync_tenant(cls, db: AsyncSession, integration: TenantIntegration) -> int:
        """Executes full sync for a given tenant integration."""
        user_id = integration.user_id
        synced_count = 0

        # 1. Fetch from Odoo if configured
        odoo_projects = []
        if integration.odoo_url and integration.odoo_username and integration.odoo_encrypted_password:
            decrypted_pwd = decrypt_credential(integration.odoo_encrypted_password)
            odoo_svc = OdooService(
                url=integration.odoo_url,
                db=integration.odoo_db or "",
                username=integration.odoo_username,
                password=decrypted_pwd
            )
            odoo_projects = await odoo_svc.fetch_projects_and_tasks()

        # 2. Fetch from Google Sheets if configured
        sheets_projects = []
        sheets_svc = SheetsService()
        if integration.google_sheets_urls:
            urls = integration.google_sheets_urls if isinstance(integration.google_sheets_urls, list) else []
            for sheet_url in urls:
                if isinstance(sheet_url, str) and sheet_url.strip():
                    sp = await sheets_svc.fetch_sheet_csv(sheet_url.strip())
                    sheets_projects.extend(sp)

        # 3. Merge & Save to DB
        all_incoming = odoo_projects + sheets_projects
        now = datetime.now(timezone.utc)

        for incoming in all_incoming:
            ext_id = incoming.get("external_id")
            p_name = incoming.get("name")
            if not p_name:
                continue

            # Find existing project by external_id or name
            stmt = select(Project).where(
                Project.user_id == user_id,
                (Project.external_id == ext_id) | (Project.name == p_name)
            )
            res = await db.execute(stmt)
            existing_project = res.scalars().first()

            meta = incoming.get("raw_metadata", {})
            source = incoming.get("source", "MANUAL")
            status = incoming.get("status", "analysis")

            if existing_project:
                existing_project.name = p_name
                existing_project.status = status
                existing_project.source = "COMBINED" if existing_project.source != source else source
                existing_project.last_sync_timestamp = now
                existing_project.raw_metadata = {**(existing_project.raw_metadata or {}), **meta}
                if incoming.get("current_progress_percentage"):
                    existing_project.current_progress_percentage = incoming["current_progress_percentage"]
            else:
                new_project = Project(
                    user_id=user_id,
                    source=source,
                    external_id=ext_id,
                    name=p_name,
                    status=status,
                    current_progress_percentage=incoming.get("current_progress_percentage", 0.0),
                    last_sync_timestamp=now,
                    raw_metadata=meta
                )
                db.add(new_project)

            synced_count += 1

        integration.updated_at = now
        await db.commit()
        return synced_count
