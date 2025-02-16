import streamlit as st
import requests
import json
import openai
import chromadb
import os
from chromadb.utils import embedding_functions
import time
import traceback
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
import tiktoken

openai.api_key = 'redacted'
os.environ["OPENAI_API_KEY"] = openai.api_key

client = OpenAI(api_key=openai.api_key)

DJANGO_SWOT_URL = "http://127.0.0.1:8000/swot_analysis/analyze/"
DJANGO_MARKET_SIZE_URL = "http://127.0.0.1:8000/market_size/estimate/"
DJANGO_BUSINESS_MODEL_URL = "http://127.0.0.1:8000/business_model/recommend/"
DJANGO_COMPETITOR_ANALYSIS_URL = "http://127.0.0.1:8000/competitor_analysis/analyze/"
DJANGO_NEWS_OVERVIEW_URL = "http://127.0.0.1:8000/news_overview/overview/"

st.set_page_config(
    page_title="Co-Founder App",
    layout="wide"
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai.api_key,
                model_name="text-embedding-3-small"
)
chroma_client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False, is_persistent=True), database="default_database", tenant="default_tenant")

collection_name_swot = "swot_analysis_collection"
collection_name_market_size = "market_size_collection"
collection_name_business_model = "business_model_collection"
collection_name_competitor = "competitor_analysis_collection"
collection_name_news = "news_analysis_collection"


def get_chroma_collection(collection_name):
    try:
        collection = chroma_client.get_collection(name=collection_name, embedding_function=openai_ef)
        print("Collection exists, proceeding")
    except Exception as e:
        if isinstance(e, chromadb.errors.InvalidCollectionException):
            print("Collection doesn't exist, creating it.")
            collection = chroma_client.create_collection(name=collection_name, embedding_function=openai_ef)
        else:
            raise  
    return collection

swot_collection = get_chroma_collection(collection_name_swot)
market_size_collection = get_chroma_collection(collection_name_market_size)
business_model_collection = get_chroma_collection(collection_name_business_model)
competitor_collection = get_chroma_collection(collection_name_competitor)
news_collection = get_chroma_collection(collection_name_news)

collection_dict = {
    "swot_analysis": swot_collection,
    "market_size_estimation": market_size_collection,
    "business_model_recommendation": business_model_collection,
    "competitor_analysis": competitor_collection,
    "news_overview": news_collection
}

