from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.extensions import mongo
import datetime

# 1. DEFINE the Blueprint FIRST
bp = Blueprint('kit', __name__, url_prefix='/api/kit')

# 2. Now you can use @bp.route
@bp.route('/generate', methods=['POST'])
@login_required
def generate_kit():
    # ... your existing logic ...
    return jsonify({"status": "success"})

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    # ... your existing logic ...
    return jsonify([])