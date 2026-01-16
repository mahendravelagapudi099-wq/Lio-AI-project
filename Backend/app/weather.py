import requests
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
WeatherAPIKey = env_vars.get("WeatherAPIKey")
DefaultLocation = env_vars.get("DEFAULT_WEATHER_LOCATION", "Hyderabad,India")

def GetWeather(location="auto"):
    """
    Fetch current weather for a specific location using Tomorrow.io API.
    """
    if not WeatherAPIKey:
        return "Weather API key is missing. Please add it to the .env file."

    search_location = location if location != "auto" else DefaultLocation
    
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={search_location}&apikey={WeatherAPIKey}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            values = data.get("data", {}).get("values", {})
            temp = values.get("temperature")
            humidity = values.get("humidity")
            wind_speed = values.get("windSpeed")
            
            # Formatting the response
            weather_report = f"The current weather in {search_location} is:\n"
            weather_report += f"- Temperature: {temp}°C\n"
            weather_report += f"- Humidity: {humidity}%\n"
            weather_report += f"- Wind Speed: {wind_speed} m/s"
            
            return weather_report
        else:
            return f"Error fetching weather: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Weather search error: {str(e)}"

def GetForecast(location="auto"):
    """
    Fetch weather forecast for a specific location.
    """
    if not WeatherAPIKey:
        return "Weather API key is missing."

    search_location = location if location != "auto" else DefaultLocation
    
    url = f"https://api.tomorrow.io/v4/weather/forecast?location={search_location}&apikey={WeatherAPIKey}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Simplification: just get the next few hours/days
            timelines = data.get("timelines", {})
            daily = timelines.get("daily", [])
            
            if not daily:
                return "No forecast available."
                
            forecast_report = f"Weather forecast for {search_location}:\n"
            for day in daily[:3]: # Next 3 days
                date = day.get("time", "").split("T")[0]
                values = day.get("values", {})
                temp_avg = values.get("temperatureAvg")
                forecast_report += f"- {date}: {temp_avg}°C average\n"
            
            return forecast_report
        else:
            return f"Error fetching forecast: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Forecast search error: {str(e)}"

if __name__ == "__main__":
    # Test
    print(GetWeather("London"))
    print(GetForecast("London"))
