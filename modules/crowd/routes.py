from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from pydantic import BaseModel, ValidationError
from extensions import requireRole
from .service import getZones, getRecommendation, createAlert

crowd_bp = Blueprint('crowd', __name__)

@crowd_bp.route('/zones', methods=['GET'])
@requireRole('fan', 'volunteer', 'organizer')
def zones():
    """
    Get current density per zone
    ---
    tags:
      - Crowd
    security:
      - Bearer: []
    responses:
      200:
        description: List of zones and densities
        schema:
          type: object
          properties:
            zones:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  capacity:
                    type: integer
                  density:
                    type: integer
                  status:
                    type: string
      401:
        description: Missing or invalid token
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
    security:
      - Bearer: []
    parameters:
      - name: zone_id
        in: path
        type: string
        required: true
        example: zone-a
    responses:
      200:
        description: Generated recommendation
        schema:
          type: object
          properties:
            zone_id:
              type: string
            recommendation:
              type: string
            generated_at:
              type: string
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
      404:
        description: Zone not found
    """
    rec = getRecommendation(zone_id)
    if not rec:
        return jsonify({"error": "not_found"}), 404
    return jsonify(rec), 200

class AlertRequest(BaseModel):
    zone_id: str
    message: str
    model_config = {"extra": "forbid"}

@crowd_bp.route('/alert', methods=['POST'])
@requireRole('organizer')
def alert():
    """
    Broadcast a crowd alert
    ---
    tags:
      - Crowd
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            zone_id:
              type: string
              example: zone-a
            message:
              type: string
              example: "Reroute Gate 3 crowd to Gate 5 immediately"
    responses:
      200:
        description: Alert created
        schema:
          type: object
          properties:
            alert_id:
              type: integer
            broadcast:
              type: boolean
      400:
        description: Validation failed
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
    """
    try:
        data = AlertRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "details": e.errors()}), 400
        
    user_id = get_jwt_identity()
    alert_id = createAlert(data.zone_id, data.message, int(user_id))
    
    return jsonify({
        "alert_id": alert_id,
        "broadcast": True
    }), 200
