from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError
from flask_jwt_extended import get_jwt_identity
from extensions import requireRole
from .service import logSustainabilityAction

sustainability_bp = Blueprint('sustainability', __name__)

class SustainabilityRequest(BaseModel):
    action_type: str
    model_config = {"extra": "forbid"}

@sustainability_bp.route('/log', methods=['POST'])
@requireRole('fan')
def log_action():
    """
    Log a sustainability action and get points and tip
    ---
    tags:
      - Sustainability
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            action_type:
              type: string
              example: "public_transit"
    responses:
      200:
        description: Successful logging
        schema:
          type: object
          properties:
            points_total:
              type: integer
            tip:
              type: string
      400:
        description: Validation failed
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
    """
    try:
        data = SustainabilityRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "details": e.errors()}), 400
        
    user_id = get_jwt_identity()
    result = logSustainabilityAction(int(user_id), data.action_type)
    
    return jsonify(result), 200
