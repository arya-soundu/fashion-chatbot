import os
import google.generativeai as genai

# Best practice: store your API key in an environment variable
# For now, you can paste it here for testing, but the other way is safer.
# genai.configure(api_key="YOUR_API_KEY_HERE")
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def load_knowledge():
    """Loads the clothing knowledge base from the text file."""
    with open('outfits_knowledge.txt', 'r') as file:
        return file.read()

def get_bot_response_gemini(user_text):
    """Gets a creative outfit recommendation from the Gemini API."""
    
    clothing_knowledge = load_knowledge()
    model = genai.GenerativeModel('gemini-pro')

    # This is the core of the new approach: The Prompt!
    prompt = f"""
    You are Aura, a creative and friendly AI fashion stylist. Your goal is to create a complete outfit for a user based on their request and the available clothing items.

    **KNOWLEDGE BASE (Available Clothes):**
    {clothing_knowledge}

    **USER'S REQUEST:**
    "{user_text}"

    **YOUR TASK:**
    1.  Analyze the user's request to understand the desired gender, occasion, and style.
    2.  From the knowledge base, select a suitable top, bottom, and shoes (or a dress and shoes).
    3.  If you cannot create a full outfit, explain why in a friendly way.
    4.  Return your response ONLY in the following JSON format. Do not add any other text or explanations outside of the JSON structure.

    {{
      "name": "A creative name for the outfit",
      "item_names": ["Name of Item 1", "Name of Item 2", "Name of Item 3"],
      "image_url": "An example image URL of a similar complete outfit from the web",
      "commentary": "A short, friendly comment about why this outfit is a great choice."
    }}
    """

    try:
        response = model.generate_content(prompt)
        # The API might return the JSON inside markdown, so we clean it up.
        json_response = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_response)
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return {"error": "I had a creative spark fizzle out! Could you try rephrasing your request?"}