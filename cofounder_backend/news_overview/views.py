from django.shortcuts import render
from .forms import NewsOverviewInputForm
from core.utils import initialize_gemini, generate_text  
from django.http import JsonResponse
import logging
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import (
    ConversationLimitException,
    DuckDuckGoSearchException,
    RatelimitException,
    TimeoutException,
)
from datetime import datetime, timedelta
import json
import numpy as np
import time 
import random 

import os
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

from openai import OpenAI
client = OpenAI()

client.api_key = os.getenv("OPENAI_API_KEY")

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

def embed_text(text):
    """Embeds a given text using OpenAI's embeddings API."""
    try:
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"  
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None


def get_news_articles(sector, max_results=10, max_retries=3, delay=5):
    """Gets recent news articles about the sector from DuckDuckGo and embeds them."""
    for attempt in range(max_retries):
        try:
            user_agent = random.choice(USER_AGENTS)
            with DDGS(headers={"User-Agent": user_agent}) as ddgs:
                results = [r for r in ddgs.news(
                    sector,
                    max_results=max_results,
                    safesearch='Off',
                    timelimit='m1'  
                )]
                
                for r in results:
                    r['embedding'] = embed_text(r['body']) 
                return results
        except RatelimitException as e:
            logger.warning(f"Rate limit exceeded for {sector}. Attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds.")
            if attempt < max_retries - 1:
                time.sleep(delay)  
            else:
                logger.error(f"Max retries exceeded due to rate limit for {sector}.")
                return None
        except TimeoutException as e:
            logger.warning(f"Timeout occurred for {sector}. Attempt {attempt + 1}/{max_retries}. Retrying in {delay} seconds.")
            if attempt < max_retries - 1:
                time.sleep(delay)  
            else:
                logger.error(f"Max retries exceeded due to timeout for {sector}.")
                return None
        except DuckDuckGoSearchException as e:
            logger.error(f"DuckDuckGo Search Exception for {sector}: {e}")
            return None
        except ConversationLimitException as e:
            logger.error(f"Conversation Limit Exception for {sector}: {e}")
            return None
        except Exception as e:
            logger.error(f"General Exception for {sector}: {e}")
            return None
    return None  

def analyze_sentiment_with_llm(text):
    """Analyzes the sentiment of a given text using the LLM."""
    try:
        model = initialize_gemini()
        prompt = f"""
        Analyze the sentiment of the following text:

        {text}

        Is the sentiment positive, negative, or neutral?  Respond with only one word: Positive, Negative, or Neutral.
        """
        sentiment = generate_text(model, prompt)
        return sentiment.strip()  
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return "Neutral" 

def news_overview_view(request):
    if request.method == 'POST':
        logger.info("news_overview: Request body: %s", request.body)  
        try:
            data = json.loads(request.body)
            logger.info("news_overview: Parsed JSON data: %s", data)
            form = NewsOverviewInputForm(data)
            if form.is_valid():
                logger.info("news_overview: Form is valid")
                sector = form.cleaned_data['sector']

                
                news_articles = get_news_articles(sector)

                
                num_articles = len(news_articles) if news_articles else 0
                sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
                if news_articles:
                    for article in news_articles:
                        sentiment = analyze_sentiment_with_llm(article['body'])
                        sentiment_counts[sentiment] += 1

                
                prompt = f"""
                Provide a general overview of the {sector} sector based on the following recent news articles. Focus on identifying the most common themes, opportunities and trends.

                Number of Articles: {num_articles}
                Overall Sentiment: {sentiment_counts}
                Market size : 
                """
                if news_articles:
                    prompt += "Include the following search results:\n"
                    for article in news_articles:
                        prompt += f"-{article.get('title', 'N/A')}: {article.get('body', 'N/A')}\n" 

                model = initialize_gemini()
                news_overview_result = generate_text(model, prompt)

                
                data = {
                    'sector': sector,
                    'news_overview_result': news_overview_result,
                    'num_articles': num_articles,
                    'sentiment_counts': sentiment_counts,
                }
                return JsonResponse(data)
            else:
                logger.warning("news_overview: Form is invalid: %s", form.errors)
                
                return JsonResponse({'error': form.errors}, status=400)
        except json.JSONDecodeError as e:
            logger.error("news_overview: Invalid JSON: %s", e)
            return JsonResponse({'error': f"Invalid JSON: {e}"}, status=400)
    else:
        form = NewsOverviewInputForm()
        return render(request, 'news_overview/news_overview_input.html', {'form': form})