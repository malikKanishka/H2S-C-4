from flask import Blueprint, jsonify, render_template, request, redirect
from extensions import requireRole, generate_csrf_token
from .service import getDashboardSummary
from flask_jwt_extended import decode_token

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../../templates', static_folder='../../static')

@dashboard_bp.route('/api/dashboard/summary', methods=['GET'])
@requireRole('volunteer', 'organizer')
def summary():
    """
    Get dashboard summary metrics and AI insights
    ---
    tags:
      - Dashboard
    """
    data = getDashboardSummary()
    return jsonify(data), 200

@dashboard_bp.route('/dashboard', methods=['GET'])
def index():
    token = request.cookies.get('access_token_cookie')
    if not token:
        return redirect('/api/auth/staff/login')
    
    try:
        # Just ensure it's a valid structure, actual role check happens on API endpoints
        decoded = decode_token(token)
    except Exception:
        return redirect('/api/auth/staff/login')
        
    return render_template('dashboard.html', token=token, csrf_token=generate_csrf_token())
