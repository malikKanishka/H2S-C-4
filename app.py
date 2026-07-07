"""
FanPulse — GenAI Stadium Operations Platform

Run the application:
    python app.py

Endpoints prefix:
    /api/* for JSON APIs
    /dashboard for the UI

Tests:
    pytest
"""

from flask import Flask, jsonify, make_response, render_template, request
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from config import Config
from extensions import jwt, limiter, closeDb, setSecurityHeaders, FanPulseError, ValidationFailedError, NotFoundError, GenAIUnavailableError
from flasgger import Swagger

def createApp(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    if testing:
        app.config["TESTING"] = True
        app.config["RATELIMIT_ENABLED"] = False
        limiter.enabled = False

    # Initialize Extensions
    CORS(app, origins=app.config["CORS_ALLOWED_ORIGINS"])
    jwt.init_app(app)
    limiter.init_app(app)

    @app.after_request
    def apply_caching(response):
        return setSecurityHeaders(response)

    # Configure Swagger UI with JWT Support
    app.config['SWAGGER'] = {
        'title': 'FanPulse API Docs',
        'uiversion': 3
    }
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda model: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
            }
        }
    }
    Swagger(app, config=swagger_config)

    # Database teardown
    app.teardown_appcontext(closeDb)

    # Global Error Handler
    @app.errorhandler(Exception)
    def handleException(e):
        if isinstance(e, ValidationFailedError):
            return jsonify({"error": "validation_failed", "message": "One of the fields you sent wasn't in the right format. Please check and try again.", "details": getattr(e, 'details', [])}), 400
        if isinstance(e, NotFoundError):
            return jsonify({"error": "not_found", "message": e.message}), 404
        if isinstance(e, GenAIUnavailableError):
            return jsonify({"error": "ai_unavailable", "message": "Our AI service is temporarily down. Please try again in a few moments."}), 503
        
        # Pass through HTTP exceptions (404, 405, etc.) with their proper status codes
        if isinstance(e, HTTPException):
            return jsonify({"error": e.name, "message": "An error occurred with your request."}), e.code
        
        app.logger.error(f"Internal Error: {e}")
        return jsonify({"error": "internal_error", "message": "We encountered an unexpected issue on our end. Please try again later."}), 500

    @app.route("/favicon.ico", methods=["GET"])
    @limiter.exempt
    def favicon():
        """Return no-content for favicon requests to avoid 404→500 noise."""
        return make_response("", 204)

    @app.route("/", methods=["GET"])
    @limiter.exempt
    def index():
        """Login page — served at the root URL."""
        return render_template("login.html")

    @app.route("/health", methods=["GET"])
    @limiter.exempt
    def health():
        return jsonify({"status": "ok"})

    # Blueprint Registration (to be implemented in subsequent tasks)
    from modules.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from modules.assistant.routes import assistant_bp
    app.register_blueprint(assistant_bp, url_prefix='/api/assistant')

    from modules.crowd.routes import crowd_bp
    app.register_blueprint(crowd_bp, url_prefix='/api/crowd')

    from modules.accessibility.routes import accessibility_bp
    app.register_blueprint(accessibility_bp, url_prefix='/api/accessibility')

    from modules.transport.routes import transport_bp
    app.register_blueprint(transport_bp, url_prefix='/api/transport')

    from modules.sustainability.routes import sustainability_bp
    app.register_blueprint(sustainability_bp, url_prefix='/api/sustainability')

    from modules.dashboard.routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app

if __name__ == "__main__":
    from database import initDb
    # Initialize the DB automatically before running
    initDb(seed=True)
    app = createApp()
    app.run(debug=True, port=5000)
