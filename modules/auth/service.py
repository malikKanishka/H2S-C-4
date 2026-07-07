from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from extensions import getDb
from typing import Optional, Dict, Any

def authenticateUser(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user by username and password.
    
    Args:
        username (str): The user's username.
        password (str): The user's plaintext password.
        
    Returns:
        Optional[Dict[str, Any]]: The user record if authentication succeeds, else None.
    """
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT id, passwordHash, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user["passwordHash"], password):
        return {
            "id": user["id"],
            "role": user["role"]
        }
    return None

def generateToken(user: dict) -> str:
    """
    Generate a JWT token for a given user.
    
    Args:
        user (dict): A dictionary containing user information.
        
    Returns:
        str: A signed JWT access token.
    """
    return create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"]}
    )
