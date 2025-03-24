from flask import Flask, request, jsonify
import re
from pipeline import detect_fraud
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def extract_app_id(play_store_url):
    """Extracts app ID from a given Google Play Store URL."""
    match = re.search(r"id=([a-zA-Z0-9._-]+)", play_store_url)
    return match.group(1) if match else None

@app.route("/detect_fraud", methods=["POST"])
def detect_fraud_api():
    """API endpoint to check for fraudulent apps."""
    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    play_store_url = data["url"]
    app_id = extract_app_id(play_store_url)

    if not app_id:
        return jsonify({"error": "Invalid Google Play Store URL"}), 400

    # Run fraud detection
    result = detect_fraud(app_id)
    
    return jsonify({"app_id": app_id, "fraud_detection_result": result})

if __name__ == "__main__":
    app.run()  # Running locally
