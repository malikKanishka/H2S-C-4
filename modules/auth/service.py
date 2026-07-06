from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from extensions import getDb

def authenticateUser(username, password):
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

def generateToken(user):
    return create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"]}
    )
