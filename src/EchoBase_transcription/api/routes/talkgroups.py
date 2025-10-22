from fastapi import APIRouter
from starlette import status

from src.EchoBase_transcription.db import get_session
from src.EchoBase_transcription.db.models import TalkGroup
from src.EchoBase_transcription.db.schemas import TalkGroupRead

router = APIRouter()


@router.get("/talkgroups", status_code=status.HTTP_200_OK, response_model=list[TalkGroupRead])
async def handle_get_talkgroups():
    """ Return all talkgroups """
    with get_session() as db:
        talkgroups = db.query(TalkGroup).all()
        return talkgroups
