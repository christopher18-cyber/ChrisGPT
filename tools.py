import os
import requests
import math
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from database import search_memory,save_memory
from rag import retrieve_from_rag


load_dotenv()

CURRENT_THREAD_ID = "default"

def set_current_thread_id(thread_id:str):
    global CURRENT_THREAD_ID
    CURRENT_THREAD_ID = thread_id

web_Search = TavilySearch(
    max_results=3,
    topic="general",
    search_depth="advanced"
)

@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10 * 5
    """
    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def remember_this(memory: str) -> str:
    """
    Save an important user perference or fact into long-term memory.
    Use this when the user asks you for something.
    """

    return save_memory(
        thread_id=CURRENT_THREAD_ID,
        memory=memory
    )

@tool
def search_uploaded_document(query:str)-> str:
    """
    Search uploaded documents for relevant information
    Use this when the user asks about uploaded PDFS, DOCX, TXT, notes, files or documents
    """

    return retrieve_from_rag(
        query=query,
        thread_id= CURRENT_THREAD_ID
    )



@tool
def get_stock_price(symbol: str) -> str:
    """
    Fetch latest stock price for a given symbol (e.g 'AAPL', 'TSLA')
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=DFAY4184HQ44GJOB"
    r = requests.get(url)
    return r.json()

def get_current_weather(location: str) -> dict:
    """
    Fetch real-time weather data for a given location using the Weatherstack API.

    Args:
        location (str): The city name, zip code, latitude/longitude, or IP address.

    Returns:
        dict: A dictionary containing key weather details or an error message.
    """
    api_key = os.getenv("WEATHERSTACK_API_KEY")
    if not api_key:
        return {"error": "WEATHERSTACK_API_KEY environment variable is not set."}

    url = "https://api.weatherstack.com/current"

    params = {
        "access_key": api_key,
        "query": location,
        "units": "m"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "success" in data and data["success"] is False:
            error_info = data.get("error", {})
            return {"error": error_info.get("info", "Unknown Weatherstack API error")}

        current = data.get("current", {})
        loc = data.get("location", {})

        return {
            "location": f"{loc.get('name')}, {loc.get('country')}",
            "temperature_c": current.get("temperature"),
            "condition": current.get("weather_descriptions", [""])[0],
            "humidity": current.get("humidity"),
            "wind_speed_kmh": current.get("wind_speed"),
            "feels_like_c": current.get("feelslike")
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP Request failed: {e}"}


@tool
def recall_memory(query: str) -> str:
    """
    Recall saved long-term memories about the user or this conversation
    """

    return search_memory(
        thread_id=CURRENT_THREAD_ID,
        query=query
    )

tools = [web_Search,
         recall_memory,
         remember_this,
         search_uploaded_document,
         calculator,
         get_stock_price,
         get_current_weather
         ]