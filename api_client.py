# api_client.py
import requests
import os
import json

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")

# Mock Places Database (fallback for activities)
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

def get_destination_info(destination: str) -> dict:
    """
    Fetch detailed destination information from Wikipedia API
    FREE - No API key required
    """
    try:
        # Wikipedia REST API
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{destination}"
        params = {
            "redirect": "true"
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            "title": data.get('title', destination),
            "description": data.get('description', ''),
            "extract": data.get('extract', ''),
            "thumbnail": data.get('thumbnail', {}).get('source', ''),
            "url": data.get('content_urls', {}).get('desktop', {}).get('page', ''),
            "coordinates": data.get('coordinates', {})
        }
    except Exception as e:
        print(f"Wikipedia API Error: {e}")
        return {
            "title": destination,
            "description": f"Explore {destination}",
            "extract": f"{destination} is a popular travel destination.",
            "thumbnail": "",
            "url": ""
        }

def get_destination_images(query: str, limit: int = 5) -> list:
    """
    Fetch high-quality images from Unsplash API
    FREE - API key required (instant approval, no payment)
    Get key at: https://unsplash.com/developers
    """
    
    if not UNSPLASH_API_KEY:
        print("⚠️  Unsplash API key not configured. Using placeholder images.")
        return []
    
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": limit,
            "orientation": "landscape",
            "client_id": UNSPLASH_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        images = []
        for result in data.get('results', []):
            images.append({
                "url": result['urls']['regular'],
                "thumbnail": result['urls']['thumb'],
                "alt_description": result.get('alt_description', ''),
                "photographer": result['user']['name'],
                "width": result['width'],
                "height": result['height']
            })
        
        return images
    except Exception as e:
        print(f"Unsplash API Error: {e}")
        return []

def get_location_coordinates(place: str) -> dict:
    """
    Fetch coordinates and location data from OpenStreetMap Nominatim
    FREE - No API key required
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place,
            "format": "json",
            "limit": 1
        }
        
        headers = {
            "User-Agent": "ThriveTravelApp/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data:
            return {
                "lat": float(data[0]['lat']),
                "lng": float(data[0]['lon']),
                "display_name": data[0].get('display_name', place),
                "bounding_box": {
                    "north": float(data[0].get('boundingbox', [0, 0, 0, 0])[1]),
                    "south": float(data[0].get('boundingbox', [0, 0, 0, 0])[0]),
                    "east": float(data[0].get('boundingbox', [0, 0, 0, 0])[3]),
                    "west": float(data[0].get('boundingbox', [0, 0, 0, 0])[2])
                }
            }
        
        return {"lat": 0.0, "lng": 0.0, "display_name": place}
    except Exception as e:
        print(f"OpenStreetMap Error: {e}")
        return {"lat": 0.0, "lng": 0.0, "display_name": place}

def search_places(destination: str, query: str, max_results: int = 5) -> list:
    """
    Search for places using mock database + real coordinates from OpenStreetMap
    FREE - No payment required
    """
    
    destination_lower = destination.lower().split()[0]
    
    # Find matching mock data
    mock_data = None
    for key in MOCK_PLACES:
        if key in destination_lower or destination_lower in key:
            mock_data = MOCK_PLACES[key]
            break
    
    if not mock_data:
        # Return generic fallback with real coordinates
        coords = get_location_coordinates(destination)
        return [
            {
                "name": f"Popular {query} in {destination}",
                "rating": 4.0,
                "price_level": 2,
                "lat": coords.get('lat', 0.0),
                "lng": coords.get('lng', 0.0),
                "address": destination,
                "description": f"Top-rated {query} spot in {destination}"
            }
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
    
    # Enhance with Wikipedia descriptions
    enhanced_places = []
    for place in places[:max_results]:
        # Try to get Wikipedia info for the place
        wiki_info = get_destination_info(place['name'])
        
        enhanced_places.append({
            "name": place['name'],
            "address": place.get('address', ''),
            "rating": place.get('rating', 4.0),
            "price_level": place.get('price_level', 2),
            "lat": place.get('lat', 0.0),
            "lng": place.get('lng', 0.0),
            "description": wiki_info.get('extract', '')[:200] if wiki_info.get('extract') else '',
            "image": wiki_info.get('thumbnail', ''),
            "wiki_url": wiki_info.get('url', '')
        })
    
    return enhanced_places

def get_place_details(place_name: str) -> dict:
    """
    Get detailed information about a specific place
    Combines Wikipedia + OpenStreetMap data
    FREE - No payment required
    """
    
    # Get Wikipedia info
    wiki_info = get_destination_info(place_name)
    
    # Get coordinates
    coords = get_location_coordinates(place_name)
    
    # Get images
    images = get_destination_images(place_name, limit=3)
    
    return {
        "name": place_name,
        "description": wiki_info.get('extract', ''),
        "thumbnail": wiki_info.get('thumbnail', ''),
        "coordinates": coords,
        "images": images,
        "wiki_url": wiki_info.get('url', '')
    }

def get_hotels(destination: str) -> list:
    """
    Mock hotel data (can be replaced with real hotel API later)
    FREE - Mock data for now
    """
    
    hotels_db = {
        "paris": [
            {"name": "Hard Rock Hotels Paris", "price": 350, "rating": 4.5, "stars": 5, "lat": 48.8584, "lng": 2.2945},
            {"name": "Grand Palladium Paris", "price": 280, "rating": 4.3, "stars": 4, "lat": 48.8606, "lng": 2.3376}
        ],
        "tokyo": [
            {"name": "Park Hyatt Tokyo", "price": 450, "rating": 4.8, "stars": 5, "lat": 35.6717, "lng": 139.7640},
            {"name": "Shibuya Granbell Hotel", "price": 200, "rating": 4.4, "stars": 4, "lat": 35.6595, "lng": 139.7004}
        ],
        "london": [
            {"name": "The Savoy", "price": 500, "rating": 4.7, "stars": 5, "lat": 51.5103, "lng": -0.1201},
            {"name": "Premier Inn London", "price": 150, "rating": 4.2, "stars": 3, "lat": 51.5194, "lng": -0.1270}
        ],
        "new york": [
            {"name": "The Plaza Hotel", "price": 600, "rating": 4.6, "stars": 5, "lat": 40.7648, "lng": -73.9754},
            {"name": "Pod Hotels Times Square", "price": 180, "rating": 4.1, "stars": 3, "lat": 40.7580, "lng": -73.9855}
        ],
        "bali": [
            {"name": "Four Seasons Resort Bali", "price": 400, "rating": 4.9, "stars": 5, "lat": -8.5069, "lng": 115.2625},
            {"name": "Ubud Village Hotel", "price": 120, "rating": 4.4, "stars": 4, "lat": -8.5069, "lng": 115.2625}
        ]
    }
    
    destination_lower = destination.lower().split()[0]
    
    # Find matching hotels
    for key in hotels_db:
        if key in destination_lower or destination_lower in key:
            return hotels_db[key]
    
    # Default fallback
    return [
        {"name": f"Grand Hotel {destination}", "price": 250, "rating": 4.3, "stars": 4, "lat": 0.0, "lng": 0.0},
        {"name": f"Budget Stay {destination}", "price": 100, "rating": 3.9, "stars": 3, "lat": 0.0, "lng": 0.0}
    ]