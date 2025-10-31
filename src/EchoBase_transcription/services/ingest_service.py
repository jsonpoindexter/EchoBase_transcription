from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Dict, Tuple

from sqlalchemy import delete

from ..db import get_session
from ..db.models.talkgroup import TalkGroup


def _parse_sdrtrunk_aliases(xml_bytes: bytes) -> Dict[int, str]:
    """
    Parse SDRTrunk-style alias XML and return a mapping of
    {tg_number: alias}. The first alias we see for a tg_number wins.

    Raises ET.ParseError if the XML is invalid.
    """
    root = ET.fromstring(xml_bytes)

    talkgroups: Dict[int, str] = {}

    for alias in root.findall(".//alias"):
        name = alias.get("name")
        if not name:
            continue

        # SDRTrunk represents talkgroups like:
        #   <id type="talkgroup" value="1234" />
        for id_el in alias.findall('./id[@type="talkgroup"]'):
            raw_val = (id_el.get("value") or "").strip()
            if not raw_val.isdigit():
                continue

            tg_num = int(raw_val)
            # first alias for a tg_number wins, don't overwrite
            talkgroups.setdefault(tg_num, name)

    return talkgroups


def ingest_talkgroup_aliases(xml_bytes: bytes, system_id: int = 1) -> Tuple[Dict[int, str], int]:
    """
    High-level ingest pipeline used by the /internal/ingest route.

    Steps:
    - Parse the uploaded XML into {tg_number: alias}.
    - Delete any existing TalkGroup rows for those tg_numbers in that system.
    - Insert fresh rows.

    Returns (talkgroups_map, created_count).

    Raises:
    - ET.ParseError        if XML is invalid
    - SQLAlchemyError      if DB operations fail
    - ValueError           if no talkgroups were found
    """
    talkgroups = _parse_sdrtrunk_aliases(xml_bytes)
    if not talkgroups:
        raise ValueError("No talkgroup IDs found")

    tg_nums = list(talkgroups.keys())

    with get_session() as session:
        # 1. Delete existing rows for these talkgroup numbers in this system
        if tg_nums:
            session.exec(
                delete(TalkGroup).where(
                    TalkGroup.system_id == system_id,
                    TalkGroup.tg_number.in_(tg_nums),
                )
            )

        # 2. Insert new rows
        new_rows = [
            TalkGroup(system_id=system_id, tg_number=tg, alias=name)
            for tg, name in talkgroups.items()
        ]

        session.add_all(new_rows)
        session.flush()

        created_count = len(new_rows)

    return talkgroups, created_count
