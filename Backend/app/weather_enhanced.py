import requests
import os
from dotenv import dotenv_values
from datetime import datetime, timedelta

env_vars = dotenv_values(".env")
WeatherAPIKey = env_vars.get("WeatherAPIKey")
DefaultLocation = env_vars.get("DEFAULT_WEATHER_LOCATION", "Hyderabad,India")

def get_current_weather(location="auto"):
    """
    Fetch current weather with detailed information.
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
            wind_direction = values.get("windDirection")
            pressure = values.get("pressureSurfaceLevel")
            visibility = values.get("visibility")
            precipitation = values.get("precipitationProbability")
            
            weather_report = f"The current weather in {search_location} is:\n"
            weather_report += f"- Temperature: {temp}°C\n"
            weather_report += f"- Humidity: {humidity}%\n"
            weather_report += f"- Wind: {wind_speed} m/s from {wind_direction}°\n"
            weather_report += f"- Pressure: {pressure} hPa\n"
            weather_report += f"- Visibility: {visibility} km\n"
            weather_report += f"- Precipitation: {precipitation}%\n"
            
            return weather_report
        else:
            return f"Error fetching weather: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Weather search error: {str(e)}"

def get_weather_forecast(location="auto", days=7):
    """
    Fetch detailed weather forecast for specified number of days.
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
            timelines = data.get("timelines", {})
            daily = timelines.get("daily", [])
            
            if not daily:
                return "No forecast available."
                
            forecast_report = f"Weather forecast for {search_location} ({days} days):\n"
            for day in daily[:days]:
                date = day.get("time", "").split("T")[0]
                values = day.get("values", {})
                temp_min = values.get("temperatureMin")
                temp_max = values.get("temperatureMax")
                humidity = values.get("humidityAvg")
                wind_speed = values.get("windSpeedAvg")
                precipitation = values.get("precipitationProbabilityAvg")
                
                forecast_report += (
                    f"- {date}: {temp_min}°C - {temp_max}°C\n"
                    f"  Humidity: {humidity}%, Wind: {wind_speed} m/s, Precipitation: {precipitation}%\n"
                )
            
            return forecast_report
        else:
            return f"Error fetching forecast: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Forecast search error: {str(e)}"

def get_hourly_forecast(location="auto", hours=24):
    """
    Fetch hourly weather forecast.
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
            timelines = data.get("timelines", {})
            hourly = timelines.get("hourly", [])
            
            if not hourly:
                return "No hourly forecast available."
                
            forecast_report = f"Hourly weather forecast for {search_location} ({hours} hours):\n"
            for hour in hourly[:hours]:
                time_str = hour.get("time", "")
                time_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                hour_str = time_obj.strftime("%H:%M")
                values = hour.get("values", {})
                temp = values.get("temperature")
                humidity = values.get("humidity")
                precipitation = values.get("precipitationProbability")
                
                forecast_report += (
                    f"- {hour_str}: {temp}°C, {humidity}%, Precipitation: {precipitation}%\n"
                )
            
            return forecast_report
        else:
            return f"Error fetching hourly forecast: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Hourly forecast error: {str(e)}"

def get_weather_alerts(location="auto"):
    """
    Get weather alerts and warnings for a location.
    """
    if not WeatherAPIKey:
        return "Weather API key is missing."

    search_location = location if location != "auto" else DefaultLocation
    
    # Note: This endpoint might require different API endpoint or parameters
    url = f"https://api.tomorrow.io/v4/weather/alerts?location={search_location}&apikey={WeatherAPIKey}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            alerts = data.get("alerts", [])
            
            if not alerts:
                return "No weather alerts currently active."
                
            alert_report = f"Weather alerts for {search_location}:\n"
            for alert in alerts:
                alert_report += (
                    f"- {alert.get('event')}\n"
                    f"  {alert.get('description')}\n"
                    f"  Effective: {alert.get('effective')} to {alert.get('expires')}\n"
                )
            
            return alert_report
        else:
            return f"Error fetching weather alerts: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Weather alerts error: {str(e)}"

def get_weather_summary(location="auto"):
    """
    Get comprehensive weather summary including current conditions and forecast.
    """
    current = get_current_weather(location)
    forecast = get_weather_forecast(location, 3)  # 3-day forecast
    alerts = get_weather_alerts(location)
    
    return (
        f"{current}\n"
        f"\n{forecast}\n"
        f"\n{alerts}"
    )

def is_raining(location="auto"):
    """Check if it's currently raining at a location."""
    if not WeatherAPIKey:
        return False

    search_location = location if location != "auto" else DefaultLocation
    
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={search_location}&apikey={WeatherAPIKey}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            values = data.get("data", {}).get("values", {})
            precipitation = values.get("precipitationProbability")
            return precipitation > 50
        return False
    except Exception:
        return False

def get_uv_index(location="auto"):
    """Get current UV index information."""
    if not WeatherAPIKey:
        return "Weather API key is missing."

    search_location = location if location != "auto" else DefaultLocation
    
    url = f"https://api.tomorrow.io/v4/weather/realtime?location={search_location}&apikey={WeatherAPIKey}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            values = data.get("data", {}).get("values", {})
            uv_index = values.get("uvIndex")
            
            if uv_index is None:
                return "UV index information not available"
                
            uv_level = "Low"
            if uv_index >= 11:
                uv_level = "Extreme"
            elif uv_index >= 8:
                uv_level = "Very High"
            elif uv_index >= 6:
                uv_level = "High"
            elif uv_index >= 3:
                uv_level = "Moderate"
                
            return f"UV Index: {uv_index} ({uv_level})"
        return "UV index information not available"
    except Exception as e:
        return f"UV index error: {str(e)}"

if __name__ == "__main__":
    print("Testing Enhanced Weather Functions...")
    
    print("\n1. Current Weather:")
    print(get_current_weather("London"))
    
    print("\n2. 3-Day Forecast:")
    print(get_weather_forecast("London", 3))
    
    print("\n3. 6-Hour Forecast:")
    print(get_hourly_forecast("London", 6))
    
    print("\n4. Weather Alerts:")
    print(get_weather_alerts("London"))
    
    print("\n5. UV Index:")
    print(get_uv_index("London"))
    
    print("\n6. Is it Raining?")
    print(is_raining("London"))
