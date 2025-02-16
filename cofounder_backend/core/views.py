from django.shortcuts import render
from django.conf import settings
import google.generativeai as genai
from .forms import PromptForm

def ask_gemini(request):
    gemini_response = None

    if request.method == 'POST':
        form = PromptForm(request.POST)
        if form.is_valid():
            user_prompt = form.cleaned_data['text']
            
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(user_prompt)
                gemini_response = response.text  
            except Exception as e:
                gemini_response = f"Error: {e}"  

    else:
        form = PromptForm() 

    return render(request, 'core/ask_gemini.html', {'form': form, 'gemini_response': gemini_response})
from django.middleware.csrf import get_token
from django.http import JsonResponse

def get_csrf_token_view(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})