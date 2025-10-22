from fastapi import APIRouter, UploadFile, File, HTTPException
import xml.etree.ElementTree as ET
from sqlalchemy.exc import SQLAlchemyError

from src.EchoBase_transcription.db import get_session
from src.EchoBase_transcription.db.models import TalkGroup

router = APIRouter()


@router.post("/internal/ingest", status_code=200)
async def ingest_data(file: UploadFile = File(...)) -> dict:
    """Ingest SDRTrunk XML data and overwrite talkgroups efficiently."""
    xml_bytes = await file.read()
    if not xml_bytes:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {e}")

    # Parse unique talkgroups (first alias wins for a given tg_number)
    talkgroups: dict[int, str] = {}
    for alias in root.findall(".//alias"):
        name = alias.get("name")
        if not name:
            continue
        for id_el in alias.findall('./id[@type="talkgroup"]'):
            raw = (id_el.get("value") or "").strip()
            if raw.isdigit():
                tg_num = int(raw)
                talkgroups.setdefault(tg_num, name)

    if not talkgroups:
        raise HTTPException(status_code=422, detail="No talkgroup IDs found")

    created = 0
    try:
        with get_session() as db:
            tg_nums = list(talkgroups.keys())

            # Overwrite strategy: delete any existing rows for these tg_numbers in one query
            db.query(TalkGroup).filter(
                TalkGroup.system_id == 1,
                TalkGroup.tg_number.in_(tg_nums),
            ).delete(synchronize_session=False)

            # Bulk insert all parsed talkgroups
            objs = [
                TalkGroup(system_id=1, tg_number=tg, alias=name)
                for tg, name in talkgroups.items()
            ]
            db.bulk_save_objects(objs)
            db.commit()
            created = len(objs)
    except SQLAlchemyError as e:
        print(f"Database error during ingest: {e}")
        raise HTTPException(status_code=500, detail="Failed to persist talkgroups")

    return {
        "message": "Data ingested successfully",
        "counts": {"created": created, "updated": 0, "skipped": 0},
        "talkgroups": {str(k): v for k, v in talkgroups.items()},
    }
