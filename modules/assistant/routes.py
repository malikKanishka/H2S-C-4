from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError, Field
from typing import Optional
from flask_jwt_extended import get_jwt_identity
from extensions import requireRole, limiter
from .service import askAssistant, logQuery

assistant_bp = Blueprint('assistant', __name__)

class AskRequest(BaseModel):
    question: str = Field(..., max_length=500)
    language: Optional[str] = Field(None, max_length=50)
    model_config = {"extra": "forbid"}

@assistant_bp.route('/ask', methods=['POST'])
@requireRole('fan', 'volunteer', 'organizer')
@limiter.limit("10 per minute")
def ask():
    """
    Assistant endpoint to ask stadium questions
    ---
    tags:
      - Assistant
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
              example: "Where is Gate 1?"
            language:
              type: string
              example: "en"
    responses:
      200:
        description: Successful answer
        schema:
          type: object
          properties:
            answer:
              type: string
            language:
              type: string
            sources:
              type: array
              items:
                type: string
      400:
        description: Validation failed
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
    """
    try:
        data = AskRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "details": e.errors()}), 400
        
    user_id = get_jwt_identity()
    
    logQuery(int(user_id), data.question)
    result = askAssistant(data.question, data.language)
    
    return jsonify(result), 200
