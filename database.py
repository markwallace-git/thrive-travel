# database.py
import sqlite3
import json
from datetime import datetime

DB_NAME = "thrive_trips.db"

def init_db():
    """Create trips table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                destination TEXT NOT NULL,
                duration TEXT NOT NULL,
                budget TEXT,
                preferences TEXT,
                itinerary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized.")
    except Exception as e:
        print(f"❌ Database init error: {e}")

def save_trip(user_id: str, trip_data: dict) -> int:
    """Save a trip and return its ID"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trips (user_id, destination, duration, budget, preferences, itinerary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            trip_data.get("destination", ""),
            trip_data.get("duration", ""),
            trip_data.get("budget", ""),
            json.dumps(trip_data.get("preferences", [])),
            json.dumps(trip_data.get("itinerary", []))
        ))
        
        trip_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return trip_id
    except Exception as e:
        print(f"❌ Database save error: {e}")
        return -1

def get_user_trips(user_id: str) -> list:
    """Retrieve all trips for a user"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM trips WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        trips = []
        for row in rows:
            trips.append({
                "id": row[0],
                "user_id": row[1],
                "destination": row[2],
                "duration": row[3],
                "budget": row[4],
                "preferences": json.loads(row[5]),
                "itinerary": json.loads(row[6]),
                "created_at": row[7]
            })
        
        return trips
    except Exception as e:
        print(f"❌ Database fetch error: {e}")
        return []