from django.shortcuts import render
from .forms import MarketSizeInputForm
from core.utils import initialize_gemini, generate_text  
from django.http import JsonResponse
import json
def market_size_view(request):
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)
            industry = data.get('industry')
            region = data.get('region')
            target_market = data.get('target_market')

            customer_segment = data.get('customer_segment', '')
            average_selling_price = data.get('average_selling_price', 0.0)

            if not all([industry, region, target_market]):
                return JsonResponse({
                    'error': 'Missing required fields: industry, region, and target_market are required'
                }, status=400)

            
            prompt = f"""
            Estimate the Total Addressable Market (TAM), Serviceable Available Market (SAM), and Serviceable Obtainable Market (SOM)
            for the {industry} industry in {region}.

            Target Market: {target_market}
            """

            if customer_segment:
                prompt += f"\nCustomer Segment: {customer_segment}"
            if average_selling_price:
                prompt += f"\nAverage Selling Price: {average_selling_price} USD"

            prompt += """

            Provide estimates in USD.
            Explain the methodology and assumptions used to derive the estimates.

            Also, provide a growth rate forecast for this market over the next 5 years.

            Format the response with clear sections for:
            1. Market Size Estimates (TAM, SAM, SOM)
            2. Methodology and Assumptions
            3. Growth Forecast
            """

            
            model = initialize_gemini()
            market_size_result = generate_text(model, prompt)

            
            return JsonResponse({
                'industry': industry,
                'region': region,
                'target_market': target_market,
                'customer_segment': customer_segment,
                'average_selling_price': average_selling_price,
                'market_size_result': market_size_result,
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