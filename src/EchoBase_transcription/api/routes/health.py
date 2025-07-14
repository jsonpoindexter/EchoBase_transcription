from flask import Blueprint, jsonify
from ...api.app import add_base_path, swagger_gen

bp = Blueprint("health", __name__)

@bp.route(add_base_path("/health"), methods=["GET"])
@swagger_gen.response(status_code=200, schema={"status": "ok"})
def health():
    return jsonify({"status": "ok"}), 200