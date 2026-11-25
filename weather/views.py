
import os
import requests

from datetime import datetime
from django.shortcuts import render


def weather_home(request):
    weather_data = None
    forecast_data = []
    error = None

    city = request.GET.get('city', '').strip()
    api_key = os.getenv('OPENWEATHER_API_KEY')

    if city:
        if not api_key:
            error = "Weather API key is not configured."
        else:
            current_url = "https://api.openweathermap.org/data/2.5/weather"
            forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric'
            }

            try:
                # Fetch current weather
                current_response = requests.get(
                    current_url,
                    params=params,
                    timeout=10
                )

                if current_response.status_code == 200:
                    data = current_response.json()

                    weather_data = {
                        'city': data['name'],
                        'country': data['sys']['country'],
                        'temperature': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'humidity': data['main']['humidity'],
                        'pressure': data['main']['pressure'],
                        'description': data['weather'][0]['description'],
                        'icon': data['weather'][0]['icon'],
                        'wind_speed': data['wind']['speed'],
                    }

                    # Fetch 5-day forecast
                    forecast_response = requests.get(
                        forecast_url,
                        params=params,
                        timeout=10
                    )

                    if forecast_response.status_code == 200:
                        forecast_json = forecast_response.json()

                        daily_forecasts = {}

                        for item in forecast_json['list']:
                            date = item['dt_txt'].split(' ')[0]
                            hour = int(item['dt_txt'].split(' ')[1][:2])

                            # Keep the forecast closest to 12 noon
                            if (
                                date not in daily_forecasts
                                or abs(hour - 12) <
                                abs(daily_forecasts[date]['hour'] - 12)
                            ):
                                daily_forecasts[date] = {
                                    'hour': hour,
                                    'temperature': item['main']['temp'],
                                    'humidity': item['main']['humidity'],
                                    'description': item['weather'][0]['description'],
                                    'icon': item['weather'][0]['icon'],
                                    'wind_speed': item['wind']['speed'],
                                    'rain': item.get('rain', {}).get('3h', 0),
                                }

                        for date, item in list(daily_forecasts.items())[:5]:
                            forecast_data.append({
                                'date': datetime.strptime(
                                    date, '%Y-%m-%d'
                                ).strftime('%d %b'),
                                'temperature': item['temperature'],
                                'humidity': item['humidity'],
                                'description': item['description'],
                                'icon': item['icon'],
                                'wind_speed': item['wind_speed'],
                                'rain': item['rain'],
                            })

                    else:
                        error = "Current weather loaded, but forecast is unavailable."

                elif current_response.status_code == 404:
                    error = "City not found. Please check the spelling."

                elif current_response.status_code == 401:
                    error = "Invalid API key or API key not activated yet."

                else:
                    error = "Unable to retrieve weather information."

            except requests.RequestException:
                error = "Network error. Please try again."

    return render(request, 'weather/weather.html', {
        'weather_data': weather_data,
        'forecast_data': forecast_data,
        'error': error,
        'city': city,
    })
