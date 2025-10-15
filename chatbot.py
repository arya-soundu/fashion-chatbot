import json
import random

# --- Load Data and Keywords ---
with open('outfits.json', 'r') as file:
    clothing_data = json.load(file)['items']

OCCASION_KEYWORDS = {
    'work': ['work', 'office', 'business', 'professional'],
    'casual': ['casual', 'weekend', 'day', 'relaxed', 'chilling'],
    'formal': ['formal', 'party', 'event', 'elegant', 'wedding']
}
STYLE_KEYWORDS = {
    'classic': ['classic', 'timeless', 'simple'],
    'modern': ['modern', 'trendy', 'edgy', 'cool'],
    'boho': ['boho', 'bohemian', 'chic', 'flowy']
}
GENDER_KEYWORDS = {
    'mens': ['man', 'men', 'mens', 'male', 'guy'],
    'womens': ['woman', 'women', 'womens', 'female', 'lady']
}

# --- This function does not change ---
def find_category(word, keyword_map):
    """Finds which category a word belongs to."""
    for category, keywords in keyword_map.items():
        if word in keywords:
            return category
    return None

# --- THIS IS THE NEW BRAIN - NO NLTK NEEDED ---
def extract_entities_simple(text):
    """Extracts entities using simple word matching."""
    words = text.lower().split()
    occasion = None
    style = None
    gender = None

    for word in words:
        # Remove punctuation for better matching, e.g., "men's" -> "mens"
        cleaned_word = ''.join(filter(str.isalnum, word))
        
        if not occasion:
            occasion = find_category(cleaned_word, OCCASION_KEYWORDS)
        if not style:
            style = find_category(cleaned_word, STYLE_KEYWORDS)
        if not gender:
            gender = find_category(cleaned_word, GENDER_KEYWORDS)
            
    return occasion, style, gender

# --- This function does not change ---
def build_outfit(tags, gender):
    """Builds a unique outfit by finding items that match tags AND gender."""
    gender_filtered_items = [item for item in clothing_data if item['gender'] in [gender, 'unisex']]

    if gender == 'womens' and any(tag in ['formal', 'event', 'party', 'summer'] for tag in tags):
        possible_dresses = [item for item in gender_filtered_items if item['type'] == 'dress' and any(t in item['tags'] for t in tags)]
        if possible_dresses:
            dress = random.choice(possible_dresses)
            possible_shoes = [item for item in gender_filtered_items if item['type'] == 'shoes' and any(t in item['tags'] for t in dress['tags'])]
            if possible_shoes:
                return {"name": f"A Complete {dress['tags'][0].title()} Look", "items": [dress, random.choice(possible_shoes)]}

    outfit = {}
    for item_type in ["top", "bottom", "shoes"]:
        possible_items = [item for item in gender_filtered_items if item['type'] == item_type and all(t in item['tags'] for t in tags)]
        if not possible_items:
             possible_items = [item for item in gender_filtered_items if item['type'] == item_type and any(t in item['tags'] for t in tags)]
        if possible_items:
            outfit[item_type] = random.choice(possible_items)
    
    if len(outfit) == 3:
        return {"name": f"Your Custom {tags[1].title()} {tags[0].title()} Look", "items": [outfit['top'], outfit['bottom'], outfit['shoes']]}
        
    return None

# --- This function now calls the new, simpler brain ---
def get_bot_response(user_text, memory={}):
    """Handles the conversation flow."""
    # We now call our simple function instead of the NLTK one
    occasion, style, gender = extract_entities_simple(user_text)

    occasion = occasion or memory.get('occasion')
    style = style or memory.get('style')
    gender = gender or memory.get('gender')

    if not gender:
        memory['occasion'] = occasion
        memory['style'] = style
        return {"error": "Of course! Are you looking for men's or women's fashion?", "memory": memory}
    
    if not occasion or not style:
        memory['gender'] = gender
        memory['occasion'] = occasion
        memory['style'] = style
        return {"error": "I can help with that! Could you also tell me the occasion and style you're thinking of?", "memory": memory}
    
    tags_to_match = [occasion, style]
    outfit = build_outfit(tags_to_match, gender)

    if outfit:
        outfit['item_names'] = [item['name'] for item in outfit['items']]
        outfit['image_url'] = outfit['items'][0]['image_url']
        return outfit
    else:
        return {"error": f"Sorry, I couldn't create a {gender} {style} outfit for a {occasion} occasion."}