def make_api_request(url, data, collection, analysis_type, max_retries=3):
    for attempt in range(max_retries):
        try:
            headers = {'Content-Type': 'application/json'}

            # RAG implementation
            query = f"Industry: {data.get('industry', '')}, Business Description: {data.get('business_description', '')}, Target Market: {data.get('target_market', '')}, Sector: {data.get('sector', '')}"

            results = collection.query(
                query_texts=[query],
                n_results=2
            )

            context = "\n".join(results['documents'][0]) if results and results['documents'] else "No prior context found."

            max_context_tokens = 3000
            encoding = tiktoken.encoding_for_model("gpt-4o-mini-2024-07-18")
            encoded_context = encoding.encode(context)
            truncated_context = encoding.decode(encoded_context[:max_context_tokens])

            data['context'] = truncated_context

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            response_data = response.json()

   
            try:
                collection.add(
                    documents=[f"User Input: {data}\nAPI Response: {response_data}"],
                    ids=[f"{analysis_type}-{len(collection.get()['ids'])}"] 
                )
            except Exception as e:
                st.error(f"Error adding data to ChromaDB: {e}. Traceback: {traceback.format_exc()}")
            return response_data

        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {e}")
            return None
        except json.JSONDecodeError as e:
            st.error(f"JSON Decode Error: {e}.  Response Text: {response.text if 'response' in locals() else 'No response'}")
            return None
        except APIConnectionError as e:
            st.warning(f"Failed to connect to OpenAI API (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt) 
        except RateLimitError as e:
            st.warning(f"OpenAI API Rate Limit exceeded (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt) 
        except APIStatusError as e:
            st.error(f"OpenAI API returned an error: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {e}. Traceback: {traceback.format_exc()}")
            return None
    st.error("Max retries reached. Failed to complete the API request.")
    return None

def show_history(collection, analysis_type):
    try:
        results = collection.get() 
        if results and results['ids']:
            st.subheader("Analysis History")

            if st.button("Clear History", key=f"clear_{analysis_type}"):
                collection.delete(ids=results['ids'])
                st.success("History cleared!")
                st.rerun() 

            for i, id in enumerate(results['ids']):
                if id.startswith(analysis_type):
                    st.markdown(f"**Analysis {i + 1}:**")
                    st.markdown(f"*ID:* {id}")
                    documents = results['documents'][i].split("\\n")

                    st.markdown(f"*User Input:* {documents[0]}") 
                    st.markdown(f"*API Response:* {documents[1]}") 
                    st.markdown("---")
        else:
            st.info("No history found for this analysis type.")
    except Exception as e:
        st.error(f"Error retrieving history: {e}")

def show_swot_analysis():
    analysis_tab, history_tab = st.tabs(["Analysis", "History"])

    with analysis_tab:
        st.header("SWOT Analysis")
        business_description = st.text_area(
            "Describe your business idea:",
            height=200,
            placeholder="Enter a detailed description of your business concept..."
        )

        industry = st.text_input(
            "Enter the industry:",
            placeholder="e.g., e-commerce, fintech, healthcare"
        )

        if st.button("Generate SWOT Analysis"):
            if business_description and industry:
                with st.spinner("Analyzing your business..."):
                    data = {'business_description': business_description, 'industry': industry}
                    results = make_api_request(DJANGO_SWOT_URL, data, swot_collection, "swot_analysis")

                    if results:
                        st.markdown("### Analysis Results "+":material/dashboard:")
                        st.markdown(f"#### Business Overview")
                        st.markdown(f"*Industry:* {results.get('industry', 'N/A')}")
                        st.markdown(f"*Description:* {results.get('business_description', 'N/A')}")

                        st.markdown("#### Key Market Assumptions")
                        st.markdown(f"{results.get('generated_assumptions', 'N/A')}")

                        st.markdown("#### SWOT Analysis")
                        st.markdown(f"{results.get('swot_result', 'N/A')}")
            else:
                st.warning("Please provide both a business description and industry.")

    with history_tab:
        show_history(swot_collection, "swot_analysis")

def show_market_size_estimation():
    analysis_tab, history_tab = st.tabs(["Analysis", "History"])

    with analysis_tab:
        st.header("Market Size Estimation")
        industry = st.text_input("Enter the industry:", help="e.g., 'e-commerce', 'fintech', 'healthcare'")
        region = st.text_input("Enter the region:", help="e.g., 'United States', 'Europe', 'Asia'")
        target_market = st.text_area("Describe the target market:", height=100, help="e.g., 'Small businesses in the US'")
        customer_segment = st.text_input("Customer segment (optional):", help="e.g., 'B2B', 'B2C', 'SaaS'")
        average_selling_price = st.number_input("Average selling price in USD (optional):", value=0.0, format="%.2f")

        if st.button("Estimate Market Size"):
            if industry and region and target_market:
                with st.spinner("Estimating market size..."):
                    data = {
                        'industry': industry,
                        'region': region,
                        'target_market': target_market,
                        'customer_segment': customer_segment,
                        'average_selling_price': average_selling_price,
                    }
                    results = make_api_request(DJANGO_MARKET_SIZE_URL, data, market_size_collection, "market_size_estimation")

                    if results:
                        st.markdown("### Market Size Results "+":material/pie_chart:")
                        st.markdown(f"#### Business Overview")
                        st.markdown(f"*Industry:* {results.get('industry', 'N/A')}")
                        st.markdown(f"*Region:* {results.get('region', 'N/A')}")
                        st.markdown(f"*Target Market:* {results.get('target_market', 'N/A')}")

                        if results.get('customer_segment'):
                            st.markdown(f"*Customer Segment:* {results['customer_segment']}")
                        if results.get(
                            'average_selling_price'):
                            st.markdown(f"*Average Selling Price:* {results['average_selling_price']} USD")

                        st.markdown("#### 💰 Market Size Estimation")
                        st.markdown(f"{results.get('market_size_result', 'N/A')}")
            else:
                st.warning("Please enter an industry, a region, and a target market.")

    with history_tab:
        show_history(market_size_collection, "market_size_estimation")

def show_business_model_recommendation():
    analysis_tab, history_tab = st.tabs(["Analysis", "History"])

    with analysis_tab:
        st.header("Business Model Recommendation")
        industry = st.text_input("Enter the industry:", help="e.g., 'e-commerce', 'fintech', 'healthcare'")
        target_market = st.text_area("Describe the target market:", height=100, help="e.g., 'Small businesses in the US'")
        business_description = st.text_area(
            "Describe your business idea:",
            height=200,
            placeholder="Provide a detailed description of your business concept"
        )

        if st.button("Recommend Business Model"):
            if industry and target_market and business_description:
                with st.spinner("Recommending business model..."):
                    data = {
                        'industry': industry,
                        'target_market': target_market,
                        'business_description': business_description
                    }
                    results = make_api_request(DJANGO_BUSINESS_MODEL_URL, data, business_model_collection, "business_model_recommendation")

                    if results:
                        st.markdown("### Business Model Recommendation "+":material/receipt_long:")
                        st.markdown(f"#### Business Overview")
                        st.markdown(f"*Industry:* {results.get('industry', 'N/A')}")
                        st.markdown(f"*Target Market:* {results.get('target_market', 'N/A')}")
                        st.markdown(f"*Business Description:* {results.get('business_description', 'N/A')}")

                        st.markdown("#### Recommended Business Model")
                        st.markdown(f"{results.get('business_model_result', 'N/A')}")
            else:
                st.warning("Please enter an industry, a target market, and a business description.")

    with history_tab:
        show_history(business_model_collection, "business_model_recommendation")

def show_competitor_analysis():
    analysis_tab, history_tab = st.tabs(["Analysis", "History"])

    with analysis_tab:
        st.header("Competitor Analysis")
        competitor_1 = st.text_input("Competitor 1 (Name or Website):", help="Enter the name or URL of your first competitor")
        competitor_2 = st.text_input("Competitor 2 (Name or Website):", help="Enter the name or URL of your second competitor (optional)")
        competitor_3 = st.text_input("Competitor 3 (Name or Website):", help="Enter the name or URL of your third competitor (optional)")
        if st.button("Analyze Competitors"):
            if competitor_1:
                with st.spinner("Analyzing competitors..."):
                    data = {
                        'competitor_1': competitor_1,
                        'competitor_2': competitor_2,
                        'competitor_3': competitor_3
                    }
                    results = make_api_request(DJANGO_COMPETITOR_ANALYSIS_URL, data, competitor_collection, "competitor_analysis")

                    if results:
                        st.markdown("### Competitor Analysis Results "+":material/compare_arrows:")
                        st.markdown(f"#### Business Overview")
                        st.markdown(f"*Competitor 1:* {results.get('competitor_1', 'N/A')}")
                        if results.get('competitor_2'):
                            st.markdown(f"*Competitor 2:* {results['competitor_2']}")
                        if results.get('competitor_3'):
                            st.markdown(f"*Competitor 3:* {results['competitor_3']}")

                        st.markdown("#### Competitor Analysis Summary")
                        st.markdown(f"{results.get('competitor_analysis_result', 'N/A')}")
                    else:
                        st.error("Failed to generate competitor analysis.")
        else:
            st.warning("Please enter at least one competitor.")

    with history_tab:
        show_history(competitor_collection, "competitor_analysis")

def show_news_overview():
    analysis_tab, history_tab = st.tabs(["Analysis", "History"])

    with analysis_tab:
        st.header("Sector News Overview")
        sector = st.text_input("Enter the sector:", help="e.g., 'e-commerce', 'fintech', 'healthcare'")

        if st.button("Get News Overview"):
            if sector:
                with st.spinner("Gathering news and generating overview..."):
                    data = {'sector': sector}
                    results = make_api_request(DJANGO_NEWS_OVERVIEW_URL, data, news_collection, "news_overview")

                    if results:
                        st.markdown("### Sector News Overview "+":material/newspaper:")

                        st.markdown(f"#### Business Overview")
                        st.markdown(f"*Sector:* {results.get('sector', 'N/A')}")
                        st.markdown(f"*Number of Articles:* {results.get('num_articles', 'N/A')}")
                        st.markdown(f"*Sentiment:* {results.get('sentiment_counts', 'N/A')}")
                        st.markdown(f"#### Overview")
                        st.markdown(f"{results.get('news_overview_result', 'N/A')}")
                    else:
                        st.error("Failed to generate news overview.")
        else:
            st.warning("Please enter a sector.")

    with history_tab:
        show_history(news_collection, "news_overview")

    # Main page
def main():
    st.title("Co-Founder App")
    st.write("Welcome to the Co-Founder App! Choose a tool below to get started.")

    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    with col1:
        if st.button("SWOT Analysis", icon = ":material/dashboard:"):
            st.session_state['current_page'] = "swot_analysis"
    with col2:
        if st.button("Market Size Estimation", icon = ":material/search_insights:"):
            st.session_state['current_page'] = "market_size_estimation"
    with col3:
        if st.button("Business Model Recommendation", icon=":material/pie_chart:"):
            st.session_state['current_page'] = "business_model_recommendation"
    with col4:
        if st.button("Competitor Analysis",icon=":material/compare_arrows:"):
            st.session_state['current_page'] = "competitor_analysis"
    with col5:
        if st.button("Sector Outlook", icon = ":material/insights:"):
            st.session_state['current_page'] = "news_overview"

        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = "main"

        if st.session_state['current_page'] == "swot_analysis":
            show_swot_analysis()
        elif st.session_state['current_page'] == "market_size_estimation":
            show_market_size_estimation()
        elif st.session_state['current_page'] == "business_model_recommendation":
            show_business_model_recommendation()
        elif st.session_state['current_page'] == "competitor_analysis":
            show_competitor_analysis()
        elif st.session_state['current_page'] == "news_overview":
            show_news_overview()

if __name__ == "__main__":
    main()