from __future__ import annotations

from fastapi import APIRouter
from starlette import status

from ...services.system_service import list_systems, get_or_create_system
from ...db.schemas import SystemRead, SystemCreate

router = APIRouter()


@router.get(
    "/systems",
    status_code=status.HTTP_200_OK,
    response_model=list[SystemRead],
)
async def handle_get_systems() -> list[SystemRead]:
    """Return all systems."""
    return list_systems()


@router.post(
    "/systems",
    status_code=status.HTTP_201_CREATED,
    response_model=SystemRead,
)
async def handle_post_systems(
        name: str,
        description: str | None = None,
) -> SystemRead:
    """
    Create (or return existing) a System by name.

    We go through the service layer so the worker and API stay consistent.
    """
    dto = SystemCreate(name=name, description=description)
    return get_or_create_system(dto)
