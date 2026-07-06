from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError
from extensions import requireRole
from .service import recommendTransport

transport_bp = Blueprint('transport', __name__)

class TransportRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    kickoff_iso: str
    model_config = {"extra": "forbid"}

@transport_bp.route('/recommend', methods=['POST'])
@requireRole('fan')
def recommend():
    """
    Get transport recommendation
    ---
    tags:
      - Transport
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            origin_lat:
              type: number
              example: 34.0522
            origin_lng:
              type: number
              example: -118.2437
            kickoff_iso:
              type: string
              example: "2026-06-11T12:00:00Z"
    responses:
      200:
        description: List of options and phrased recommendation summary
        schema:
          type: object
          properties:
            options:
              type: array
              items:
                type: object
                properties:
                  mode:
                    type: string
                  eta_minutes:
                    type: integer
                  congestion:
                    type: string
            summary:
              type: string
      400:
        description: Validation failed
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
    """
    try:
        data = TransportRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "details": e.errors()}), 400
        
    result = recommendTransport(data.origin_lat, data.origin_lng, data.kickoff_iso)
    return jsonify(result), 200
