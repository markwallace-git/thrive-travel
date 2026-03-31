# database.py
import os
import json
from datetime import datetime

# Detect environment and choose database
DATABASE_URL = os.environ.get('DATABASE_URL')

print(f"=== DATABASE DEBUG ===")
print(f"DATABASE_URL detected: {'YES' if DATABASE_URL else 'NO'}")

if DATABASE_URL:
    # Production: PostgreSQL with psycopg v3
    try:
        import psycopg
        from psycopg.rows import dict_row
        POSTGRES_AVAILABLE = True
        print("psycopg imported: SUCCESS")
    except ImportError as e:
        POSTGRES_AVAILABLE = False
        print(f"psycopg import: FAILED - {e}")
    
    def get_connection():
        try:
            conn = psycopg.connect(DATABASE_URL)
            print("PostgreSQL connection: SUCCESS")
            return conn
        except Exception as e:
            print(f"PostgreSQL connection: FAILED - {e}")
            raise
    
    def init_db():
        """Create trips table if it doesn't exist (PostgreSQL)"""
        if not POSTGRES_AVAILABLE:
            print("PostgreSQL not available, skipping init")
            return
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trips (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    budget TEXT,
                    preferences JSONB,
                    itinerary JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("PostgreSQL table init: SUCCESS")
        except Exception as e:
            print(f"PostgreSQL table init: FAILED - {e}")
    
    def save_trip(user_id: str, trip_data: dict) -> int:
        """Save a trip and return its ID (PostgreSQL)"""
        if not POSTGRES_AVAILABLE:
            print("PostgreSQL not available for save")
            return -1
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trips (user_id, destination, duration, budget, preferences, itinerary)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                user_id,
                trip_data.get("destination", ""),
                trip_data.get("duration", ""),
                trip_data.get("budget", ""),
                json.dumps(trip_data.get("preferences", [])),
                json.dumps(trip_data.get("itinerary", []))
            ))
            
            trip_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            
            print(f"Trip SAVED successfully with ID: {trip_id}")
            return trip_id
        except Exception as e:
            print(f"Trip SAVE failed: {e}")
            return -1
    
    def get_user_trips(user_id: str) -> list:
        """Retrieve all trips for a user (PostgreSQL)"""
        print(f"get_user_trips called for user: {user_id}")
        
        if not POSTGRES_AVAILABLE:
            print("PostgreSQL not available for fetch")
            return []
        
        try:
            conn = get_connection()
            cursor = conn.cursor(row_factory=dict_row)
            
            cursor.execute('SELECT * FROM trips WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            print(f"PostgreSQL query returned {len(rows)} rows")
            
            trips = []
            for row in rows:
                trip = {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "destination": row["destination"],
                    "duration": row["duration"],
                    "budget": row["budget"],
                    "preferences": row["preferences"] if isinstance(row["preferences"], list) else json.loads(row["preferences"]) if row["preferences"] else [],
                    "itinerary": row["itinerary"] if isinstance(row["itinerary"], list) else json.loads(row["itinerary"]) if row["itinerary"] else [],
                    "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M') if row["created_at"] else ""
                }
                trips.append(trip)
            
            print(f"get_user_trips returning {len(trips)} trips")
            return trips
        except Exception as e:
            print(f"get_user_trips FAILED: {e}")
            import traceback
            traceback.print_exc()
            return []

else:
    # Development: SQLite
    import sqlite3
    
    DB_NAME = "thrive_trips.db"
    print(f"Using SQLite database: {DB_NAME}")
    
    def get_connection():
        return sqlite3.connect(DB_NAME)
    
    def init_db():
        """Create trips table if it doesn't exist (SQLite)"""
        try:
            conn = get_connection()
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
            print("SQLite table init: SUCCESS")
        except Exception as e:
            print(f"SQLite table init: FAILED - {e}")
    
    def save_trip(user_id: str, trip_data: dict) -> int:
        """Save a trip and return its ID (SQLite)"""
        try:
            conn = get_connection()
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
            
            print(f"Trip SAVED successfully with ID: {trip_id}")
            return trip_id
        except Exception as e:
            print(f"Trip SAVE failed: {e}")
            return -1
    
    def get_user_trips(user_id: str) -> list:
        """Retrieve all trips for a user (SQLite)"""
        print(f"get_user_trips called for user: {user_id}")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trips WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            print(f"SQLite query returned {len(rows)} rows")
            
            trips = []
            for row in rows:
                trips.append({
                    "id": row[0],
                    "user_id": row[1],
                    "destination": row[2],
                    "duration": row[3],
                    "budget": row[4],
                    "preferences": json.loads(row[5]) if row[5] else [],
                    "itinerary": json.loads(row[6]) if row[6] else [],
                    "created_at": row[7]
                })
            
            print(f"get_user_trips returning {len(trips)} trips")
            return trips
        except Exception as e:
            print(f"get_user_trips FAILED: {e}")
            return []