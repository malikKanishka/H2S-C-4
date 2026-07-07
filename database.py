import sqlite3
import os
import json
from werkzeug.security import generate_password_hash

DB_PATH = os.environ.get("DB_PATH", "fanpulse.db")

def get_connection(db_path=DB_PATH):
    uri = True if "memory:" in db_path else False
    return sqlite3.connect(db_path, uri=uri)

def initDb(seed: bool = False, dbPath: str = None):
    """Initialize the database schema and optionally seed it with data."""
    path = dbPath or DB_PATH
    conn = get_connection(path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        passwordHash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('fan','volunteer','organizer')),
        preferredLanguage TEXT DEFAULT 'en'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zones (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        currentCount INTEGER NOT NULL DEFAULT 0,
        latitude REAL, longitude REAL,
        kickoffIso TEXT DEFAULT '2026-06-11T12:00:00Z'
    );
    """)
    
    # Try adding columns if they don't exist
    try: cursor.execute("ALTER TABLE zones ADD COLUMN kickoffIso TEXT DEFAULT '2026-06-11T12:00:00Z'")
    except sqlite3.OperationalError: pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gates (
        id TEXT PRIMARY KEY,
        zoneId TEXT NOT NULL REFERENCES zones(id),
        name TEXT NOT NULL,
        isWheelchairAccessible INTEGER NOT NULL DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zoneId TEXT NOT NULL REFERENCES zones(id),
        facilityType TEXT NOT NULL,
        description TEXT,
        isFullyAccessible BOOLEAN DEFAULT 1,
        distanceMetersFromNearestGate INTEGER DEFAULT 50,
        hasTactileGuidance BOOLEAN DEFAULT 0
    );
    """)
    
    try: cursor.execute("ALTER TABLE facilities ADD COLUMN isFullyAccessible BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE facilities ADD COLUMN distanceMetersFromNearestGate INTEGER DEFAULT 50")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE facilities ADD COLUMN hasTactileGuidance BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError: pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zoneId TEXT NOT NULL REFERENCES zones(id),
        message TEXT NOT NULL,
        createdBy INTEGER NOT NULL REFERENCES users(id),
        createdAt TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sustainabilityLogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER NOT NULL REFERENCES users(id),
        actionType TEXT NOT NULL,
        points INTEGER NOT NULL,
        createdAt TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assistantQueries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER NOT NULL REFERENCES users(id),
        question TEXT NOT NULL,
        topic TEXT,
        createdAt TEXT NOT NULL
    );
    """)

    conn.commit()

    if seed:
        seedData(conn)
        
    conn.close()

def seedData(conn: sqlite3.Connection):
    """Seed the database with mock data and test users."""
    cursor = conn.cursor()
    
    # 1. Seed test users
    users = [
        (os.environ.get("DEMO_FAN_USER", "fan_demo"), os.environ.get("DEMO_FAN_PASS", "fanpass123"), "fan"),
        (os.environ.get("DEMO_VOLUNTEER_USER", "volunteer_demo"), os.environ.get("DEMO_VOLUNTEER_PASS", "volpass123"), "volunteer"),
        (os.environ.get("DEMO_ORGANIZER_USER", "organizer_demo"), os.environ.get("DEMO_ORGANIZER_PASS", "orgpass123"), "organizer")
    ]
    
    for username, pwd, role in users:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, passwordHash, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(pwd, method="pbkdf2:sha256"), role)
            )

    # 2. Seed mock data files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mock_dir = os.path.join(base_dir, "mock_data")
    
    # Zones
    zones_path = os.path.join(mock_dir, "zones.json")
    if os.path.exists(zones_path):
        with open(zones_path, 'r', encoding='utf-8') as f:
            zones = json.load(f)
            for z in zones:
                cursor.execute("SELECT id FROM zones WHERE id = ?", (z["id"],))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO zones (id, name, capacity, currentCount, latitude, longitude, kickoffIso) VALUES (?, ?, ?, ?, ?, ?, '2026-06-11T12:00:00Z')",
                        (z["id"], z["name"], z["capacity"], z.get("currentCount", 0), z.get("latitude"), z.get("longitude"))
                    )

    # Gates
    gates_path = os.path.join(mock_dir, "gates.json")
    if os.path.exists(gates_path):
        with open(gates_path, 'r', encoding='utf-8') as f:
            gates = json.load(f)
            for g in gates:
                cursor.execute("SELECT id FROM gates WHERE id = ?", (g["id"],))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO gates (id, zoneId, name, isWheelchairAccessible) VALUES (?, ?, ?, ?)",
                        (g["id"], g["zoneId"], g["name"], 1 if g.get("isWheelchairAccessible") else 0)
                    )

    # Facilities
    facilities_path = os.path.join(mock_dir, "facilities.json")
    if os.path.exists(facilities_path):
        with open(facilities_path, 'r', encoding='utf-8') as f:
            facilities = json.load(f)
            for fac in facilities:
                cursor.execute(
                    "INSERT INTO facilities (zoneId, facilityType, description, isFullyAccessible, distanceMetersFromNearestGate, hasTactileGuidance) VALUES (?, ?, ?, 1, 50, 0)",
                    (fac["zoneId"], fac["facilityType"], fac.get("description", ""))
                )

    conn.commit()

if __name__ == "__main__":
    initDb(seed=True)
    print("Database initialized and seeded.")
