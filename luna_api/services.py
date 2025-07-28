# File: luna_api/services.py

import os
import random
import requests
from fastapi import HTTPException

def generate_weather_recommendation(city: str) -> str:
    """
    Fetches weather and generates a personalized, sassy outfit recommendation.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(weather_url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"'{city}'? Never heard of it. Check the spelling?")

    weather = response.json()
    temp = weather['main']['temp']
    condition = weather['weather'][0]['main'].lower()

    # L.U.N.A.'s Personality Logic
    if temp > 25:
        outfit = random.choice(["some shorts and a light top", "a breezy sundress", "your favorite tank top"])
        comment = random.choice(["Don't forget sunscreen!", "Stay hydrated out there, superstar.", "Go enjoy that sunshine!"])
    elif 15 < temp <= 25:
        outfit = random.choice(["jeans and a comfy shirt", "a light sweater", "your go-to casual look"])
        comment = random.choice(["Perfect weather to get things done.", "A great day to be you.", "Just right."])
    else:
        outfit = random.choice(["a cozy sweater and a jacket", "something warm and layered", "your favorite hoodie"])
        comment = random.choice(["Brr, stay warm!", "Perfect weather for a warm drink.", "Don't let the chill win."])

    greeting = random.choice(["Alright, let's see...", "Okay, fashion report time!", "Heads up!"])

    return f"{greeting} The forecast for {city} is {temp}°C with {condition}. I'd go with {outfit}. {comment}"