from intent_parser import extract_travel_intent
from state import ThriveState
from schema import validate_response

# Tool Import
try:
    from tools import generate_itinerary
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    print("⚠️  WARNING: tools.py not found. Planning features disabled.")

# Database Import
try:
    from database import init_db, save_trip
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️  WARNING: database.py not found. Persistence disabled.")

class ThriveEngine:
    def __init__(self, user_id="default_user"):
        self.state = ThriveState(user_id)
        self.user_id = user_id
        if DB_AVAILABLE:
            init_db()
    
    def process_input(self, user_input: str) -> dict:
        # 1. Parse Intent
        parsed = extract_travel_intent(user_input)
        intent = parsed['intent']
        data = parsed['data']
        
        # 2. Update State
        self.state.update(data)
        
        # 3. Determine Next Action & Message
        next_action = "ask_question"
        message = "Thanks for sharing that. "
        
        # Check if we have enough info to generate a plan
        if self.state.is_ready_for_plan():
            next_action = "generate_plan"
            
            if TOOLS_AVAILABLE:
                try:
                    # Call the Tool
                    plan = generate_itinerary(
                        destination=self.state.session["destination"],
                        duration=self.state.session["duration"],
                        preferences=self.state.session["preferences"],
                        budget=self.state.session["budget"]
                    )
                    
                    # 💾 Save to Database if available
                    trip_id = "N/A"
                    if DB_AVAILABLE:
                        try:
                            trip_id = save_trip(self.user_id, {
                                "destination": self.state.session["destination"],
                                "duration": self.state.session["duration"],
                                "budget": self.state.session["budget"],
                                "preferences": self.state.session["preferences"],
                                "itinerary": plan["itinerary"]
                            })
                        except Exception as db_err:
                            print(f"DB Save Error: {db_err}")
                    
                    # Format Plan into Message (WITH WEATHER DISPLAY)
                    message += f"I have enough info! Here's your draft itinerary (Trip ID: #{trip_id}):\n\n"
                    for day in plan['itinerary'][:3]:
                        message += f"🗓️ Day {day['day']}:\n"
                        # Show weather if available
                        if 'weather' in day and day['weather']:
                            message += f"   🌤️ {day['weather']}\n"
                        # Show activities
                        for activity in day['activities']:
                            message += f"   • {activity}\n"
                        message += "\n"
                    message += "... (full plan available in app)"
                    
                except Exception as e:
                    message += f"I'm ready to plan, but encountered a tool error: {str(e)}"
                    next_action = "ask_question"
            else:
                message += "I have enough info to start building your itinerary (Tool pending)."
        else:
            # Determine what's missing
            if not self.state.session.get("destination"):
                message += "To get started, where are you dreaming of going? "
            elif not self.state.session.get("duration"):
                message += "Got it. How many days are you planning for? "
            elif not self.state.session.get("budget"):
                message += "I've noted that. What's your budget range for this trip? "
            else:
                message += "Is there anything else you'd like to add? "
            
        # 4. Construct Response
        response = {
            "message": message,
            "intent": intent,
            "data": self.state.get_session(),
            "next_action": next_action
        }
        
        # 5. Validate Schema
        if not validate_response(response):
            print("⚠️ WARNING: Response schema validation failed!")
            
        return response

# CLI Loop
if __name__ == "__main__":
    engine = ThriveEngine()
    print("🤖 Thrive Engine Ready. Type 'quit' to exit.")
    
    while True:
        try:
            user_text = input("\nYou: ")
            if user_text.lower() == 'quit':
                print("👋 Closing Thrive Engine...")
                break
            
            response = engine.process_input(user_text)
            print(f"Thrive: {response['message']}")
            print(f"Action: {response['next_action']}")
            
        except KeyboardInterrupt:
            print("\n👋 Closing Thrive Engine...")
            break
        except Exception as e:
            print(f"❌ Critical Error: {e}")