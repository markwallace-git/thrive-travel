# tools.py
import random
from typing import Dict, List

# Graceful import for API client
try:
    from api_client import get_weather_forecast
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("⚠️  WARNING: api_client.py not found. Weather data disabled.")

def parse_budget(budget_str: str) -> int:
    """Convert budget string to integer"""
    if not budget_str:
        return 5000  # Default mid-range
    try:
        # Remove $ and commas
        clean = budget_str.replace('$', '').replace(',', '')
        return int(clean)
    except:
        return 5000

def generate_itinerary(destination: str, duration: str, preferences: list, budget: str = "") -> dict:
    """Generates a customized itinerary based on preferences and budget."""
    
    # Parse duration & budget
    try:
        days = int(''.join(filter(str.isdigit, duration)) or "3")
    except:
        days = 3
    
    total_budget = parse_budget(budget)
    budget_tier = "luxury" if total_budget > 5000 else "budget" if total_budget < 2000 else "mid"
    
    # Activity Database (with cost estimates)
    activity_db = {
        "luxury": [
            {"name": "Private yacht tour", "cost": "$500"},
            {"name": "Michelin star dining", "cost": "$300"},
            {"name": "VIP museum access", "cost": "$100"},
            {"name": "Spa & wellness day", "cost": "$400"}
        ],
        "budget": [
            {"name": "Free walking tour", "cost": "$0"},
            {"name": "Street food market", "cost": "$20"},
            {"name": "Public park picnic", "cost": "$10"},
            {"name": "Hostel social event", "cost": "$15"}
        ],
        "adventure": [
            {"name": "Hiking excursion", "cost": "$50"},
            {"name": "Scuba diving", "cost": "$150"},
            {"name": "Rock climbing", "cost": "$80"},
            {"name": "Night jungle trek", "cost": "$60"}
        ],
        "food": [
            {"name": "Cooking class", "cost": "$100"},
            {"name": "Food tasting tour", "cost": "$80"},
            {"name": "Wine tasting", "cost": "$60"},
            {"name": "Local bakery visit", "cost": "$20"}
        ],
        "culture": [
            {"name": "Historical landmark tour", "cost": "$40"},
            {"name": "Local museum visit", "cost": "$30"},
            {"name": "Traditional dance show", "cost": "$70"},
            {"name": "Art gallery exploration", "cost": "$25"}
        ]
    }
    
    # Fallback
    default_activities = [{"name": "City center exploration", "cost": "$0"}]
    
    itinerary = []
    used_activities = set()  # Track used activities to avoid repeats
    
    # Select primary activity pool
    primary_pref = preferences[0] if preferences else "culture"
    activity_pool = activity_db.get(primary_pref, default_activities)
    
    # Add budget-specific activities if tier matches
    if budget_tier == "luxury":
        activity_pool += activity_db["luxury"]
    elif budget_tier == "budget":
        activity_pool += activity_db["budget"]
    
    # Fetch Real Weather Data
    weather_data = []
    if API_AVAILABLE:
        weather_data = get_weather_forecast(destination, days)
    
    for day in range(1, days + 1):
        day_activities = []
        
        # Morning (Free/Light)
        day_activities.append({"name": "Breakfast at local café", "cost": "$15"})
        
        # Main Activity 1 (Unique)
        for _ in range(10):  # Try 10 times to find unique
            act = random.choice(activity_pool)
            if act["name"] not in used_activities:
                used_activities.add(act["name"])
                day_activities.append(act)
                break
        else:
            day_activities.append({"name": "Free time exploration", "cost": "$0"})  # Fallback
            
        # Main Activity 2 (Unique)
        for _ in range(10):
            act = random.choice(activity_pool)
            if act["name"] not in used_activities:
                used_activities.add(act["name"])
                day_activities.append(act)
                break
        else:
            day_activities.append({"name": "Leisure walk", "cost": "$0"})
        
        # Get Weather for this day (OpenWeather returns 8 entries per day)
        weather_note = "☁️ Weather data unavailable"
        if weather_data and not weather_data[0].get("error"):
            try:
                # Pick the forecast entry closest to noon for this day
                day_index = (day - 1) * 8
                if day_index < len(weather_data):
                    w = weather_data[day_index]
                    weather_note = f"☁️ {w.get('description', 'N/A')} ({w.get('temp', '?')}°C)"
            except:
                pass
        
        day_plan = {
            "day": day,
            "weather": weather_note,
            "activities": [f"{a['name']} ({a['cost']})" for a in day_activities]
        }
        itinerary.append(day_plan)
    
    return {
        "destination": destination,
        "duration": duration,
        "budget_tier": budget_tier,
        "preferences_used": preferences,
        "itinerary": itinerary,
        "estimated_total": f"${total_budget}"
    }

def search_hotels(destination: str, budget: str) -> list:
    """Mock hotel search"""
    return [
        {"name": "Grand Hotel", "price": "$200/night", "rating": 4.5},
        {"name": "Budget Stay", "price": "$80/night", "rating": 3.8}
    ]