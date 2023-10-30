from flask import Flask, render_template, url_for, redirect, request
import requests
import datetime
import pycountry
from pathlib import Path
from dotenv import dotenv_values

app = Flask(__name__)
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?"

icon_filenames = {"01d": "clear",
                  "01n": "nt_clear",
                  "02d": "cloudy",
                  "02n": "cloudy",
                  "03d": "cloudy",
                  "03n": "cloudy",
                  "04d": "cloudy",
                  "04n": "cloudy",
                  "09d": "chancerain",
                  "09n": "chancerain",
                  "10d": "rain",
                  "10n": "rain",
                  "11d": "tstorms",
                  "11n": "tstorms",
                  "13d": "snow",
                  "13n": "snow",
                  "50d": "fog",
                  "50n": "fog", }


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        api_key = request.form['api_key']
        create_env_file(api_key)
    
    api_key = read_api_key()
    if not api_key:
        return redirect(url_for('validate_api_key'))
    
    country_codes = {}
    for country in pycountry.countries:
        country_codes[country.alpha_2] = country.name
    return render_template('zipcode.html', country_codes=sorted(country_codes.items(), key=lambda x: x[1]))

@app.route("/get_api_key")
def validate_api_key():
    filepath = Path(__file__).parent / '.env'
    if filepath.exists():
        env_vars = dotenv_values(filepath)
        if 'OPENWEATHER_API_KEY' in env_vars:
            return redirect(url_for('/'))
    return render_template('index.html')

@app.route("/weather/lat=<float(signed=True):lat>&lon=<float(signed=True):lon>")
def weather(lat, lon):
    """
    Returns the current weather information and a five-day forecast for a specified zip code and country code.

    The function first retrieves the latitude and longitude coordinates for the provided zip code and country code, 
    then uses those coordinates to retrieve the current weather information and five-day forecast from the OpenWeatherMap API. 

    :return: A rendered HTML template containing the current temperature, weather description, city name, and an icon representing the current weather condition, as well as a table of maximum and minimum temperatures with corresponding icons for each day of the five-day forecast.
    :rtype: str

    :raises: Exception: If the zip code or country code is invalid or cannot be found in the OpenWeatherMap database.
    """
    try:
        if not validate_coordinates(lat, lon):
            raise ValueError
    except ValueError:
        return render_template('error.html', error_message='An error occurred while retrieving weather data')

    weather_data = get_weather_data(lat, lon)
    temperature = round(weather_data['main']['temp'])
    description = weather_data['weather'][0]['description'].capitalize()

    city = weather_data['name']
    icon = weather_data['weather'][0]['icon']
    icon_url = url_for('static', filename=f'icons/{icon_filenames[icon]}.svg')

    forecast_data = get_forecast_data(lat, lon)
    weather_by_date = get_max_min_temp(forecast_data)

    return render_template('weather.html', temperature=temperature, description=description, city=city, icon_url=icon_url, weather_by_date=weather_by_date)


def get_weather_data(latitude: float, longitude: float) -> dict:
    """
    Retrieve weather data from the OpenWeatherMap API for a given latitude and longitude.

    Given a latitude and longitude, the function constructs a URL and sends a GET request to the OpenWeatherMap API
    to retrieve the current weather data for the corresponding location. The weather data is returned as a JSON
    dictionary.

    :param latitude: A float representing the latitude of the location to retrieve weather data for.
    :param longitude: A float representing the longitude of the location to retrieve weather data for.
    :return: A dictionary containing weather data for the specified location.
    :raises: Exception: If the request to the OpenWeatherMap API fails or if the latitude or longitude are invalid.
    """
    if not validate_coordinates(latitude, longitude):
        raise ValueError('Invalid latitude or longitude values.')

    OPENWEATHER_API_KEY = read_api_key()
    URL = f"{OPENWEATHER_BASE_URL}lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(URL)
    response.raise_for_status()  # Raise an exception for non-2xx status codes
    data = response.json()
    
    if 'cod' in data and int(data['cod']) != 200:
        # Handle specific API error response
        raise Exception("Error: " + data['message'])
    return data


def get_forecast_data(latitude: float, longitude: float) -> dict:
    """
    Retrieve weather forecast data from the OpenWeatherMap API for a given latitude and longitude.

    Given a latitude and longitude, the function constructs a URL and sends a GET request to the OpenWeatherMap API
    to retrieve the weather forecast data for the corresponding location. The forecast data is returned as a JSON
    dictionary.

    :param latitude: A float representing the latitude of the location to retrieve forecast data for.
    :param longitude: A float representing the longitude of the location to retrieve forecast data for.
    :return: A dictionary containing forecast data for the specified location.
    :raises: Exception: If the request to the OpenWeatherMap API fails or if the latitude or longitude are invalid.
    """
    if not validate_coordinates(latitude, longitude):
        raise ValueError('Invalid latitude or longitude values.')

    OPENWEATHER_API_KEY = read_api_key()
    forecast_url = f"{OPENWEATHER_FORECAST_URL}lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(forecast_url)
    response.raise_for_status()  # Raise an exception for non-2xx status codes
    data = response.json()
    
    if 'cod' in data and int(data['cod']) != 200:
        # Handle specific API error response
        raise Exception(f'Error: {data["message"]}')
    return data


def get_max_min_temp(forecast_data: dict) -> dict:
    """
    Calculate the maximum and minimum temperature for each day from the provided forecast data.

    :param forecast_data: A dictionary containing weather forecast data.
    :type forecast_data: dict
    :return: A dictionary with the maximum and minimum temperature and the corresponding weather icon for each day.
    :rtype: dict
    """
    def most_common_icon(icons):
        items = {}
        for item in icons:
            if item in items:
                items[item] += 1
            else:
                items[item] = 1
        # Return the sorted items with a daytime icon as first item if possible
        sorted_items = sorted(items.items(), key=lambda item: (item[0][-1] != 'd', -item[1])) 
        return sorted_items[0][0]
        
    temp_by_date = {}
    for item in forecast_data['list']:
        dt = datetime.datetime.fromtimestamp(item['dt'])
        date = dt.date()
        icon = item['weather'][0]['icon']
        if date not in temp_by_date:
            temp_by_date[date] = {'temps': [], 'icons': []}
        temp_by_date[date]['temps'].append(item['main']['temp'])
        temp_by_date[date]['icons'].append(icon)

    # Loop through the dictionary to calculate the max and min temperature for each day
    for date, temps_icons in temp_by_date.items():
        max_temp = round(max(temps_icons['temps']))
        min_temp = round(min(temps_icons['temps']))
        icon = most_common_icon(temps_icons['icons'])
        icon = icon_filenames[icon]
        temp_by_date[date] = {'max_temp': max_temp,
                              'min_temp': min_temp, 'icon': icon}
    return temp_by_date


def validate_coordinates(latitude: float, longitude: float) -> None:
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise TypeError(f"Expected 'latitude' and 'longitude' to be a number, but received '{type(latitude).__name__}' for latitude and '{type(longitude).__name__}' for longitude.")
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return False
    return True

def create_env_file(api_key):
    with open('.env', 'w') as f:
        f.write(f'OPENWEATHER_API_KEY={api_key}\n')

def read_api_key():
    env_vars = dotenv_values('.env')
    api_key = env_vars.get('OPENWEATHER_API_KEY')
    return api_key

if __name__ == "__main__":
    app.run(debug=True)
