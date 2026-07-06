from extensions import getDb
from genai_service import generateGroundedReply
import datetime

ACTION_POINTS = {
    "refill_station": 10,
    "public_transit": 20,
    "recycling": 5
}

def logSustainabilityAction(user_id: int, action_type: str) -> dict:
    points = ACTION_POINTS.get(action_type, 0)
    
    db = getDb()
    cursor = db.cursor()
    now = datetime.datetime.utcnow().isoformat()
    
    cursor.execute(
        "INSERT INTO sustainabilityLogs (userId, actionType, points, createdAt) VALUES (?, ?, ?, ?)",
        (user_id, action_type, points, now)
    )
    
    cursor.execute("SELECT SUM(points) as total FROM sustainabilityLogs WHERE userId = ?", (user_id,))
    total_points = cursor.fetchone()["total"]
    
    db.commit()
    
    system_instruction = """
    You are a sustainability coach. Generate a short, encouraging 1-sentence tip personalized 
    to the user's recent sustainability action.
    """
    
    user_prompt = f"RECENT ACTION: {action_type}\nTOTAL POINTS: {total_points}"
    
    tip = generateGroundedReply(system_instruction, user_prompt, maxOutputTokens=100)
    
    return {
        "points_total": total_points,
        "tip": tip
    }
