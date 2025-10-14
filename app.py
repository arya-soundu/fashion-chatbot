from flask import Flask, render_template, request, jsonify, session
from chatbot import get_bot_response
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Needed for session management

# (Keep the add_personality function the same)
# ...
@app.route("/get_response", methods=["POST"])
def chat_response():
    user_text = request.json.get("message")
    # Get memory from the user's session, or start fresh
    memory = session.get('chat_memory', {}) 
    
    raw_response = get_bot_response(user_text, memory)
    
    # If the bot returned memory, save it back to the session
    if 'memory' in raw_response:
        session['chat_memory'] = raw_response['memory']
    else:
        # Clear memory after a successful recommendation
        session.pop('chat_memory', None)

    final_response = add_personality(raw_response)
    return jsonify(final_response)
@app.route("/")
def index():
    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True)