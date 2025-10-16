import os
from flask import Flask, render_template, request, jsonify, session
from chatbot_gemini import get_bot_response_gemini

app = Flask(__name__)
# A secret key is required for session management to remember conversations.
app.secret_key = os.urandom(24)

@app.route("/")
def index():
    """Renders the main homepage for the chatbot."""
    return render_template("index.html")

def add_personality_gemini(response_data):
    """Formats the AI's JSON response into displayable HTML with a placeholder for missing images."""
    if "error" in response_data:
        return {"display_html": f"<p>{response_data['error']}</p>"}

    image_url = response_data.get('image_url')
    if not image_url: # If the AI fails to find an image, use a placeholder.
        image_url = "https://placehold.co/600x400/EEE/31343C?text=Image+Not+Found"

    outfit_card_html = f"""
        <div class="outfit-card">
            <img src="{image_url}" alt="{response_data.get('name', 'Outfit')}">
            <h4>{response_data.get('name', 'Recommended Outfit')}</h4>
            <p><strong>Includes:</strong> {', '.join(response_data.get('item_names', []))}</p>
            <p><strong>Weaver's Note:</strong> {response_data.get('commentary', '')}</p>
        </div>
    """
    return {"display_html": outfit_card_html}

@app.route("/get_response", methods=["POST"])
def chat_response():
    """Handles the user's message and returns the bot's response."""
    user_text = request.json.get("message")
    memory = session.get('chat_memory', {}) 
    
    raw_response = get_bot_response_gemini(user_text, memory)
    
    # Handle the different types of responses from the bot
    if 'greeting' in raw_response:
        final_response = {"display_html": f"<p>{raw_response['greeting']}</p>"}
    elif 'question' in raw_response:
        session['chat_memory'] = raw_response.get('memory', {})
        final_response = {"display_html": f"<p>{raw_response['question']}</p>"}
    else: # This is a full outfit recommendation
        session.pop('chat_memory', None) # Clear memory after a success
        final_response = add_personality_gemini(raw_response)
        
    return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=True, port=5001)