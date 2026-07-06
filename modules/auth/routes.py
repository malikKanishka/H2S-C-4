from flask import Blueprint, request, jsonify
from pydantic import BaseModel, ValidationError
from .service import authenticateUser, generateToken

auth_bp = Blueprint('auth', __name__)

class LoginRequest(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: fan_demo
            password:
              type: string
              example: fanpass123
    responses:
      200:
        description: Successful login
        schema:
          type: object
          properties:
            access_token:
              type: string
            role:
              type: string
      400:
        description: Validation failed
      401:
        description: Invalid credentials
    """
    try:
        data = LoginRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "details": e.errors()}), 400

    user = authenticateUser(data.username, data.password)
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401
        
    token = generateToken(user)
    return jsonify({
        "access_token": token,
        "role": user["role"]
    }), 200
