from flask import Blueprint, jsonify, render_template, request
from extensions import requireRole
from .service import getDashboardSummary

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../../templates', static_folder='../../static')

@dashboard_bp.route('/api/dashboard/summary', methods=['GET'])
@requireRole('volunteer', 'organizer')
def summary():
    """
    Get dashboard summary metrics and AI insights
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard data
        schema:
          type: object
          properties:
            zones:
              type: array
              items:
                type: object
            alerts:
              type: array
              items:
                type: object
            sustainability_totals:
              type: object
            insights:
              type: array
              items:
                type: string
      401:
        description: Missing or invalid token
      403:
        description: Forbidden
    """
    data = getDashboardSummary()
    return jsonify(data), 200

@dashboard_bp.route('/dashboard', methods=['GET'])
def index():
    token = request.args.get('token')
    if not token:
        return "Unauthorized. Please login and provide ?token=", 401
    
    return render_template('dashboard.html', token=token)
