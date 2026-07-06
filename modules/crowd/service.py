from extensions import getDb
from genai_service import generateGroundedReply
import datetime
import time

# Simple in-memory cache for recommendations
_recommendation_cache = {}

def getZones():
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, capacity, currentCount, latitude, longitude FROM zones")
    zones = []
    for row in cursor.fetchall():
        status = "normal"
        density = row["currentCount"] / row["capacity"]
        if density > 0.8:
            status = "critical"
        elif density > 0.5:
            status = "warning"
            
        zones.append({
            "id": row["id"],
            "name": row["name"],
            "capacity": row["capacity"],
            "density": row["currentCount"], 
            "status": status
        })
    return zones

def getRecommendation(zone_id: str):
    now = time.time()
    
    # Check cache (60s TTL)
    if zone_id in _recommendation_cache:
        cached = _recommendation_cache[zone_id]
        if now - cached["timestamp"] < 60:
            return cached["data"]
            
    db = getDb()
    cursor = db.cursor()
    
    # Get all zones info for context
    cursor.execute("SELECT id, name, capacity, currentCount FROM zones")
    zones = cursor.fetchall()
    
    target_zone = next((z for z in zones if z["id"] == zone_id), None)
    if not target_zone:
        return None
        
    facts = []
    for z in zones:
        facts.append(f"Zone {z['name']} ({z['id']}): {z['currentCount']}/{z['capacity']} people.")
        
    system_instruction = """
    You are a crowd management AI. Based on the facts, provide a 1-sentence recommendation 
    to manage the crowd in the specified target zone. For example, 'Divert fans to Zone B'.
    Only use the facts provided. Do not invent zones.
    """
    
    user_prompt = f"FACTS:\n{chr(10).join(facts)}\n\nTARGET ZONE: {target_zone['name']} ({zone_id})"
    
    recommendation = generateGroundedReply(system_instruction, user_prompt, maxOutputTokens=200)
    
    result = {
        "zone_id": zone_id,
        "recommendation": recommendation,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }
    
    _recommendation_cache[zone_id] = {
        "timestamp": now,
        "data": result
    }
    
    return result

def createAlert(zone_id: str, message: str, user_id: int):
    db = getDb()
    cursor = db.cursor()
    now = datetime.datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO alerts (zoneId, message, createdBy, createdAt) VALUES (?, ?, ?, ?)",
        (zone_id, message, user_id, now)
    )
    db.commit()
    return cursor.lastrowid
