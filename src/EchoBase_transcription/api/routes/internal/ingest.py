from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.exc import SQLAlchemyError
import xml.etree.ElementTree as ET

from ....services.ingest_service import ingest_talkgroup_aliases

router = APIRouter()


@router.post("/internal/ingest", status_code=200)
async def ingest_data(file: UploadFile = File(...)) -> dict:
    """
    Ingest SDRTrunk alias XML and upsert talkgroups for system_id=1.

    Delegates all parsing / DB work to services.ingest_service so the route
    just handles HTTP concerns (request/response + error mapping).
    """
    xml_bytes = await file.read()
    if not xml_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        talkgroups_map, created = ingest_talkgroup_aliases(xml_bytes, system_id=1)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {e}")
    except ValueError as e:
        # e.g. no talkgroups found
        raise HTTPException(status_code=422, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to persist talkgroups")

    return {
        "message": "Data ingested successfully",
        "counts": {"created": created, "updated": 0, "skipped": 0},
        "talkgroups": {str(k): v for k, v in talkgroups_map.items()},
    }
