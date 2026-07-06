from extensions import getDb
from genai_service import generateGroundedReply
import time
import logging

logger = logging.getLogger(__name__)

_summary_cache = {}

def getDashboardSummary() -> dict:
    db = getDb()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, name, capacity, currentCount FROM zones")
    zones = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT id, zoneId, message, createdAt FROM alerts ORDER BY id DESC LIMIT 10")
    alerts = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT SUM(points) as total, COUNT(id) as count FROM sustainabilityLogs")
    sus_row = cursor.fetchone()
    sustainability_totals = {"total_points": sus_row["total"] or 0, "total_actions": sus_row["count"] or 0}
    
    # Check cache for insights
    now = time.time()
    insights = []
    
    if "insights" in _summary_cache and now - _summary_cache["insights"]["timestamp"] < 60:
        insights = _summary_cache["insights"]["data"]
    else:
        try:
            facts = []
            for z in zones:
                facts.append(f"Zone {z['name']}: {z['currentCount']}/{z['capacity']} capacity")
            for a in alerts[:3]:
                facts.append(f"Recent alert in {a['zoneId']}: {a['message']}")
                
            system_instruction = """
            You are an operations dashboard AI. Given the facts, provide a 3-bullet "what needs your attention right now" summary.
            Output exactly 3 short bullet points, starting with a dash.
            """
            user_prompt = "FACTS:\n" + "\n".join(facts) if facts else "No zone or alert data available."
            
            reply = generateGroundedReply(system_instruction, user_prompt, maxOutputTokens=250)
            
            # parse bullets
            bullets = [line.strip().lstrip('-').strip() for line in reply.split('\n') if line.strip().startswith('-')]
            if not bullets:
                bullets = ["No immediate issues identified."]
            
            insights = bullets[:3]
            _summary_cache["insights"] = {
                "timestamp": now,
                "data": insights
            }
        except Exception as e:
            # Gemini call failed - log the real error and return a graceful fallback
            logger.error(f"Gemini API call failed in getDashboardSummary: {e}")
            insights = ["AI insights temporarily unavailable. Check server logs for details."]

    return {
        "zones": zones,
        "alerts": alerts,
        "sustainability_totals": sustainability_totals,
        "insights": insights
    }
