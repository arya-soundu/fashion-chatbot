import os
import google.generativeai as genai

# --- IMPORTANT ---
# Make sure you set your API key in the terminal before running this!
# On Windows: $env:GEMINI_API_KEY="YOUR_KEY_HERE"
# On macOS/Linux: export GEMINI_API_KEY="YOUR_KEY_HERE"
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("API Key not found! Please set the GEMINI_API_KEY environment variable.")
    exit()

print("--- Available Models for Your API Key ---")
for model in genai.list_models():
    # We only care about models that can actually generate content
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")

print("\n-----------------------------------------")