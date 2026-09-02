import asyncio
import xmlrpc.client
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class OdooService:
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url.rstrip('/') if url else ""
        self.db = db
        self.username = username
        self.password = password

    def _sync_authenticate_and_fetch(self) -> List[Dict[str, Any]]:
        """Synchronous XML-RPC connection logic to run inside an executor."""
        if not self.url or not self.db or not self.username or not self.password:
            return []

        common_url = f"{self.url}/xmlrpc/2/common"
        object_url = f"{self.url}/xmlrpc/2/object"

        try:
            common = xmlrpc.client.ServerProxy(common_url)
            uid = common.authenticate(self.db, self.username, self.password, {})
            if not uid:
                logger.warning(f"Odoo authentication failed for db={self.db}, user={self.username}")
                return []

            models = xmlrpc.client.ServerProxy(object_url)

            # Fetch projects
            project_fields = ['id', 'name', 'stage_id', 'task_ids', 'write_date']
            projects_data = models.execute_kw(
                self.db, uid, self.password,
                'project.project', 'search_read',
                [[]], {'fields': project_fields}
            )

            # Fetch tasks
            task_fields = ['id', 'name', 'stage_id', 'user_ids', 'date_deadline', 'progress', 'project_id']
            tasks_data = models.execute_kw(
                self.db, uid, self.password,
                'project.task', 'search_read',
                [[]], {'fields': task_fields}
            )

            # Map tasks by project
            tasks_by_project = {}
            for t in tasks_data:
                proj_ref = t.get('project_id')
                if proj_ref:
                    p_id = proj_ref[0]
                    tasks_by_project.setdefault(p_id, []).append({
                        'id': str(t.get('id')),
                        'title': t.get('name'),
                        'stage': t.get('stage_id')[1] if isinstance(t.get('stage_id'), (list, tuple)) else str(t.get('stage_id') or ''),
                        'deadline': t.get('date_deadline'),
                        'progress': float(t.get('progress') or 0.0)
                    })

            results = []
            for p in projects_data:
                p_id = p.get('id')
                stage_val = p.get('stage_id')
                stage_name = stage_val[1] if isinstance(stage_val, (list, tuple)) else str(stage_val or 'Analysis')
                
                results.append({
                    'external_id': f"ODOO_{p_id}",
                    'name': p.get('name', 'Untitled Project'),
                    'source': 'ODOO',
                    'status': stage_name,
                    'last_sync_timestamp': p.get('write_date'),
                    'tasks': tasks_by_project.get(p_id, []),
                    'raw_metadata': {
                        'odoo_id': p_id,
                        'write_date': p.get('write_date')
                    }
                })

            return results

        except Exception as e:
            logger.error(f"Error fetching data from Odoo at {self.url}: {e}")
            return []

    async def fetch_projects_and_tasks(self) -> List[Dict[str, Any]]:
        """Asynchronously call the XML-RPC sync function via asyncio loop executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._sync_authenticate_and_fetch)
