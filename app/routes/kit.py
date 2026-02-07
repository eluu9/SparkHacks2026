import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import mongo
from app.services.orchestrator import run_lab_pipeline

bp = Blueprint('kit', __name__, url_prefix='/api/kit')

@bp.route('/generate', methods=['POST'])
@login_required
def handle_request():
    data = request.json
    user_input = data.get('style')
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Run the full agentic pipeline
    final_output = run_lab_pipeline(user_input)
    
    # Save the interaction to the DB if a kit was built
    if final_output.get("type") == "final_kit":
        mongo.db.kits.insert_one({
            "user_id": current_user.id,
            "kit_name": final_output.get("kit_title", "Custom Kit"),
            "created_at": datetime.datetime.utcnow()
        })
        
    return jsonify(final_output)

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    # Only find kits where the user_id matches the logged-in user
    user_kits = mongo.db.kits.find({"user_id": current_user.id}).sort("created_at", -1)
    
    # Map the database results to the format the sidebar expects
    return jsonify([{
        "kit_name": k.get("kit_name", "New Config"),
        "created_at": k.get("created_at")
    } for k in user_kits])