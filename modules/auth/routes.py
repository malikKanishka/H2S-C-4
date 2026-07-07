from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from pydantic import BaseModel, ValidationError, Field
from .service import authenticateUser, generateToken
from extensions import limiter
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

class LoginRequest(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)
    model_config = {"extra": "forbid"}

def login_rate_limit_key():
    return f"{request.remote_addr}:{request.json.get('username') if request.is_json else request.form.get('username')}"

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute", key_func=login_rate_limit_key)
def login():
    """
    Login endpoint
    ---
    tags:
      - Auth
    """
    try:
        data = LoginRequest(**request.get_json() or {})
    except ValidationError as e:
        return jsonify({"error": "validation_failed", "message": "One of the fields you sent wasn't in the right format. Please check and try again.", "details": e.errors()}), 400

    user = authenticateUser(data.username, data.password)
    if not user:
        return jsonify({"error": "invalid_credentials", "message": "Invalid username or password. Please try again."}), 401
        
    token = generateToken(user)
    # NOTE: set cookie here so browser-based flows (dashboard) work without a second login
    response = jsonify({"access_token": token, "role": user["role"]})
    response.set_cookie(
        'access_token_cookie', token,
        httponly=True, samesite='Lax',
        secure=False  # NOTE: set secure=True in production behind HTTPS
    )
    return response, 200

@auth_bp.route('/staff/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=login_rate_limit_key)
def staff_login():
    if request.method == 'GET':
        return render_template('staff_login.html')
    
    try:
        data = LoginRequest(username=request.form.get('username'), password=request.form.get('password'))
    except ValidationError as e:
        return render_template('staff_login.html', error="Invalid username or password format.")

    user = authenticateUser(data.username, data.password)
    if not user:
        return render_template('staff_login.html', error="Invalid credentials.")
        
    token = generateToken(user)
    response = make_response(redirect('/dashboard'))
    response.set_cookie('access_token_cookie', token, httponly=True, secure=True, samesite='Lax')
    return response
