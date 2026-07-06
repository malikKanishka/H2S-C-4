import sqlite3
from flask import g, jsonify
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per minute"])

DB_PATH = os.environ.get("DB_PATH", "fanpulse.db")

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
