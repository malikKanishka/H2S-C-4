import math
from genai_service import generateGroundedReply

def distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def recommendTransport(origin_lat: float, origin_lng: float, kickoff_iso: str) -> dict:
    options = [
        {"mode": "metro", "lat": 34.0520, "lng": -118.2430, "eta_minutes": 15, "congestion": "low"},
        {"mode": "shuttle", "lat": 34.0530, "lng": -118.2440, "eta_minutes": 25, "congestion": "medium"},
        {"mode": "rideshare", "lat": 34.0540, "lng": -118.2450, "eta_minutes": 40, "congestion": "high"}
    ]
    
    for opt in options:
        dist = distance(origin_lat, origin_lng, opt["lat"], opt["lng"])
        penalty = 0
        if opt["congestion"] == "medium": penalty = 10
        if opt["congestion"] == "high": penalty = 20
        opt["score"] = dist * 100 + penalty + opt["eta_minutes"]
        
    options.sort(key=lambda x: x["score"])
    
    final_options = []
    for opt in options:
        final_options.append({
            "mode": opt["mode"],
            "eta_minutes": opt["eta_minutes"],
            "congestion": opt["congestion"]
        })
        
    best_option = final_options[0]
    
    system_instruction = """
    You are a transport guide. Rephrase the provided top recommendation into a friendly, 
    one-sentence natural language tip for the fan.
    """
    
    user_prompt = f"RECOMMENDED MODE: {best_option['mode']}\nETA: {best_option['eta_minutes']} mins\nCONGESTION: {best_option['congestion']}\nKICKOFF: {kickoff_iso}"
    
    summary = generateGroundedReply(system_instruction, user_prompt, maxOutputTokens=150)
    
    return {
        "options": final_options,
        "summary": summary
    }
