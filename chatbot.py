import json
import random
import nltk

# Load Data and Keywords
with open("outfits.json",'r') as file:
    clothing_data = json.load(file)['items']

# Defining occasion keywords and style keywords (same as in json file)
OCCASION_KEYWORDS = {'work':['work','office','business','profesional'],'casual':['casual','weekend','day','realxed'],'formal':['formal','party','elegant']}
STYLE_KEYWORDS = { 'classic': ['classic', 'timeless', 'simple'], 'modern': ['modern', 'trendy', 'edgy'], 'boho': ['boho', 'bohemian', 'chic']}

#defining gender keywords
GENDER_KEYWORDS = {'men':['man','men','male','mens','guy'],
                   'women':['woman','women','womens','female','lady']}

#function to find category
def find_category(word,keyword_map):
    for cat,keywords in keyword_map.items():
        if word in keywords:
            return cat
    return None

def extract_entities_nltk(text):
    # Extracts occasion, gender and style from user text
    tokens=nltk.word_tokenize(text.lower())
    tagged_tokens=nltk.pos_tag(tokens)
    occasion = None
    gender = None
    style = None
    for word,tag in tagged_tokens:
        if tag in ['NN','NNS','JJ']: #Looks for nouns and adjectives
            if not occasion: occasion = find_category(word,OCCASION_KEYWORDS)
            if not gender: gender = find_category(word,GENDER_KEYWORDS)
            if not style: style = find_category(word,STYLE_KEYWORDS)
    return occasion,gender,style

def build_outfit(tags, gender):
    #Builds a unique outfit by finding items that match tags AND gender.
    # Filter items by gender first (including unisex items)
    gender_filtered_items = [item for item in clothing_data if item['gender'] in [gender, 'unisex']]

    # Handle dresses (only for women's requests)
    if gender == 'women' and any(tag in ['formal', 'event', 'party', 'summer'] for tag in tags):
        possible_dresses = [item for item in gender_filtered_items if item['type'] == 'dress' and any(t in item['tags'] for t in tags)]
        if possible_dresses:
            dress = random.choice(possible_dresses)
            # Find matching shoes
            possible_shoes = [item for item in gender_filtered_items if item['type'] == 'shoes' and any(t in item['tags'] for t in dress['tags'])]
            if possible_shoes:
                return {"name": f"A Complete {dress['tags'][0].title()} Look", "items": [dress, random.choice(possible_shoes)]}

    # Standard outfit build: top, bottom, shoes
    outfit = {}
    for item_type in ["top", "bottom", "shoes"]:
        # Find items of the correct type that match all requested tags
        possible_items = [item for item in gender_filtered_items if item['type'] == item_type and all(t in item['tags'] for t in tags)]
        if not possible_items: # If no perfect match, try a partial match
             possible_items = [item for item in gender_filtered_items if item['type'] == item_type and any(t in item['tags'] for t in tags)]
        if possible_items:
            outfit[item_type] = random.choice(possible_items)
    
    if len(outfit) == 3:
        return {"name": f"Your Custom {tags[1].title()} {tags[0].title()} Look", "items": [outfit['top'], outfit['bottom'], outfit['shoes']]}
        
    return None

def get_bot_response(user_text, memory={}):
    """Handles the conversation, now with memory for follow-up questions."""
    occasion, style, gender = extract_entities_nltk(user_text)

    # Use memory if available
    occasion = occasion or memory.get('occasion')
    style = style or memory.get('style')
    gender = gender or memory.get('gender')

    # --- NEW CONVERSATIONAL LOGIC ---
    if not gender:
        memory['occasion'] = occasion
        memory['style'] = style
        return {"error": "Of course! Are you looking for men's or women's fashion?", "memory": memory}
    
    if not occasion or not style:
        # Store what we know and ask for what's missing
        memory['gender'] = gender
        memory['occasion'] = occasion
        memory['style'] = style
        return {"error": "I can help with that! Could you also tell me the occasion and style you're thinking of?", "memory": memory}
    
    # If we have everything, build the outfit
    tags_to_match = [occasion, style]
    outfit = build_outfit(tags_to_match, gender)

    if outfit:
        outfit['item_names'] = [item['name'] for item in outfit['items']]
        # Use the main image of the most significant item (top or dress)
        outfit['image_url'] = outfit['items'][0]['image_url']
        return outfit
    else:
        return {"error": f"Sorry, I couldn't create a {gender} {style} outfit for a {occasion} occasion."}