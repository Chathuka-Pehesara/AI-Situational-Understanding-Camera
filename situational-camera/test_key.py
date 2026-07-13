import os
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

try:
    genai.configure(api_key=api_key)
    print("Available models:")
    for m in genai.list_models():
        print(f" - {m.name}")
except Exception as e:
    print(f"Error testing key: {type(e).__name__} - {e}")
