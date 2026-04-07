# app.py
import os
import io
import json
from flask import Flask, render_template, request, jsonify, send_file
from engine import ThriveEngine
from pdf_generator import generate_itinerary_pdf
from database import init_db

app = Flask(__name__)

# Initialize engine
engine = ThriveEngine(user_id="web_user")

# Initialize database on startup
init_db()

@app.route('/')
def home():
    """Render the chat interface"""
    return render_template('index.html')

@app.route('/destination/<destination_name>')
def destination_page(destination_name):
    """Render destination details page"""
    destinations = {
        'Ibiza': {
            'name': 'Ibiza',
            'location': 'Spain',
            'image': 'https://images.unsplash.com/photo-1523497604123-29b5dc695e78?w=800&h=600&fit=crop',
            'description': 'The city is located on the southeast coast of the island, on top of a picturesque hill. It is certainly not a metropolis, and Ibiza has a population of around 50,000. Overlooking the seaport and warm bay, the resort attracts attention with its historic fortresses, old buildings and pretty streets.',
            'gallery': [
                'https://images.unsplash.com/photo-1516966953174-808c2eb7d61d?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1540206395-64ffff982f42?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1506970666340-287a7d286e7f?w=400&h=300&fit=crop'
            ]
        },
        'Dubai': {
            'name': 'Dubai',
            'location': 'UAE',
            'image': 'https://images.unsplash.com/photo-1512453979798-5ea904ac66de?w=800&h=600&fit=crop',
            'description': 'Dubai is a city and emirate in the United Arab Emirates known for luxury shopping, ultramodern architecture and a lively nightlife scene. Burj Khalifa, the 830m-tall tower that dominates the skyline, was inspired by the structure of a desert flower.',
            'gallery': [
                'https://images.unsplash.com/photo-1546412414-e18852351348?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1582672060674-bc2bd808a8b5?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=400&h=300&fit=crop'
            ]
        },
        'Rome': {
            'name': 'Rome',
            'location': 'Italy',
            'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=800&h=600&fit=crop',
            'description': 'Rome, the capital of Italy, is a sprawling cosmopolitan city with nearly 3,000 years of globally influential art, architecture and culture on display. Ancient ruins such as the Colosseum and the Pantheon evoke the power of the former Roman Empire.',
            'gallery': [
                'https://images.unsplash.com/photo-1552423541-1c08a0860b2e?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1515542606-7428e7b144b4?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=400&h=300&fit=crop'
            ]
        },
        'Paris': {
            'name': 'Paris',
            'location': 'France',
            'image': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&h=600&fit=crop',
            'description': 'Paris, France\'s capital, is a major European city and a global center for art, fashion, gastronomy and culture. Its 19th-century cityscape is crisscrossed by wide boulevards and the River Seine. Beyond such landmarks as the Eiffel Tower and the 12th-century, Gothic Notre-Dame cathedral.',
            'gallery': [
                'https://images.unsplash.com/photo-1509299349698-dd22323b5963?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1511739001486-6bfe10ce7859?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1499856871940-a09627c6dc76?w=400&h=300&fit=crop'
            ]
        },
        'Tokyo': {
            'name': 'Tokyo',
            'location': 'Japan',
            'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&h=600&fit=crop',
            'description': 'Tokyo, Japan\'s busy capital, mixes the ultramodern and the traditional, from neon-lit skyscrapers to historic temples. The opulent Meiji Shinto Shrine is known for its towering gate and surrounding woods. The Imperial Palace sits amid large public gardens.',
            'gallery': [
                'https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?w=400&h=300&fit=crop',
                'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=400&h=300&fit=crop'
            ]
        }
    }
    
    destination = destinations.get(destination_name, None)
    if destination:
        return render_template('destination.html', destination=destination)
    else:
        return "Destination not found", 404

@app.route('/trip/<int:trip_id>')
def trip_detail_page(trip_id):
    """Render trip details page"""
    return render_template('trip_detail.html', trip_id=trip_id)

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
        print(f"Chat Error: {str(e)}")
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
        print(f"Trips Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/trip/<int:trip_id>', methods=['GET'])
def get_trip_detail(trip_id):
    """Get trip details by ID"""
    try:
        from database import get_user_trips
        trips = get_user_trips("web_user")
        trip = next((t for t in trips if t['id'] == trip_id), None)
        
        if trip:
            return jsonify({'success': True, 'trip': trip})
        else:
            return jsonify({'success': False, 'error': 'Trip not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        
        # Ensure itinerary is a list
        if isinstance(trip.get('itinerary'), str):
            trip['itinerary'] = json.loads(trip['itinerary'])
        
        # Ensure preferences is a list
        if isinstance(trip.get('preferences'), str):
            trip['preferences'] = json.loads(trip['preferences'])
        
        # Ensure hotels is a list
        if isinstance(trip.get('hotels'), str):
            trip['hotels'] = json.loads(trip['hotels'])
        
        # Generate PDF
        pdf_bytes = generate_itinerary_pdf(trip)
        
        # Return as downloadable file
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"thrive-trip-{trip_id}.pdf"
        )
    
    except Exception as e:
        print(f"PDF Export Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Thrive Web Server starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)