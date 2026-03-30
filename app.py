# app.py
import os
from flask import Flask, render_template, request, jsonify
from engine import ThriveEngine
from pdf_generator import generate_itinerary_pdf
from flask import send_file

app = Flask(__name__)

# Initialize engine (one instance per session)
engine = ThriveEngine(user_id="web_user")

@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    """Generate and download itinerary as PDF"""
    try:
        from database import get_user_trips
        data = request.get_json()
        trip_id = data.get('trip_id')
        
        if not trip_id:
            return jsonify({'error': 'No trip ID provided'}), 400
        
        # Get trip from database
        trips = get_user_trips("web_user")
        trip = next((t for t in trips if t['id'] == int(trip_id)), None)
        
        if not trip:
            return jsonify({'error': 'Trip not found'}), 404
        
        # Generate PDF
        pdf_bytes = generate_itinerary_pdf(trip)
        
        # Return as downloadable file
        from flask import send_file
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"thrive-trip-{trip_id}.pdf"
            )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Thrive Web Server starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)