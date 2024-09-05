from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import random
from datetime import datetime, timedelta
from openpyxl import load_workbook

app = Flask(__name__)
CORS(app)

WEATHERAPI_KEY = "91505f7efd4b494eb66191358240509"  # Replace with your actual API key
CACHE_FILE = 'weather_cache.json'
CACHE_DURATION = timedelta(hours=1)

def load_city_data():
    """Loads city data from the Excel file."""
    cities = {}
    try:
        workbook = load_workbook('palestine_cities.xlsx')
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            city_name = row[0]
            cities[city_name.lower()] = {
                'city': city_name,
                'location_ar': row[1],
                'land_area': row[2],
                'population': row[3],
                'latitude': row[4],
                'longitude': row[5],
                'population_density': row[6]
            }
    except FileNotFoundError:
        print("Error: palestine_cities.xlsx not found.")
    except Exception as e:
        print(f"Error loading city data: {e}")
    return cities

def load_weather_cache():
    """Loads weather data from the cache file."""
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}
    return cache

def save_weather_cache(cache):
    """Saves weather data to the cache file."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def fetch_weather_data(city_name, latitude, longitude):
    """Fetches weather data from WeatherAPI."""
    print(f"Fetching weather for {city_name} ({latitude}, {longitude})")
    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": WEATHERAPI_KEY,
        "q": f"{latitude},{longitude}",
        "days": 1,
        "aqi": "no"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching weather: {response.status_code}")
        return None

def get_weather(city_name, latitude, longitude):
    """Gets weather data, using cache if available."""
    cache = load_weather_cache()
    cache_key = f"{city_name}_{latitude}_{longitude}"
    now = datetime.now()

    if cache_key in cache and now - datetime.fromisoformat(cache[cache_key]['timestamp']) < CACHE_DURATION:
        print("Loading weather from cache")
        return cache[cache_key]['weather']
    else:
        print("Fetching new weather data")
        weather_data = fetch_weather_data(city_name, latitude, longitude)
        if weather_data:
            cache[cache_key] = {'weather': weather_data, 'timestamp': now.isoformat()}
            save_weather_cache(cache)
            return weather_data
        else:
            return None

@app.route('/api/cities')
def get_cities():
    """Returns a list of available city names."""
    cities = load_city_data()
    return jsonify(sorted(cities.keys()))

@app.route('/api/city/<city_name>')
def get_city_info(city_name):
    """Returns city information and weather data."""
    city_name = city_name.lower()
    cities = load_city_data()

    if city_name in cities:
        city_info = cities[city_name]
        weather_data = get_weather(city_name, city_info['latitude'], city_info['longitude'])

        if weather_data:
            city_info['weather'] = weather_data
            return jsonify(city_info)
        else:
            return jsonify({'error': 'Weather data not available'}), 500
    else:
        return jsonify({'error': 'City not found'}), 404

@app.route('/api/predict', methods=['POST'])
def predict():
    """Returns a random prediction for the given city."""
    data = request.get_json()
    city_name = data.get('city', '').lower()
    if city_name:
        prediction = random.random() 
        return jsonify({'prediction': prediction})
    else:
        return jsonify({'error': 'City name is required'}), 400

if __name__ == '__main__':
    app.run(debug=True)