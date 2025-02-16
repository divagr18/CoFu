from django.shortcuts import render
from .forms import PromptForm
from .utils import initialize_gemini, generate_text  

def ask_gemini(request):
    gemini_response = None

    if request.method == 'POST':
        form = PromptForm(request.POST)
        if form.is_valid():
            user_prompt = form.cleaned_data['text']
            model = initialize_gemini()
            if model:
                gemini_response = generate_text(model, user_prompt)

                if not gemini_response:
                    gemini_response = "Error: Failed to generate response from Gemini."
            else:
                gemini_response = "Error: Could not initialize Gemini."

    else:
        form = PromptForm()

    return render(request, 'core/ask_gemini.html', {'form': form, 'gemini_response': gemini_response})