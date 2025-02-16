from django.shortcuts import render
from .forms import BusinessModelInputForm
from core.utils import initialize_gemini, generate_text
from django.http import JsonResponse
import logging
import json


logger = logging.getLogger(__name__)

def business_model_view(request):
    if request.method == 'POST':
        logger.info("business_model_view: Received POST request")
        logger.info("business_model_view: Request body: %s", request.body) 
        try:
            data = json.loads(request.body)  
            logger.info("business_model_view: Parsed JSON data: %s", data)
            form = BusinessModelInputForm(data)
            if form.is_valid():
                logger.info("business_model_view: Form is valid")
                industry = form.cleaned_data['industry']
                target_market = form.cleaned_data['target_market']
                business_description = form.cleaned_data['business_description']

                
                prompt = f"""
                Recommend suitable monetization models for a business in the {industry} industry, targeting {target_market}.

                Business Description: {business_description}

                Evaluate the revenue potential, scalability, and acquisition costs of each recommended model.
                Suggest customer acquisition strategies (organic vs. paid) and optimal growth strategies based on market gaps.

                Provide a detailed explanation of each recommended model and its suitability for this business.
                """

                model = initialize_gemini()
                business_model_result = generate_text(model, prompt)

                
                data = {
                    'industry': industry,
                    'target_market': target_market,
                    'business_description': business_description,
                    'business_model_result': business_model_result,
                }
                logger.info("business_model_view: Returning JSON response: %s", data)
                return JsonResponse(data)
            else:
                logger.warning("business_model_view: Form is invalid: %s", form.errors)
                
                return JsonResponse({'error': form.errors}, status=400)  
        except json.JSONDecodeError as e:
            logger.error("business_model_view: Invalid JSON: %s", e)
            return JsonResponse({'error': f"Invalid JSON: {e}"}, status=400) 
        except Exception as e:
            logger.exception("business_model_view: An exception occurred: %s", e)
            return JsonResponse({'error': str(e)}, status=500) 
    else:
        form = BusinessModelInputForm()
        return render(request, 'business_model/business_model_input.html', {'form': form})