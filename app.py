from flask import Flask, request, jsonify
from flask_cors import CORS
import time, json, os

app = Flask(__name__)
CORS(app)

URLS_FILE = 'urls.json'
SESSIONS = {}

# Load URLs from file
def load_data():
    try:
        with open(URLS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

# Save URLs to file
def save_data(data):
    with open(URLS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Get actual redirect
@app.route('/api/get-redirect/<slug>')
def get_redirect(slug):
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    key = (user_ip, slug)
    start_time = SESSIONS.get(key)
    now = time.time()

    if not start_time or now - start_time < 15:
        return jsonify({'error': 'Wait longer'}), 403

    data = load_data()
    if slug not in data:
        return jsonify({'error': 'Invalid link'}), 404

    return jsonify({'url': data[slug]})

# Track user visit to start the timer
@app.route('/track/<slug>')
def track(slug):
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    SESSIONS[(user_ip, slug)] = time.time()
    return jsonify({'status': 'ok'})

# Add a new URL to the redirection system
@app.route('/api/add-url', methods=['POST'])
def add_url():
    try:
        content = request.get_json(force=True)
        print("Received JSON:", content)  # Log to debug

        slug = content.get('slug')
        url = content.get('url')

        if not slug or not url:
            return jsonify({'error': 'Missing slug or url'}), 400

        data = load_data()

        if slug in data:
            return jsonify({'error': 'Slug already exists'}), 409

        data[slug] = url
        save_data(data)
        return jsonify({'message': 'URL added', 'slug': slug, 'url': url}), 201

    except Exception as e:
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
