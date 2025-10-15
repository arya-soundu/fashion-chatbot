import os
import json
import google.generativeai as genai

# Configure the API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Keywords for our simple gender extractor
GENDER_KEYWORDS = {
    'mens': ['man', 'men', 'mens', 'male', 'guy'],
    'womens': ['woman', 'women', 'womens', 'female', 'lady']
}

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
    """Handles the conversation, now with gender awareness and memory."""
    
    # First, try to find a gender in the user's text or in memory
    gender = extract_gender_simple(user_text) or memory.get('gender')

    # If no gender is found, ask for it and stop.
    if not gender:
        # Save the original request in memory
        memory['original_request'] = user_text
        return {"question": "Of course! To give you the best recommendation, are you looking for men's or women's fashion?", "memory": memory}
    
    # If we have a gender, combine it with the original request from memory if needed
    full_request = user_text
    if 'original_request' in memory:
        full_request = f"{memory['original_request']} for a {gender} person"

    clothing_knowledge = load_knowledge()
    model = genai.GenerativeModel('gemini-1.0-pro') # Or the specific model name that works for you

    # The prompt is now given the gender to ensure it makes a relevant outfit
    prompt = f"""
    You are Aura, a creative and friendly AI fashion stylist.
    Your goal is to create a complete outfit for a user based on their request and the available clothing items.

    **KNOWLEDGE BASE (Available Clothes):**
    {clothing_knowledge}

    **USER'S REQUEST:**
    "{full_request}"

    **YOUR TASK:**
    1.  Create a complete outfit (e.g., top, bottom, shoes) suitable for the user's request from the knowledge base.
    2.  The outfit must be appropriate for the specified gender in the request.
    3.  Return your response ONLY in the following JSON format. Do not add any other text.

    {{
      "name": "A creative name for the outfit",
      "item_names": ["Name of Item 1", "Name of Item 2", "Name of Item 3"],
      "image_url": "An example image URL of a similar complete outfit from the web",
      "commentary": "A short, friendly comment about why this outfit is a great choice."
    }}
    """

    try:
        response = model.generate_content(prompt)
        json_response = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_response)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return {"error": "I had a creative spark fizzle out! Could you try rephrasing your request?"}