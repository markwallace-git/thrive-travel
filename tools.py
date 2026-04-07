# tools.py
import random

try:
    from api_client import search_places, get_weather_forecast, get_hotels
    API_AVAILABLE = True
except:
    API_AVAILABLE = False

def parse_budget(budget_str):
    if not budget_str:
        return 5000
    try:
        clean = budget_str.replace('$', '').replace(',', '')
        return int(clean)
    except:
        return 5000

def generate_itinerary(destination, duration, preferences, budget=""):
    try:
        days = int(''.join(filter(str.isdigit, duration)) or "3")
    except:
        days = 3
    
    total_budget = parse_budget(budget)
    
    activities_list = []
    if API_AVAILABLE:
        for pref in preferences:
            places = search_places(destination, pref, max_results=5)
            for place in places:
                price_symbols = "$" * (place.get('price_level', 2) or 2)
                rating = place.get('rating', 'N/A')
                act = {}
                act["name"] = place['name'] + " (" + price_symbols + ", " + str(rating) + ")"
                act["cost"] = "$" + str(place.get('price_level', 2) * 30)
                act["address"] = place.get('address', '')
                activities_list.append(act)
    
    if not activities_list:
        activities_list = []
        activities_list.append({"name": "Explore city", "cost": "$0", "address": destination})
        activities_list.append({"name": "Local market", "cost": "$20", "address": destination})
        activities_list.append({"name": "Landmark tour", "cost": "$40", "address": destination})
    
    itinerary = []
    used_names = set()
    
    for day in range(1, days + 1):
        day_acts = []
        day_acts.append("Breakfast at local café ($15)")
        
        for i in range(2):
            added = False
            for attempt in range(10):
                act = random.choice(activities_list)
                if act["name"] not in used_names:
                    used_names.add(act["name"])
                    day_acts.append(act['name'] + " (" + act['cost'] + ")")
                    added = True
                    break
            if not added:
                day_acts.append("Free time ($0)")
        
        weather_text = "Weather unavailable"
        if API_AVAILABLE:
            try:
                weather_data = get_weather_forecast(destination, days)
                if weather_data and len(weather_data) > 0:
                    idx = min((day - 1) * 8, len(weather_data) - 1)
                    w = weather_data[idx]
                    if "error" not in w:
                        weather_text = w.get('description', 'N/A') + " (" + str(w.get('temp', '?')) + "°C)"
            except:
                pass
        
        day_plan = {}
        day_plan["day"] = day
        day_plan["weather"] = weather_text
        day_plan["activities"] = day_acts
        itinerary.append(day_plan)
    
    hotels_list = []
    if API_AVAILABLE:
        try:
            hotels_list = get_hotels(destination)
        except:
            pass
    
    result = {}
    result["destination"] = destination
    result["duration"] = duration
    result["budget_tier"] = "mid"
    result["preferences_used"] = preferences
    result["itinerary"] = itinerary
    result["estimated_total"] = "$" + str(total_budget)
    result["hotels"] = hotels_list
    
    return result

def search_hotels(destination, budget=""):
    if API_AVAILABLE:
        try:
            return get_hotels(destination)
        except:
            pass
    return [
        {"name": "Grand Hotel", "price": "$200/night", "rating": 4.5},
        {"name": "Budget Stay", "price": "$80/night", "rating": 3.8}
    ]