from flask import Blueprint, jsonify
from pony.orm import db_session
from ..models import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/healthz", methods=["GET"])
def healthcheck():
    """Basic health check endpoint including database connectivity."""
    db_ok = False
    try:
        with db_session:
            # Simple connectivity check
            list(db.select("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 500
    payload = {
        "status": "ok" if db_ok else "degraded",
        "checks": {
            "database": "ok" if db_ok else "failed",
        },
    }
    return jsonify(payload), status_code
