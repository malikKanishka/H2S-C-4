import sqlite3
import secrets
from flask import g, jsonify, request, session, make_response
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per minute"])

DB_PATH = os.environ.get("DB_PATH", "fanpulse.db")

class FanPulseError(Exception):
    def __init__(self, message):
        self.message = message

class ValidationFailedError(FanPulseError): pass
class NotFoundError(FanPulseError): pass
class GenAIUnavailableError(FanPulseError): pass

def setSecurityHeaders(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_csrf_token(token):
    return token == session.get('_csrf_token')

def getDb():
    """Get the SQLite database connection for the current request."""
    if 'db' not in g:
        uri = True if "memory:" in DB_PATH else False
        g.db = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES,
            uri=uri
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def closeDb(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def requireRole(*roles):
    """
    Decorator to protect routes by ensuring the user has one of the allowed roles.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify({"error": "forbidden", "message": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
