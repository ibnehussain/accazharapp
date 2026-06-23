import os
import time
import requests
from flask import Flask, jsonify, render_template, request, send_from_directory

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')
OPENWEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Realistic mock data for testing without a live API key.
# Remove or set USE_MOCK_DATA=false to use the real OpenWeatherMap API.
USE_MOCK_DATA = os.environ.get('USE_MOCK_DATA', 'true').lower() == 'true'
CACHE_TTL_SECONDS = int(os.environ.get('WEATHER_CACHE_TTL_SECONDS', '300'))

WEATHER_CACHE = {}

MOCK_WEATHER = {
    'london': {
        'city': 'London', 'country': 'GB',
        'temp': 14.2, 'feels_like': 12.8, 'humidity': 78,
        'description': 'overcast clouds', 'condition_code': 804,
        'wind_speed': 5.1, 'visibility': 9.0,
    },
    'new york': {
        'city': 'New York', 'country': 'US',
        'temp': 27.5, 'feels_like': 29.1, 'humidity': 62,
        'description': 'few clouds', 'condition_code': 801,
        'wind_speed': 3.6, 'visibility': 10.0,
    },
    'tokyo': {
        'city': 'Tokyo', 'country': 'JP',
        'temp': 31.0, 'feels_like': 34.2, 'humidity': 85,
        'description': 'light rain', 'condition_code': 500,
        'wind_speed': 2.3, 'visibility': 6.5,
    },
    'sydney': {
        'city': 'Sydney', 'country': 'AU',
        'temp': 18.7, 'feels_like': 17.9, 'humidity': 55,
        'description': 'clear sky', 'condition_code': 800,
        'wind_speed': 4.8, 'visibility': 10.0,
    },
    'dubai': {
        'city': 'Dubai', 'country': 'AE',
        'temp': 41.3, 'feels_like': 44.0, 'humidity': 30,
        'description': 'sunny', 'condition_code': 800,
        'wind_speed': 6.2, 'visibility': 10.0,
    },
    'paris': {
        'city': 'Paris', 'country': 'FR',
        'temp': 22.4, 'feels_like': 21.8, 'humidity': 60,
        'description': 'scattered clouds', 'condition_code': 802,
        'wind_speed': 3.1, 'visibility': 10.0,
    },
    'moscow': {
        'city': 'Moscow', 'country': 'RU',
        'temp': -5.2, 'feels_like': -9.8, 'humidity': 88,
        'description': 'heavy snow', 'condition_code': 602,
        'wind_speed': 7.4, 'visibility': 3.0,
    },
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/style.css')
def serve_css():
    return send_from_directory(app.root_path, 'style.css')


def cache_key(city):
    return city.strip().lower()


def get_cached_weather(city):
    key = cache_key(city)
    cached = WEATHER_CACHE.get(key)
    if not cached:
        return None

    if time.time() - cached['timestamp'] > CACHE_TTL_SECONDS:
        WEATHER_CACHE.pop(key, None)
        return None

    return cached['data']


def store_cached_weather(city, data):
    WEATHER_CACHE[cache_key(city)] = {
        'timestamp': time.time(),
        'data': data,
    }


@app.route('/weather')
def weather():
    city = request.args.get('city', '').strip()

    if not city:
        return jsonify({'error': 'City name is required.'}), 400

    cached = get_cached_weather(city)
    if cached:
        response = jsonify(cached)
        response.headers['X-Weather-Cache'] = 'HIT'
        return response

    if USE_MOCK_DATA:
        mock = MOCK_WEATHER.get(city.lower())
        if mock:
            store_cached_weather(city, mock)
            response = jsonify(mock)
            response.headers['X-Weather-Cache'] = 'MISS'
            return response
        return jsonify({'error': f'City "{city}" not found in mock data. Try: London, New York, Tokyo, Sydney, Dubai, Paris, Moscow.'}), 404

    try:
        response = requests.get(OPENWEATHER_URL, params={
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
        }, timeout=5)

        if response.status_code == 404:
            return jsonify({'error': f'City "{city}" not found. Please check the spelling and try again.'}), 404

        if response.status_code == 401:
            return jsonify({'error': 'Invalid API key. Check your OPENWEATHER_API_KEY environment variable.'}), 401

        response.raise_for_status()
        raw = response.json()

        data = {
            'city':           raw['name'],
            'country':        raw['sys']['country'],
            'temp':           raw['main']['temp'],
            'feels_like':     raw['main']['feels_like'],
            'humidity':       raw['main']['humidity'],
            'description':    raw['weather'][0]['description'],
            'condition_code': raw['weather'][0]['id'],
            'wind_speed':     raw['wind']['speed'],
            'visibility':     round(raw.get('visibility', 0) / 1000, 1),
        }
        store_cached_weather(city, data)
        response = jsonify(data)
        response.headers['X-Weather-Cache'] = 'MISS'
        return response

    except requests.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except requests.RequestException:
        return jsonify({'error': 'Failed to fetch weather data. Please try again later.'}), 502


if __name__ == '__main__':
    app.run(debug=True)
