from __future__ import annotations

from fastapi import APIRouter, Query
from starlette import status

from ...services.talkgroup_service import list_talkgroups_for_system
from ...db.schemas import TalkGroupRead

router = APIRouter()


@router.get(
    "/talkgroups",
    status_code=status.HTTP_200_OK,
    response_model=list[TalkGroupRead],
)
async def handle_get_talkgroups(
        system_id: int = Query(
            1,
            description="System ID whose talkgroups to return (defaults to 1)",
        ),
) -> list[TalkGroupRead]:
    """
    Return all talkgroups for the requested system.

    We delegate to talkgroup_service so API and worker share the same logic.
    """
    return list_talkgroups_for_system(system_id)
