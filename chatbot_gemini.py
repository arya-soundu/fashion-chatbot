import os
import json
import random
import google.generativeai as genai

# DO NOT configure the key here. We will do it inside the function.

# Keywords for simple gender and greeting extraction
GENDER_KEYWORDS = {
    'mens': ['man', 'men', 'mens', 'male', 'guy'],
    'womens': ['woman', 'women', 'womens', 'female', 'lady']
}
GREETINGS = [
    'hi', 'hii', 'hello', 'hey', 'heyy', 'heyyy', 'yo', 'sup',
    "what's up", 'good morning', 'good afternoon', 'good evening'
]

def load_knowledge():
    """Loads the clothing knowledge base from the text file."""
    with open('outfits_knowledge.txt', 'r') as file:
        return file.read()

def extract_gender_simple(text):
    """Finds a gender keyword in the user's text."""
    words = text.lower().split()
    for word in words:
        cleaned_word = ''.join(filter(str.isalnum, word))
        for gender, keywords in GENDER_KEYWORDS.items():
            if cleaned_word in keywords:
                return gender
    return None

def get_bot_response_gemini(user_text, memory={}):
    """Handles the full conversation with a pre-flight check for the API key."""
    
    # 1. Handle simple greetings first (this doesn't need an API key).
    if user_text.lower().strip() in GREETINGS:
        responses = [
            "Hello there! How can I help you with your style today?",
            "Hi! Ready to find the perfect outfit?",
            "Hey! What kind of look are you going for?"
        ]
        return {"greeting": random.choice(responses)}

    # 2. --- PRE-FLIGHT CHECK FOR API KEY ---
    # This is the most important fix. The server will no longer crash.
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except KeyError:
        return {"error": "CRITICAL ERROR: The GEMINI_API_KEY is not set in your terminal. Please stop the server, set the key using the '$env:...' command, and restart."}
    # ----------------------------------------

    # 3. Proceed with normal logic if the key exists.
    gender = extract_gender_simple(user_text) or memory.get('gender')

    if not gender:
        memory['original_request'] = user_text
        return {"question": "Of course! To give you the best recommendation, are you looking for men's or women's fashion?", "memory": memory}
    
    full_request = user_text
    if 'original_request' in memory:
        full_request = f"{memory['original_request']} for a {gender} person"

    clothing_knowledge = load_knowledge()
    model = genai.GenerativeModel('gemini-1.0-pro')

    prompt = f"""
    You are Weaver, a creative AI fashion stylist. Your goal is to create an outfit based on a user's request and a knowledge base of clothes. You must respond ONLY with a valid JSON object.

    --- EXAMPLE OF A GOOD RESPONSE ---
    USER REQUEST: "I need a classic work outfit for a man."
    YOUR JSON RESPONSE:
    {{
      "name": "Classic Business Professional",
      "item_names": ["Blue Dress Shirt", "Grey Suit Trousers", "Brown Oxford Shoes"],
      "image_url": "https://i.pinimg.com/564x/8a/0a/2c/8a0a2c0f6b3e9a5d3f8a0a9a1d3f0a3e.jpg",
      "commentary": "This is a timeless and professional look, perfect for the office or a formal business meeting."
    }}
    --- END OF EXAMPLE ---

    --- CURRENT TASK ---
    USER REQUEST: "{full_request}"
    KNOWLEDGE BASE (Available Clothes):
    {clothing_knowledge}
    
    YOUR TASK:
    1. Analyze the user's request to understand the desired gender, occasion, and style.
    2. From the knowledge base, create a complete, stylish outfit. It must be appropriate for the specified gender.
    3. A complete outfit consists of at least a top and bottom (or a dress), and shoes. You can also include optional items like 'outerwear' or an 'accessory'.
    4. Return your response ONLY in the following JSON format. Do not add any other text.

    YOUR JSON RESPONSE:
    """

    try:
        response = model.generate_content(prompt)
        json_response = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_response)
    except Exception as e:
        print(f"--- ERROR PARSING GEMINI RESPONSE ---")
        print(f"ERROR: {e}")
        print(f"RAW RESPONSE FROM API:\n{response.text if 'response' in locals() else 'No response object'}")
        print("-------------------------------------")
        return {"error": "I had a creative spark fizzle out! The AI's response was not in the correct format. Could you try rephrasing?"}