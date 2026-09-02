import asyncio
import logging
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import TenantIntegration
from app.services.sync_engine import SyncEngine

logger = logging.getLogger(__name__)

class BackgroundScheduler:
    def __init__(self, interval_seconds: int = 60):
        self.interval_seconds = interval_seconds
        self._is_running = False
        self._task = None

    async def _sync_all_active_tenants(self):
        async with AsyncSessionLocal() as db:
            try:
                stmt = select(TenantIntegration)
                res = await db.execute(stmt)
                integrations = res.scalars().all()

                if not integrations:
                    return

                tasks = [SyncEngine.sync_tenant(db, integ) for integ in integrations]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for idx, r in enumerate(results):
                    if isinstance(r, Exception):
                        logger.error(f"Error syncing tenant integration {integrations[idx].id}: {r}")
                    else:
                        logger.info(f"Successfully synced tenant integration {integrations[idx].id}: {r} records")
            except Exception as e:
                logger.error(f"Error in background scheduler sync loop: {e}")

    async def _run_loop(self):
        while self._is_running:
            logger.info("Executing 60-second periodic tenant synchronization cycle...")
            await self._sync_all_active_tenants()
            await asyncio.sleep(self.interval_seconds)

    def start(self):
        if not self._is_running:
            self._is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Background 60-second polling scheduler started.")

    def stop(self):
        if self._is_running:
            self._is_running = False
            if self._task:
                self._task.cancel()
            logger.info("Background polling scheduler stopped.")

scheduler = BackgroundScheduler(interval_seconds=60)
