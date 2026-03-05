import json
import os
import re
from html import unescape
from typing import Any, Dict, List

import requests
import streamlit as st

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "stepfun/step-3.5-flash:free"


# ---------------- WEATHER TOOL ---------------- #

def weather_code_to_text(code: int) -> str:
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
    }
    return mapping.get(code, f"Weather code {code}")


def get_weather(location: str) -> Dict[str, Any]:

    geocode_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": location, "count": 1},
        timeout=30,
    )
    geocode_resp.raise_for_status()
    geocode_data = geocode_resp.json()

    results = geocode_data.get("results", [])
    if not results:
        return {"error": f"No location found for '{location}'"}

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    forecast_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,weather_code",
        },
        timeout=30,
    )

    forecast_resp.raise_for_status()
    forecast_data = forecast_resp.json()

    current = forecast_data.get("current", {})
    units = forecast_data.get("current_units", {})

    code = current.get("weather_code")

    return {
        "location": {
            "name": place.get("name"),
            "country": place.get("country"),
            "admin1": place.get("admin1"),
            "latitude": latitude,
            "longitude": longitude,
        },
        "current": {
            "temperature": current.get("temperature_2m"),
            "temperature_unit": units.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": units.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_text": weather_code_to_text(code) if isinstance(code, int) else "Unknown",
        },
    }


def handle_get_weather(args: Dict[str, Any]) -> Dict[str, Any]:

    location = str(args.get("location", "")).strip()

    if not location:
        return {"error": "Location missing"}

    try:
        return get_weather(location)
    except requests.RequestException as e:
        return {"error": str(e)}


# ---------------- URL FETCH TOOL ---------------- #

def extract_text_from_html(html: str) -> str:

    clean = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    clean = re.sub(r"(?is)<style.*?>.*?</style>", " ", clean)
    clean = re.sub(r"(?is)<[^>]+>", " ", clean)

    clean = unescape(clean)
    clean = re.sub(r"\s+", " ", clean)

    return clean.strip()


def fetch_url(url: str, max_chars: int = 5000) -> Dict[str, Any]:

    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )

    resp.raise_for_status()

    text = resp.text
    extracted = extract_text_from_html(text)

    return {
        "url": resp.url,
        "status": resp.status_code,
        "content": extracted[:max_chars],
    }


def handle_fetch_url(args: Dict[str, Any]) -> Dict[str, Any]:

    url = str(args.get("url", "")).strip()

    if not url:
        return {"error": "URL missing"}

    try:
        return fetch_url(url)
    except requests.RequestException as e:
        return {"error": str(e)}


# ---------------- TOOL REGISTRY ---------------- #

TOOL_REGISTRY = {
    "get_weather": handle_get_weather,
    "fetch_url": handle_fetch_url,
}


def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:

    if tool_name not in TOOL_REGISTRY:
        return {"error": "Unknown tool"}

    return TOOL_REGISTRY[tool_name](args)


# ---------------- OPENROUTER ---------------- #

def call_openrouter(api_key: str, model: str, messages: List[Dict[str, Any]]):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=90,
    )

    response.raise_for_status()

    return response.json()


# ---------------- STREAMLIT APP ---------------- #

def main():

    st.title("AI Agent with Tools")

    api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Ask something...")

    if prompt:

        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                response = call_openrouter(
                    api_key,
                    DEFAULT_MODEL,
                    st.session_state.messages,
                )

                answer = response["choices"][0]["message"]["content"]

                st.write(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )


if __name__ == "__main__":
    main()