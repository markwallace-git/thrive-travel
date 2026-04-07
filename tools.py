# tools.py
import random
from typing import Dict, List

# Import the new search_places function
try:
    from api_client import search_places, get_weather_forecast, get_hotels
    API_AVAILABLE = True
except ImportError as e:
    API_AVAILABLE = False
    print(f"⚠️  WARNING: api_client.py import error: {e}")

def parse_budget(budget_str: str) -> int:
    """Convert budget string to integer"""
    if not budget_str:
        return 5000
    try:
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
    
    # Get real places from mock Places API + free APIs
    places_activities = []
    if API_AVAILABLE:
        for pref in preferences:
            places = search_places(destination, pref, max_results=5)
            for place in places:
                price_symbols = "$" * (place.get('price_level', 2) or 2)
                rating = place.get('rating', 'N/A')
                places_activities.append({
                    "name": f"{place['name']} ({price_symbols}, ⭐{rating})",
                    "cost": f"${place.get('price_level', 2) * 30}",
                    "location": place.get('location', {}),
                    "address": place.get('address', ''),
                    "description": place.get('description', ''),
                    "image": place.get('image', '')
                })
    
    # Fallback if no places found
    if not places_activities:
        fallback_activities = [
            {"name": "Explore city center", "cost": "$0", "location": {}, "address": destination, "description": "", "image": ""},
            {"name": "Local market visit", "cost": "$20", "location": {}, "address": destination, "description": "", "image": ""},
            {"name": "Historical landmark tour", "cost": "$40", "location": {}, "address": destination, "description": "", "image": ""}
        ]
        places_activities = fallback_activities
    
    itinerary = []
    used_activities = set()
    
    for day in range(1, days + 1):
        day_activities = []
        
        # Morning (Free/Light)
        day_activities.append({"name": "Breakfast at local café", "cost": "$15", "location": {}, "address": "", "description": "", "image": ""})
        
        # Main Activity 1 (Unique)
        for _ in range(10):
            act = random.choice(places_activities)
            if act.get("name", "") not in used_activities:
                used_activities.add(act["name"])
                day_activities.append(act)
                break
        else:
            day_activities.append({"name": "Free time exploration", "cost": "$0", "location": {}, "address": "", "description": "", "image": ""})
            
        # Main Activity 2 (Unique)
        for _ in range(10):
            act = random.choice(places_activities)
            if act.get("name", "") not in used_activities:
                used_activities.add(act["name"])
                day_activities.append(act)
                break
        else:
            day_activities.append({"name": "Leisure walk", "cost": "$0", "location": {}, "address": "", "description": "", "image": ""})
        
        # Get Weather for this day
        weather_note = "☁️ Weather data unavailable"
        if API_AVAILABLE:
            weather_data = get_weather_forecast(destination, days)
            if weather_data and not weather_data[0].get("error"):
                try:
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
    
    # Get hotel recommendations
    hotels = []
    if API_AVAILABLE:
        hotels = get_hotels(destination)
    
    return {
        "destination": destination,
        "duration": duration,
        "budget_tier": budget_tier,
        "preferences_used": preferences,
        "itinerary": itinerary,
        "estimated_total": f"${total_budget}",
        "hotels": hotels
    }

def search_hotels(destination: str, budget: str) -> list:
    """Search for hotels in destination"""
    if API_AVAILABLE:
        return get_hotels(destination)
    return [
        {"name": "Grand Hotel", "price": "$200/night", "rating": 4.5},
        {"name": "Budget Stay", "price": "$80/night", "rating": 3.8}
    ]