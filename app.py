# app.py
import os
from flask import Flask, render_template, request, jsonify
from engine import ThriveEngine

app = Flask(__name__)

# Initialize engine (one instance per session)
engine = ThriveEngine(user_id="web_user")

@app.route('/')
def home():
    """Render the chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process through Thrive Engine
        response = engine.process_input(user_message)
        
        return jsonify({
            'success': True,
            'message': response['message'],
            'action': response['next_action'],
            'data': response['data']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trips', methods=['GET'])
def get_trips():
    """Retrieve saved trip history"""
    try:
        from database import get_user_trips
        trips = get_user_trips("web_user")
        return jsonify({'success': True, 'trips': trips})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Thrive Web Server starting on http://localhost:5000")
   if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Thrive Web Server starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)