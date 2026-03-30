# database.py
import os
import json
from datetime import datetime

# Detect environment and choose database
DATABASE_URL = os.environ.get('DATABASE_URL')

print(f"DATABASE_URL detected: {'YES' if DATABASE_URL else 'NO'}")

if DATABASE_URL:
    # Production: PostgreSQL
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        POSTGRES_AVAILABLE = True
        print("psycopg2 imported successfully")
    except ImportError as e:
        POSTGRES_AVAILABLE = False
        print(f"psycopg2 import failed: {e}")
    
    def get_connection():
        try:
            conn = psycopg2.connect(DATABASE_URL)
            print("PostgreSQL connection successful")
            return conn
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
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
            print("PostgreSQL database initialized.")
        except Exception as e:
            print(f"Database init error: {e}")
    
    def save_trip(user_id: str, trip_data: dict) -> int:
        """Save a trip and return its ID (PostgreSQL)"""
        if not POSTGRES_AVAILABLE:
            print("PostgreSQL not available")
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
            
            print(f"Trip saved successfully with ID: {trip_id}")
            return trip_id
        except Exception as e:
            print(f"Database save error: {e}")
            return -1
    
    def get_user_trips(user_id: str) -> list:
        """Retrieve all trips for a user (PostgreSQL)"""
        if not POSTGRES_AVAILABLE:
            return []
        
        try:
            conn = get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute('SELECT * FROM trips WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            trips = []
            for row in rows:
                trips.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "destination": row["destination"],
                    "duration": row["duration"],
                    "budget": row["budget"],
                    "preferences": row["preferences"] if isinstance(row["preferences"], list) else json.loads(row["preferences"]),
                    "itinerary": row["itinerary"] if isinstance(row["itinerary"], list) else json.loads(row["itinerary"]),
                    "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M') if row["created_at"] else ""
                })
            
            print(f"Retrieved {len(trips)} trips for user {user_id}")
            return trips
        except Exception as e:
            print(f"Database fetch error: {e}")
            return []

else:
    # Development: SQLite
    import sqlite3
    
    DB_NAME = "thrive_trips.db"
    
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
            print("SQLite database initialized.")
        except Exception as e:
            print(f"Database init error: {e}")
    
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
            
            print(f"Trip saved successfully with ID: {trip_id}")
            return trip_id
        except Exception as e:
            print(f"Database save error: {e}")
            return -1
    
    def get_user_trips(user_id: str) -> list:
        """Retrieve all trips for a user (SQLite)"""
        try:
            conn = get_connection()
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
            
            print(f"Retrieved {len(trips)} trips for user {user_id}")
            return trips
        except Exception as e:
            print(f"Database fetch error: {e}")
            return []