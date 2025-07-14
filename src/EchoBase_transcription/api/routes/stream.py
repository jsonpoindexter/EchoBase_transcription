import uuid
from flask import Blueprint
from ...api.sse import create_call_stream_response

bp = Blueprint("stream", __name__)


@bp.route("/transcription/events")
def transcription_events():
    return create_call_stream_response()