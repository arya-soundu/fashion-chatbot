import json
from flask import Flask, render_template, request, jsonify
from chatbot_gemini import get_bot_response_gemini # <-- Importing the new function
import random

app = Flask(__name__)

def add_personality_gemini(response_data):
    """A personality layer specifically for Gemini's output."""
    if "error" in response_data:
        return {"display_html": f"<p>{response_data['error']}</p>"}

    # Gemini already provides commentary, so we just format it!
    outfit_card_html = f"""
        <div class="outfit-card">
            <img src="{response_data['image_url']}" alt="{response_data['name']}">
            <h4>{response_data['name']}</h4>
            <p><strong>Includes:</strong> {', '.join(response_data['item_names'])}</p>
            <p><strong>Aura's Note:</strong> {response_data['commentary']}</p>
        </div>
    """
    return {"display_html": outfit_card_html}

@app.route("/")
def index():
    return render_template("index.html")

# In app_gemini.py

@app.route("/get_response", methods=["POST"])
def chat_response():
    user_text = request.json.get("message")
    # Get memory from the user's session, or start fresh
    memory = session.get('chat_memory', {}) 
    
    raw_response = get_bot_response_gemini(user_text, memory)
    
    # If the bot returned a question, update the memory
    if 'question' in raw_response:
        session['chat_memory'] = raw_response.get('memory', {})
        # Format the question for display
        final_response = {"display_html": f"<p>{raw_response['question']}</p>"}
    else:
        # If we got a full response, clear the memory
        session.pop('chat_memory', None)
        final_response = add_personality_gemini(raw_response)
        
    return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=True, port=5001) # Using a different port to avoid conflicts