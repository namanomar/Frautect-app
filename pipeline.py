from datetime import datetime
import json
import re
import numpy as np
import google.generativeai as genai
import os
from dotenv import load_dotenv
from functions.google_play_scrap import get_play_store_data


def make_serializable(obj):
    """Convert non-serializable objects (like datetime) to string format."""
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to "YYYY-MM-DDTHH:MM:SS" format
    return obj


# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("❌ Error: GEMINI_API_KEY not found. Please check your .env file.")

# Save and load Gemini results
def save_gemini_result(app_id, result, filename="gemini_results.json"):
    """Save Gemini results in a structured JSON file instead of JSON Lines."""
    try:
        # Load existing results (if the file exists)
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)  # Load entire JSON as dict
        else:
            data = {}  # Empty dictionary if file doesn't exist

        # Update with new result
        data[app_id] = result

        # Save back to file
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)  # Save pretty JSON format

    except Exception as e:
        print(f"❌ Error saving Gemini result: {e}")

def load_gemini_result(app_id, filename="gemini_results.json"):
    """Load Gemini result from a structured JSON file."""
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)  # Load as dict
                return data.get(app_id, None)  # Return result if exists
        return None
    except Exception as e:
        print(f"❌ Error loading Gemini result: {e}")
        return None


def call_gemini(app_details, reviews):

    # Convert review data into a JSON serializable format
    reviews_serializable = [{k: make_serializable(v) for k, v in review.items()} for review in reviews]


    if app_details.get("title", "") == "Not Found":
        return json.loads('{"type": "unknown_id", "reason": "App not found on Play Store"}')

    prompt = f"""
    You are an expert in fraud detection, analyzing apps for potential fraud. Be **strict and vigilant** in identifying fraudulent behavior.

    ### **App Details**  
    {json.dumps(app_details, indent=2)}

    ### **Reviews**  
    {json.dumps(reviews_serializable, indent=2)}

    
    ## **STRICT FRAUD DETECTION RULES**
    - If the app has **excessive permissions**, fake reviews, or misleading descriptions, classify it as `"fraud"`.
    - If there are **clear signs of manipulation** (e.g., fake installs, repeated keywords, aggressive monetization), classify as `"fraud"`.
    - If the app shows **some suspicious behavior** but lacks conclusive evidence, classify as `"suspected"`.
    - **Only classify as `"genuine"` if there is NO sign of fraud.** Justify why the app is safe.

    ## **Output JSON Format**
    Ensure the response follows this JSON format **exactly**:
    ```json
    {{
        "type": "fraud"|"genuine"|"suspected",
        "reason": "Concise explanation (max 300 chars)"
    }}
    ```

    **Be strict! If in doubt, lean towards 'suspected' or 'fraud'.**
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # ✅ Remove Markdown JSON formatting (e.g., ```json ... ```)
    cleaned_response = re.sub(r"```json\n|\n```", "", response.text).strip()

    try:
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON response from Gemini: {cleaned_response}")
        return {"type": "suspected", "reason": "Invalid JSON format from Gemini"}

# Fraud detection pipeline
def detect_fraud(app_id):
    print(f"🔍 Checking fraud detection for: {app_id}")

    # Step 1: Get app details
    app_details, review_list = get_play_store_data(app_id)

    # Step 2: Analyze with Gemini
    gemini_result = call_gemini(app_details, review_list)
    save_gemini_result(app_id, gemini_result)
    return gemini_result
