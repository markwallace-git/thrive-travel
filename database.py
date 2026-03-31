# database.py
import os
import json
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL: {'SET' if DATABASE_URL else 'NOT SET'}")

# Global connection cache
_db_conn = None

def _get_conn():
    global _db_conn
    if DATABASE_URL:
        try:
            import psycopg
            if _db_conn is None or _db_conn.closed:
                _db_conn = psycopg.connect(DATABASE_URL)
            return _db_conn, 'postgres'
        except Exception as e:
            print(f"PostgreSQL error: {e}")
            return None, None
    else:
        import sqlite3
        return sqlite3.connect('thrive_trips.db'), 'sqlite'

def init_db():
    conn, db_type = _get_conn()
    if not conn:
        print("Database connection failed")
        return
    try:
        cur = conn.cursor()
        if db_type == 'postgres':
            cur.execute("""
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
            """)
        else:
            cur.execute("""
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
            """)
        conn.commit()
        print("Database initialized")
    except Exception as e:
        print(f"Init error: {e}")
    finally:
        if db_type != 'postgres':
            conn.close()

def save_trip(user_id, trip_data):
    conn, db_type = _get_conn()
    if not conn:
        return -1
    try:
        cur = conn.cursor()
        prefs = json.dumps(trip_data.get("preferences", []))
        itinerary = json.dumps(trip_data.get("itinerary", []))
        if db_type == 'postgres':
            cur.execute(
                "INSERT INTO trips (user_id,destination,duration,budget,preferences,itinerary) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                (user_id, trip_data.get("destination",""), trip_data.get("duration",""), trip_data.get("budget",""), prefs, itinerary)
            )
            trip_id = cur.fetchone()[0]
        else:
            cur.execute(
                "INSERT INTO trips (user_id,destination,duration,budget,preferences,itinerary) VALUES (?,?,?,?,?,?)",
                (user_id, trip_data.get("destination",""), trip_data.get("duration",""), trip_data.get("budget",""), prefs, itinerary)
            )
            trip_id = cur.lastrowid
        conn.commit()
        print(f"Trip saved: {trip_id}")
        return trip_id
    except Exception as e:
        print(f"Save error: {e}")
        return -1
    finally:
        if db_type != 'postgres':
            conn.close()

def get_user_trips(user_id):
    conn, db_type = _get_conn()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        if db_type == 'postgres':
            from psycopg.rows import dict_row
            cur = conn.cursor(row_factory=dict_row)
            cur.execute("SELECT * FROM trips WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
            rows = cur.fetchall()
        else:
            cur.execute("SELECT * FROM trips WHERE user_id=? ORDER BY created_at DESC", (user_id,))
            rows = cur.fetchall()
        trips = []
        for row in rows:
            if db_type == 'postgres':
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
            else:
                trip = {
                    "id": row[0],
                    "user_id": row[1],
                    "destination": row[2],
                    "duration": row[3],
                    "budget": row[4],
                    "preferences": json.loads(row[5]) if row[5] else [],
                    "itinerary": json.loads(row[6]) if row[6] else [],
                    "created_at": row[7]
                }
            trips.append(trip)
        print(f"Retrieved {len(trips)} trips")
        return trips
    except Exception as e:
        print(f"Fetch error: {e}")
        return []
    finally:
        if db_type != 'postgres':
            conn.close()