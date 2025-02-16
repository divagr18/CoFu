from django.shortcuts import render
from .forms import CompetitorAnalysisInputForm
from core.utils import initialize_gemini, generate_text
from django.http import JsonResponse
import logging
from duckduckgo_search import DDGS
import json

logger = logging.getLogger(__name__)

def get_search_results(query):
    """Gets search results from DuckDuckGo for a given query."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]  
            return results
    except Exception as e:
        logger.error(f"Error getting search results for {query}: {e}")
        return None

def competitor_analysis_view(request):
    if request.method == 'POST':
        logger.info("Request body: %s", request.body)  
        try:
            data = json.loads(request.body)  
            form = CompetitorAnalysisInputForm(data)
            if form.is_valid():
                competitor_1 = form.cleaned_data['competitor_1']
                competitor_2 = form.cleaned_data['competitor_2']
                competitor_3 = form.cleaned_data['competitor_3']
                
                competitor_1_results = get_search_results(competitor_1)
                competitor_2_results = get_search_results(competitor_2)
                competitor_3_results = get_search_results(competitor_3)

                
                prompt = f"""
                Analyze the following competitors and provide a comparative analysis, focusing on their strengths, weaknesses, and potential opportunities for differentiation:

                Competitor 1: {competitor_1}
                Search Results: {competitor_1_results}

                """
                if competitor_2 and competitor_2_results:
                    prompt += f"""
                    Competitor 2: {competitor_2}
                    Search Results: {competitor_2_results}
                    """
                if competitor_3 and competitor_3_results:
                    prompt += f"""
                    Competitor 3: {competitor_3}
                    Search Results: {competitor_3_results}
                    """

                prompt += """
                Provide a summary of each competitor's key strengths and weaknesses. Identify opportunities for differentiation based on market gaps and competitor weaknesses. Suggest niche marketing strategies for a new entrant.

                The response should be well-structured and highly suitable for presentation.
                """

                model = initialize_gemini()
                competitor_analysis_result = generate_text(model, prompt)
                
                data = {
                    'competitor_1': competitor_1,
                    'competitor_2': competitor_2,
                    'competitor_3': competitor_3,
                    'competitor_analysis_result': competitor_analysis_result,
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': form.errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"JSONDecode Error: {e}"}, status=400)
    else:
        form = CompetitorAnalysisInputForm()
        return render(request, 'competitor_analysis/competitor_analysis_input.html', {'form': form})