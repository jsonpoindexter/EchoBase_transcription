from fastapi import APIRouter
from starlette import status

from src.EchoBase_transcription.db import get_session
from src.EchoBase_transcription.db.models import System
from src.EchoBase_transcription.db.schemas import SystemRead

router = APIRouter()

@router.get("/system", status_code=status.HTTP_202_ACCEPTED, response_model=list[SystemRead])
async def handle_get_system():
    with get_session() as db:
        systems = db.query(System).all()
        return systems



