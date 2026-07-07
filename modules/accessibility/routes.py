from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError, Field
from extensions import requireRole, limiter
from .service import planAccessibility

accessibility_bp = Blueprint('accessibility', __name__)

class AccessibilityPlanRequest(BaseModel):
    needs: list[str]
    destination_zone: str = Field(..., max_length=50)
    language: str = Field(None, max_length=50)
    model_config = {"extra": "forbid"}

@accessibility_bp.route('/plan', methods=['POST'])
@requireRole('fan', 'volunteer')
@limiter.limit("10 per minute")
def plan():
    """
    Get customized accessibility route plan
    ---
    tags:
      - Accessibility
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            needs:
              type: array
              items:
                type: string
              example: ["wheelchair"]
            destination_zone:
              type: string
              example: "zone-a"
    responses:
      200:
        description: Generated accessibility plan
        schema:
          type: object
          properties:
            plan:
              type: string
            facilities_used:
              type: array
              items:
                type: object
                properties:
                  type:
                    type: string
                  description:
                    type: string
      400:
        description: Validation failed
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
    """
    try:
        data = AccessibilityPlanRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "details": e.errors()}), 400
        
    result = planAccessibility(data.needs, data.destination_zone)
    
    return jsonify(result), 200
