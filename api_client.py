# api_client.py
import requests
import os
import random

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Mock Places Database (Realistic data for popular destinations)
MOCK_PLACES = {
    "paris": {
        "restaurants": [
            {"name": "Le Comptoir du Relais", "rating": 4.5, "price_level": 3, "lat": 48.8534, "lng": 2.3364, "address": "9 Carrefour de l'Odéon, 75006 Paris"},
            {"name": "L'As du Fallafel", "rating": 4.6, "price_level": 1, "lat": 48.8575, "lng": 2.3597, "address": "34 Rue des Rosiers, 75004 Paris"},
            {"name": "Breizh Café", "rating": 4.4, "price_level": 2, "lat": 48.8634, "lng": 2.3628, "address": "109 Rue Vieille du Temple, 75003 Paris"}
        ],
        "museums": [
            {"name": "Louvre Museum", "rating": 4.8, "price_level": 2, "lat": 48.8606, "lng": 2.3376, "address": "Rue de Rivoli, 75001 Paris"},
            {"name": "Musée d'Orsay", "rating": 4.7, "price_level": 2, "lat": 48.8600, "lng": 2.3266, "address": "1 Rue de la Légion d'Honneur, 75007 Paris"},
            {"name": "Centre Pompidou", "rating": 4.5, "price_level": 2, "lat": 48.8606, "lng": 2.3522, "address": "Place Georges-Pompidou, 75004 Paris"}
        ],
        "attractions": [
            {"name": "Eiffel Tower", "rating": 4.6, "price_level": 2, "lat": 48.8584, "lng": 2.2945, "address": "Champ de Mars, 75007 Paris"},
            {"name": "Arc de Triomphe", "rating": 4.7, "price_level": 2, "lat": 48.8738, "lng": 2.2950, "address": "Place Charles de Gaulle, 75008 Paris"},
            {"name": "Sacré-Cœur", "rating": 4.7, "price_level": 1, "lat": 48.8867, "lng": 2.3431, "address": "35 Rue du Chevalier de la Barre, 75018 Paris"}
        ]
    },
    "tokyo": {
        "restaurants": [
            {"name": "Sukiyabashi Jiro", "rating": 4.9, "price_level": 4, "lat": 35.6717, "lng": 139.7640, "address": "Tsukamoto Sogyo Building, Tokyo"},
            {"name": "Ichiran Ramen", "rating": 4.5, "price_level": 1, "lat": 35.6654, "lng": 139.7006, "address": "1-22-7 Jinnan, Shibuya, Tokyo"},
            {"name": "Tsukiji Outer Market", "rating": 4.6, "price_level": 2, "lat": 35.6654, "lng": 139.7707, "address": "4 Chome Tsukiji, Chuo City, Tokyo"}
        ],
        "museums": [
            {"name": "Senso-ji Temple", "rating": 4.7, "price_level": 1, "lat": 35.7148, "lng": 139.7967, "address": "2-3-1 Asakusa, Taito City, Tokyo"},
            {"name": "Meiji Shrine", "rating": 4.8, "price_level": 1, "lat": 35.6764, "lng": 139.6993, "address": "1-1 Yoyogikamizonocho, Shibuya City, Tokyo"}
        ],
        "attractions": [
            {"name": "Shibuya Crossing", "rating": 4.6, "price_level": 1, "lat": 35.6595, "lng": 139.7004, "address": "2-2-1 Dogenzaka, Shibuya City, Tokyo"},
            {"name": "Tokyo Skytree", "rating": 4.5, "price_level": 3, "lat": 35.7101, "lng": 139.8107, "address": "1-1-2 Oshiage, Sumida City, Tokyo"}
        ]
    },
    "london": {
        "restaurants": [
            {"name": "Dishoom", "rating": 4.6, "price_level": 2, "lat": 51.5129, "lng": -0.1252, "address": "12 Upper St Martin's Ln, London WC2H 9FB"},
            {"name": "Sketch", "rating": 4.4, "price_level": 4, "lat": 51.5130, "lng": -0.1416, "address": "9 Conduit St, London W1S 2XG"}
        ],
        "museums": [
            {"name": "British Museum", "rating": 4.7, "price_level": 1, "lat": 51.5194, "lng": -0.1270, "address": "Great Russell St, London WC1B 3DG"},
            {"name": "Tate Modern", "rating": 4.6, "price_level": 1, "lat": 51.5076, "lng": -0.0994, "address": "Bankside, London SE1 9TG"}
        ],
        "attractions": [
            {"name": "Tower of London", "rating": 4.7, "price_level": 3, "lat": 51.5081, "lng": -0.0759, "address": "St Katharine's & Wapping, London EC3N 4AB"},
            {"name": "London Eye", "rating": 4.5, "price_level": 3, "lat": 51.5033, "lng": -0.1196, "address": "Riverside Building, County Hall, London SE1 7PB"}
        ]
    },
    "new york": {
        "restaurants": [
            {"name": "Katz's Delicatessen", "rating": 4.5, "price_level": 2, "lat": 40.7223, "lng": -73.9874, "address": "205 E Houston St, New York, NY 10002"},
            {"name": "Le Bernardin", "rating": 4.7, "price_level": 4, "lat": 40.7614, "lng": -73.9800, "address": "155 W 51st St, New York, NY 10019"}
        ],
        "museums": [
            {"name": "Metropolitan Museum of Art", "rating": 4.8, "price_level": 2, "lat": 40.7794, "lng": -73.9632, "address": "1000 5th Ave, New York, NY 10028"},
            {"name": "MoMA", "rating": 4.6, "price_level": 2, "lat": 40.7614, "lng": -73.9776, "address": "11 W 53rd St, New York, NY 10019"}
        ],
        "attractions": [
            {"name": "Statue of Liberty", "rating": 4.7, "price_level": 2, "lat": 40.6892, "lng": -74.0445, "address": "New York, NY 10004"},
            {"name": "Central Park", "rating": 4.8, "price_level": 1, "lat": 40.7829, "lng": -73.9654, "address": "New York, NY"}
        ]
    },
    "bali": {
        "restaurants": [
            {"name": "Mozaic Restaurant", "rating": 4.7, "price_level": 3, "lat": -8.5069, "lng": 115.2625, "address": "Jl. Raya Sanggingan, Ubud, Bali"},
            {"name": "Warung Babi Guling Ibu Oka", "rating": 4.5, "price_level": 1, "lat": -8.5069, "lng": 115.2625, "address": "Jl. Suweta, Ubud, Bali"}
        ],
        "attractions": [
            {"name": "Tanah Lot Temple", "rating": 4.6, "price_level": 1, "lat": -8.6211, "lng": 115.0868, "address": "Beraban, Kediri, Tabanan Regency, Bali"},
            {"name": "Tegalalang Rice Terrace", "rating": 4.5, "price_level": 1, "lat": -8.4333, "lng": 115.2833, "address": "Jl. Raya Tegallalang, Bali"}
        ]
    }
}

