from fastapi import APIRouter
from starlette import status

from src.EchoBase_transcription.db import get_session
from src.EchoBase_transcription.db.models import System
from src.EchoBase_transcription.db.schemas import SystemRead, SystemCreate

router = APIRouter()

@router.get("/systems", status_code=status.HTTP_200_OK, response_model=list[SystemRead])
async def handle_get_systems():
    """ Return all systems """
    with get_session() as db:
        systems = db.query(System).all()
        return systems

@router.post("/systems", status_code=status.HTTP_201_CREATED, response_model=SystemRead)
async def handle_post_systems(name: str, description: str | None):
    """ Create new system """
    with get_session() as db:
        system = SystemCreate(
            name=name,
            description=description
        )
        system = System(**system.model_dump())
        db.add(system)
        db.flush()
        return system
