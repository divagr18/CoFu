
import google.generativeai as genai
from django.conf import settings

def initialize_gemini():
    """Initializes the Gemini API with your API key."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)  
        return genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05') 
    except Exception as e:
        print(f"Gemini API Initialization Error: {e}")
        return None  


def generate_text(model, prompt):
    """Sends a prompt to Gemini and returns the generated text."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None  