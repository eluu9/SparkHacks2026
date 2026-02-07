"""Kit generation and history API endpoints."""

import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import mongo
from app.services.orchestrator import run_lab_pipeline

bp = Blueprint("kit", __name__, url_prefix="/api/kit")


@bp.route("/generate", methods=["POST"])
@login_required
def handle_request():
    """Run the full kit-building pipeline for the user's query."""
    data = request.get_json(silent=True) or {}
    user_input = data.get("style")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    final_output = run_lab_pipeline(user_input)

    # Persist the kit to the user's history
    if final_output.get("type") == "final_kit":
        mongo.db.kits.insert_one({
            "user_id": current_user.id,
            "kit_name": final_output.get("kit_title", "Custom Kit"),
            "created_at": datetime.datetime.utcnow(),
        })

    return jsonify(final_output)


@bp.route("/history", methods=["GET"])
@login_required
def get_history():
    """Return the current user's saved kits, newest first."""
    user_kits = mongo.db.kits.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1)

    return jsonify([
        {
            "kit_name": kit.get("kit_name", "New Config"),
            "created_at": kit.get("created_at"),
        }
        for kit in user_kits
    ])