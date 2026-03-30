# api_client.py
import requests
import os

# Load API key from environment variable (best practice)
# Or replace with your key directly for testing: WEATHER_API_KEY = "your_key_here"
WEATHER_API_KEY = "3a4e25f99a2532a72d67567b042beacc"

def get_weather_forecast(city: str, days: int = 3) -> list:
    """Fetch real weather data from OpenWeatherMap"""
    
    if WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        return [{"error": "API Key not configured"}]
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"  # Celsius
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Parse forecast into daily summaries
        forecast = []
        for item in data['list'][:days * 8]:  # 8 entries per day (3-hour steps)
            forecast.append({
                "time": item['dt_txt'],
                "temp": item['main']['temp'],
                "description": item['weather'][0]['description'],
                "icon": item['weather'][0]['icon']
            })
        
        return forecast
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Weather API Error: {e}")
        return [{"error": "Weather data unavailable"}]