def get_weather_forecast(city: str, days: int = 3) -> list:
    """Fetch real weather data from OpenWeatherMap"""
    
    if not WEATHER_API_KEY or WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return [{"error": "Weather API key not configured"}]
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        forecast = []
        for item in data.get('list', [])[:days * 8]:
            forecast.append({
                "time": item.get('dt_txt', ''),
                "temp": item.get('main', {}).get('temp', 0),
                "description": item.get('weather', [{}])[0].get('description', 'unknown'),
                "icon": item.get('weather', [{}])[0].get('icon', '')
            })
        
        return forecast
    except Exception as e:
        print(f"Weather API Error: {e}")
        return [{"error": "Weather data unavailable"}]

def search_places(destination: str, query: str, max_results: int = 5) -> list:
    """Search for places using Google Places API OR mock data fallback"""
    
    # Try real Google Places API first
    if GOOGLE_PLACES_API_KEY and GOOGLE_PLACES_API_KEY != "YOUR_API_KEY_HERE":
        try:
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": f"{query} in {destination}",
                "key": GOOGLE_PLACES_API_KEY,
                "max_results": max_results
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                places = []
                for result in data.get('results', [])[:max_results]:
                    places.append({
                        "name": result.get('name', 'Unknown'),
                        "address": result.get('formatted_address', ''),
                        "rating": result.get('rating', 'N/A'),
                        "price_level": result.get('price_level', 2),
                        "location": result.get('geometry', {}).get('location', {}),
                        "photo_reference": result.get('photos', [{}])[0].get('photo_reference', '') if result.get('photos') else ''
                    })
                return places
        except Exception as e:
            print(f"Google Places API Error: {e}")
            # Fall through to mock data
    
    # Fallback to mock data
    print("Using mock Places data (Google Places API not configured)")
    destination_lower = destination.lower().split()[0]  # Get first word (e.g., "New York" → "new")
    
    # Find matching mock data
    mock_data = None
    for key in MOCK_PLACES:
        if key in destination_lower or destination_lower in key:
            mock_data = MOCK_PLACES[key]
            break
    
    if not mock_data:
        # Return generic fallback
        return [
            {"name": f"Local {query} in {destination}", "rating": 4.0, "price_level": 2, "lat": 0.0, "lng": 0.0, "address": destination},
            {"name": f"Popular {query} Spot", "rating": 4.2, "price_level": 2, "lat": 0.0, "lng": 0.0, "address": destination}
        ]
    
    # Map query to mock category
    category_map = {
        "restaurant": "restaurants",
        "food": "restaurants",
        "eat": "restaurants",
        "museum": "museums",
        "culture": "museums",
        "art": "museums",
        "attraction": "attractions",
        "sight": "attractions",
        "landmark": "attractions",
        "tour": "attractions"
    }
    
    category = "attractions"  # Default
    for key, value in category_map.items():
        if key in query.lower():
            category = value
            break
    
    places = mock_data.get(category, mock_data.get("attractions", []))
    
    # Return random selection up to max_results
    import random
    selected = random.sample(places, min(max_results, len(places))) if len(places) > max_results else places
    
    return selected

def get_place_details(place_id: str) -> dict:
    """Get detailed info about a specific place"""
    
    if not GOOGLE_PLACES_API_KEY or not place_id:
        return {}
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('result', {})
    except Exception as e:
        print(f"Place Details Error: {e}")
        return {}