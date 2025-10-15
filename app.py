from flask import Flask, render_template, request, jsonify, session
from chatbot import get_bot_response
import random

app = Flask(__name__)
app.secret_key = 'a_super_secret_key_for_sessions' # Needed for session management

@app.route("/")
def index():
    """Renders the main homepage for the chatbot."""
    return render_template("index.html")

def add_personality(response_data):
    """
    This is the missing function. It takes the bot's raw data and wraps it in
    friendly text and the HTML needed to display the outfit card.
    """
    # Handle error messages first
    if "error" in response_data:
        return {"display_html": f"<p>{response_data['error']}</p>"}

    greetings = [
        "Of course! Based on your request, I've put together a look I think you'll love.",
        "I've got just the thing! Here’s an outfit that fits your vibe:",
        "Excellent choice! Check out this look I've curated for you:"
    ]
    tips = [
        "You could accessorize with a simple necklace to complete the look.",
        "This outfit pairs wonderfully with a leather jacket for a cooler evening.",
        "Consider a bold handbag to make a statement with this ensemble."
    ]

    # Build the final HTML response card
    outfit_card_html = f"""
        <div class="outfit-card">
            <img src="{response_data.get('image_url', '')}" alt="{response_data.get('name', 'Outfit')}">
            <h4>{response_data.get('name', 'Recommended Outfit')}</h4>
            <p><strong>Includes:</strong> {', '.join(response_data.get('item_names', []))}</p>
            <p><strong>Style Tip:</strong> {random.choice(tips)}</p>
        </div>
    """
    
    full_response_html = f"<p>{random.choice(greetings)}</p>{outfit_card_html}"

    return {"display_html": full_response_html}


@app.route("/get_response", methods=["POST"])
def chat_response():
    """Handles the user's message and returns the bot's response."""
    user_text = request.json.get("message")
    memory = session.get('chat_memory', {}) 
    
    raw_response = get_bot_response(user_text, memory)
    
    if 'memory' in raw_response:
        session['chat_memory'] = raw_response['memory']
    else:
        session.pop('chat_memory', None)

    # This line was causing the error, but will now work
    final_response = add_personality(raw_response)
    return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=True)