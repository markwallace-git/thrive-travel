import re
from typing import Dict, List

def extract_travel_intent(user_input: str) -> Dict:
    intent = "unknown"
    data = {"destination": "", "budget": "", "duration": "", "preferences": []}
    
    # === INTENT CLASSIFICATION ===
    user_lower = user_input.lower()
    if any(word in user_lower for word in ["hotel", "stay", "accommodation", "where to stay"]):
        intent = "accommodation_search"
    elif any(word in user_lower for word in ["flight", "fly", "airport", "transport"]):
        intent = "transport_search"
    elif any(word in user_lower for word in ["plan", "itinerary", "trip", "visit", "go to"]):
        intent = "trip_planning"
    elif any(word in user_lower for word in ["budget", "cost", "price", "under $"]):
        intent = "budget_query"
    
    # === DESTINATION EXTRACTION ===
    # Pattern 1: "to [Place]" or "in [Place]"
    dest_match = re.search(r'\b(to|in|at|visiting|going to)\s+([A-Z][a-zA-Z\s&\-]+?)(?:\s*(?:for|under|,|$))', user_input)
    if dest_match:
        data["destination"] = dest_match.group(2).strip()
    
    # Pattern 2: Standalone capitalized word that looks like a city (fallback)
    if not data["destination"]:
        # Look for words after common travel verbs
        simple_match = re.search(r'\b(go|visit|travel|fly)\s+to\s+([A-Z][a-zA-Z]+)\b', user_input, re.I)
        if simple_match:
            data["destination"] = simple_match.group(2).strip()
    
    # === BUDGET EXTRACTION ===
    budget_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:budget|per day|total|under)?', user_input, re.I)
    if budget_match:
        data["budget"] = budget_match.group(1)
    
    # === DURATION EXTRACTION ===
    duration_match = re.search(r'(\d+)\s*(day|week|night)s?\b', user_input, re.I)
    if duration_match:
        data["duration"] = f"{duration_match.group(1)} {duration_match.group(2)}s"
    
    # === PREFERENCE EXTRACTION ===
    pref_keywords = ["luxury", "budget", "adventure", "relaxation", "culture", "food", "nature", "city", "beach", "mountain"]
    data["preferences"] = [p for p in pref_keywords if p in user_lower]
    
    return {"intent": intent, "data": data}