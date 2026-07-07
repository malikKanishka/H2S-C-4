from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
from pydantic import BaseModel, ValidationError, Field
from extensions import requireRole, validate_csrf_token
from .service import getZones, getRecommendation, createAlert
from typing import Optional

crowd_bp = Blueprint('crowd', __name__)

@crowd_bp.route('/zones', methods=['GET'])
@requireRole('fan', 'volunteer', 'organizer')
def zones():
    """
    Get current density per zone
    ---
    tags:
      - Crowd
    """
    return jsonify({"zones": getZones()}), 200

@crowd_bp.route('/recommendation/<zone_id>', methods=['GET'])
@requireRole('volunteer', 'organizer')
def recommendation(zone_id):
    """
    Get crowd management recommendation for a zone
    ---
    tags:
      - Crowd
    """
    rec = getRecommendation(zone_id)
    if not rec:
        return jsonify({"error": "not_found", "message": "Zone not found."}), 404
    return jsonify(rec), 200

class AlertRequest(BaseModel):
    zone_id: str = Field(..., max_length=50)
    message: str = Field(..., max_length=280)
    csrf_token: Optional[str] = None
    model_config = {"extra": "forbid"}

@crowd_bp.route('/alert', methods=['POST'])
@requireRole('organizer')
def alert():
    """
    Broadcast a crowd alert
    ---
    tags:
      - Crowd
    """
    try:
        data = AlertRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "message": "One of the fields you sent wasn't in the right format. Please check and try again.", "details": e.errors()}), 400
        
    # Check CSRF token if authenticated via cookie
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        # We assume cookie auth was used because requireRole passed
        if not data.csrf_token or not validate_csrf_token(data.csrf_token):
            return jsonify({"error": "forbidden", "message": "Invalid CSRF token."}), 403

    user_id = get_jwt_identity()
    alert_id = createAlert(data.zone_id, data.message, int(user_id))
    
    return jsonify({
        "alert_id": alert_id,
        "broadcast": True
    }), 200
