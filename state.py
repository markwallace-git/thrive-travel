class ThriveState:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session = {
            "destination": "",      # Changed from None to ""
            "budget": "",           # Changed from None to ""
            "duration": "",         # Changed from None to ""
            "preferences": [],
            "conversation_history": []
        }
        self.persistent_prefs = {}
    
    def update(self, new_data: dict):
        """Merge new intent data into session state"""
        for key, value in new_data.items():
            if key == "preferences":
                # Merge preference lists, avoid duplicates
                if value:
                    existing = self.session.get(key, [])
                    self.session[key] = list(set(existing + value))
            else:
                # Only update if new value is non-empty
                if value and isinstance(value, str) and value.strip():
                    self.session[key] = value.strip()
    
    def is_ready_for_plan(self) -> bool:
        """Check if we have minimum required info"""
        dest = self.session.get("destination", "")
        dur = self.session.get("duration", "")
        return bool(dest and dest.strip() and dur and dur.strip())
    
    def get_session(self) -> dict:
        """Return a clean copy of session data"""
        return {
            "destination": self.session.get("destination", ""),
            "budget": self.session.get("budget", ""),
            "duration": self.session.get("duration", ""),
            "preferences": self.session.get("preferences", [])
        }