from django.shortcuts import render
from .forms import SWOTInputForm
from core.utils import initialize_gemini, generate_text
import json
from django.http import JsonResponse    
def swot_analysis_view(request):
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)
            business_description = data.get('business_description')
            industry = data.get('industry')

            if not business_description or not industry:
                return JsonResponse({
                    'error': 'Missing required fields'
                }, status=400)

            
            assumption_prompt = f"""
            As an expert business analyst, identify key market conditions, resource availability factors, 
            and potential competitive landscape elements relevant to the {industry} industry. 
            Provide these as a series of concise bullet points. Focus on assumptions a startup in this industry should consider.
            """

            model = initialize_gemini()
            generated_assumptions = generate_text(model, assumption_prompt)

            
            swot_prompt = f"""
            Analyze the following business idea and provide a detailed SWOT analysis, taking into account the following industry assumptions:

            Business Description: {business_description}

            Industry: {industry}

            **Assumptions:**
            {generated_assumptions}

            Include:
            *   Strengths (internal advantages, considering the stated assumptions)
            *   Weaknesses (internal disadvantages, considering the stated assumptions)
            *   Opportunities (external factors that can be exploited, given the market assumptions)
            *   Threats (external factors that can cause problems, given the market assumptions)

            Provide a risk and opportunity assessment, considering potential regulatory, financial, and market risks, and how these risks are affected by the stated assumptions.

            Format the output clearly with headings for each SWOT element.
            """

            swot_result = generate_text(model, swot_prompt)

            
            return JsonResponse({
                'business_description': business_description,
                'industry': industry,
                'generated_assumptions': generated_assumptions,
                'swot_result': swot_result,
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    
    return JsonResponse({
        'message': 'This endpoint accepts POST requests only'
    }, status=405)
