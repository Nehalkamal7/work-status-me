import re
import csv
import io
import logging
import httpx
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SheetsService:
    SPREADSHEET_ID_REGEX = re.compile(r'/spreadsheets/d/([a-zA-Z0-9-_]+)')
    GID_REGEX = re.compile(r'[#&?]gid=([0-9]+)')

    @classmethod
    def extract_sheet_info(cls, url: str) -> Optional[Dict[str, str]]:
        match_id = cls.SPREADSHEET_ID_REGEX.search(url)
        if not match_id:
            return None
        spreadsheet_id = match_id.group(1)
        
        match_gid = cls.GID_REGEX.search(url)
        gid = match_gid.group(1) if match_gid else "0"
        
        return {"spreadsheet_id": spreadsheet_id, "gid": gid}

    @classmethod
    def normalize_header(cls, header: str) -> str:
        h = header.strip().lower()
        h = re.sub(r'[\s_\-\/\\]+', ' ', h)
        return h

    @classmethod
    def fuzzy_match_column(cls, headers: List[str], target_keywords: List[str]) -> Optional[int]:
        normalized_headers = [cls.normalize_header(h) for h in headers]
        for idx, h in enumerate(normalized_headers):
            for kw in target_keywords:
                if kw in h:
                    return idx
        return None

    async def fetch_sheet_csv(self, url: str) -> List[Dict[str, Any]]:
        info = self.extract_sheet_info(url)
        if not info:
            logger.warning(f"Invalid Google Sheet URL: {url}")
            return []

        csv_export_url = f"https://docs.google.com/spreadsheets/d/{info['spreadsheet_id']}/gviz/tq?tqx=out:csv&gid={info['gid']}"

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(csv_export_url)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch Google Sheet CSV (Status {response.status_code}) from {url}")
                    return []
                
                content = response.text
                reader = csv.reader(io.StringIO(content))
                rows = list(reader)
                if not rows or len(rows) < 2:
                    return []

                headers = rows[0]
                
                # Header mapping
                code_col = self.fuzzy_match_column(headers, ['code', 'كود', 'الكود', 'aa'])
                name_col = self.fuzzy_match_column(headers, ['project', 'name', 'المشروع', 'اسم المشروع'])
                stage_col = self.fuzzy_match_column(headers, ['stage', 'status', 'المرحلة', 'مرحلة العمل', 'حالة'])
                owner_col = self.fuzzy_match_column(headers, ['owner', 'responsible', 'المسؤول', 'صاحب الخطوة', 'الجهة'])
                exp_date_col = self.fuzzy_match_column(headers, ['expected', 'due', 'التسليم المتوقع', 'المتوقع'])
                act_date_col = self.fuzzy_match_column(headers, ['actual', 'revised', 'التاريخ الفعلي', 'الفعلي'])
                notes_col = self.fuzzy_match_column(headers, ['note', 'notes', 'timeline', 'الملاحظات', 'التحديث', 'تحديث'])
                progress_col = self.fuzzy_match_column(headers, ['progress', 'نسبة', 'الإنجاز'])

                projects = []
                for idx, row in enumerate(rows[1:]):
                    if not row or not any(cell.strip() for cell in row):
                        continue
                    
                    p_name = row[name_col].strip() if name_col is not None and name_col < len(row) else ""
                    if not p_name:
                        continue

                    p_code = row[code_col].strip() if code_col is not None and code_col < len(row) else f"GS_{idx}"
                    p_stage = row[stage_col].strip() if stage_col is not None and stage_col < len(row) else "Analysis"
                    p_owner = row[owner_col].strip() if owner_col is not None and owner_col < len(row) else ""
                    p_exp = row[exp_date_col].strip() if exp_date_col is not None and exp_date_col < len(row) else ""
                    p_act = row[act_date_col].strip() if act_date_col is not None and act_date_col < len(row) else ""
                    p_notes = row[notes_col].strip() if notes_col is not None and notes_col < len(row) else ""
                    
                    p_progress = 0.0
                    if progress_col is not None and progress_col < len(row):
                        raw_p = re.sub(r'[^\d.]', '', row[progress_col])
                        if raw_p:
                            p_progress = float(raw_p)

                    projects.append({
                        'external_id': p_code,
                        'name': p_name,
                        'source': 'GOOGLE_SHEETS',
                        'status': p_stage,
                        'current_progress_percentage': p_progress,
                        'raw_metadata': {
                            'owner': p_owner,
                            'expected_delivery': p_exp,
                            'actual_delivery': p_act,
                            'latest_notes': p_notes,
                            'sheet_url': url
                        }
                    })

                return projects

        except Exception as e:
            logger.error(f"Error fetching Google Sheet CSV from {url}: {e}")
            return []
