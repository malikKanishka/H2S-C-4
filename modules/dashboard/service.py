from extensions import getDb
from genai_service import generateGroundedReply
import time
import logging

logger = logging.getLogger(__name__)

_summary_cache = {}

def getDashboardSummary() -> dict:
    """Returns zones, alerts, and sustainability totals. Fast — no AI call."""
    from modules.crowd.service import getZones
    db = getDb()
    cursor = db.cursor()

    zones = getZones()

    cursor.execute("SELECT id, zoneId, message, createdAt FROM alerts ORDER BY id DESC LIMIT 10")
    alerts = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT SUM(points) as total, COUNT(id) as count FROM sustainabilityLogs")
    sus_row = cursor.fetchone()
    sustainability_totals = {"total_points": sus_row["total"] or 0, "total_actions": sus_row["count"] or 0}
        import threading
        threading.Thread(target=update_insights_cache).start()

    return {
        "zones": zones,
        "alerts": alerts,
        "sustainability_totals": sustainability_totals,
        "insights": insights
    }
