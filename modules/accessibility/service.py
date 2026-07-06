from extensions import getDb
from genai_service import generateGroundedReply

def planAccessibility(needs: list[str], destination_zone: str) -> dict:
    db = getDb()
    cursor = db.cursor()
    
    # Gather facts
    cursor.execute("SELECT id, name FROM zones WHERE id = ?", (destination_zone,))
    dest = cursor.fetchone()
    dest_name = dest["name"] if dest else destination_zone
    
    facts = []
    
    cursor.execute("""
        SELECT g.name, g.isWheelchairAccessible 
        FROM gates g WHERE g.zoneId = ?
    """, (destination_zone,))
    gates = cursor.fetchall()
    
    for g in gates:
        acc = "Yes" if g['isWheelchairAccessible'] else "No"
        facts.append(f"Gate {g['name']} - Wheelchair Accessible: {acc}")
        
    cursor.execute("""
        SELECT facilityType, description 
        FROM facilities WHERE zoneId = ?
    """, (destination_zone,))
    facilities = cursor.fetchall()
    
    facilities_used = []
    for f in facilities:
        facts.append(f"Facility: {f['facilityType']} - {f['description']}")
        facilities_used.append({"type": f["facilityType"], "description": f["description"]})
        
    facts_str = "\n".join(facts)
    needs_str = ", ".join(needs)
    
    system_instruction = """
    You are an accessibility coordinator. Based on the facts provided about the destination zone, 
    create a short, personalized route and facility guide that addresses the user's stated needs.
    Only use the accessibility facts provided. Do not invent facilities or give medical advice.
    """
    
    user_prompt = f"FACTS:\n{facts_str}\n\nDESTINATION: {dest_name}\nUSER NEEDS: {needs_str}"
    
    plan = generateGroundedReply(system_instruction, user_prompt, maxOutputTokens=350)
    
    return {
        "plan": plan,
        "facilities_used": facilities_used
    }
