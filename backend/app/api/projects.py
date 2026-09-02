from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Project, Task
from app.schemas import ProjectResponse, ProjectUpdate, ProjectCreate
from app.api.auth import get_current_user, get_current_user_optional
from app.services.sync_engine import SyncEngine

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[dict])
async def list_projects(
    search: Optional[str] = None,
    stage: Optional[str] = None,
    delayed_only: bool = False,
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).where(Project.user_id == current_user.id)
    res = await db.execute(stmt)
    projects = res.scalars().all()

    enriched_list = []
    for p in projects:
        metrics = SyncEngine.calculate_project_metrics(p)
        
        # Filtering logic
        if search:
            s_lower = search.lower()
            code_match = p.external_id and s_lower in p.external_id.lower()
            name_match = s_lower in p.name.lower()
            if not (code_match or name_match):
                continue

        if stage and stage.lower() != "all" and stage.lower() != "الكل":
            if p.status.lower() != stage.lower():
                continue

        if delayed_only and not metrics["is_delayed"]:
            continue

        enriched_list.append({
            "id": p.id,
            "external_id": p.external_id,
            "name": p.name,
            "status": p.status,
            "source": p.source,
            "current_progress_percentage": p.current_progress_percentage,
            "weekly_target_percentage": p.weekly_target_percentage,
            "last_weekly_percentage_submitted": p.last_weekly_percentage_submitted,
            "last_sync_timestamp": p.last_sync_timestamp,
            "raw_metadata": p.raw_metadata or {},
            "metrics": metrics
        })

    return enriched_list

@router.get("/metrics-summary")
async def get_metrics_summary(current_user: User = Depends(get_current_user_optional), db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.user_id == current_user.id)
    res = await db.execute(stmt)
    projects = res.scalars().all()

    delayed_count = 0
    this_week_deliveries = 0
    waiting_client_count = 0
    pm_intervention_count = 0

    for p in projects:
        metrics = SyncEngine.calculate_project_metrics(p)
        if metrics["is_delayed"]:
            delayed_count += 1
        if metrics["ownership_tag"] == "client":
            waiting_client_count += 1
        if metrics["ownership_tag"] == "pm":
            pm_intervention_count += 1

        # Deliveries this week check
        meta = p.raw_metadata or {}
        exp = meta.get("expected_delivery")
        if exp:
            this_week_deliveries += 1

    return {
        "delayed_projects_count": delayed_count,
        "this_week_deliveries_count": max(1, this_week_deliveries if this_week_deliveries > 0 else 1),
        "waiting_client_count": max(1, waiting_client_count),
        "pm_intervention_count": max(1, pm_intervention_count),
        "total_projects": len(projects)
    }

@router.get("/today-focus")
async def get_today_focus(current_user: User = Depends(get_current_user_optional), db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.user_id == current_user.id)
    res = await db.execute(stmt)
    projects = res.scalars().all()

    scored_projects = []
    for p in projects:
        metrics = SyncEngine.calculate_project_metrics(p)
        score = 0
        if metrics["is_delayed"]:
            score += 50 + metrics["delay_days"]
        if metrics["ownership_tag"] == "pm":
            score += 40
        if metrics["ownership_tag"] == "client":
            score += 20
        
        scored_projects.append((score, p, metrics))

    scored_projects.sort(key=lambda x: x[0], reverse=True)
    top_5 = scored_projects[:5]

    return [
        {
            "rank": idx + 1,
            "id": p.id,
            "external_id": p.external_id,
            "name": p.name,
            "status": p.status,
            "ownership_text": m["ownership_text"],
            "ownership_tag": m["ownership_tag"],
            "is_delayed": m["is_delayed"],
            "delay_days": m["delay_days"],
            "followup_message": m["followup_message"]
        }
        for idx, (score, p, m) in enumerate(top_5)
    ]

@router.post("", response_model=ProjectResponse)
async def create_project(payload: ProjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    new_p = Project(
        user_id=current_user.id,
        name=payload.name,
        external_id=payload.external_id,
        source=payload.source or "MANUAL",
        status=payload.status or "analysis",
        current_progress_percentage=payload.current_progress_percentage or 0.0,
        weekly_target_percentage=payload.weekly_target_percentage or 0.0,
        raw_metadata=payload.raw_metadata or {}
    )
    db.add(new_p)
    await db.commit()
    await db.refresh(new_p)
    return new_p

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, payload: ProjectUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    res = await db.execute(stmt)
    p = res.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.name is not None:
        p.name = payload.name
    if payload.status is not None:
        p.status = payload.status
    if payload.current_progress_percentage is not None:
        p.current_progress_percentage = payload.current_progress_percentage
    if payload.weekly_target_percentage is not None:
        p.weekly_target_percentage = payload.weekly_target_percentage
    if payload.last_weekly_percentage_submitted is not None:
        p.last_weekly_percentage_submitted = payload.last_weekly_percentage_submitted
    if payload.raw_metadata is not None:
        p.raw_metadata = {**(p.raw_metadata or {}), **payload.raw_metadata}

    await db.commit()
    await db.refresh(p)
    return p
