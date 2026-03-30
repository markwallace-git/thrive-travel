from jsonschema import validate, ValidationError

THRIVE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "intent": {"type": "string"},
        "data": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "budget": {"type": "string"},
                "duration": {"type": "string"},
                "preferences": {"type": "array", "items": {"type": "string"}}
            }
        },
        "next_action": {
            "type": "string", 
            "enum": ["ask_question", "call_tool", "generate_plan", "none"]
        }
    },
    "required": ["message", "intent", "data", "next_action"]
}

def validate_response(response: dict) -> bool:
    try:
        validate(instance=response, schema=THRIVE_RESPONSE_SCHEMA)
        return True
    except ValidationError as e:
        print(f"Schema violation: {e.message}")
        return False