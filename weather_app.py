from typing import Tuple, Union
from flask import Flask, render_template, url_for
import requests
import config
import datetime

## TODO:
## - Add double click on city's name to change city or zip code
## - Call geolocations API to try to get user's location

app = Flask(__name__)
OPENWEATHER_API_KEY = config.OPENWEATHER_API_KEY
ZIP_API_KEY = config.ZIP_API_KEY
ZIP_BASE_URL = "https://thezipcodes.com/api/v1/search?"
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


@app.route("/")
def home():
    """
    Returns the current weather information and a five-day forecast for a specified zip code and country code.

    The function first retrieves the latitude and longitude coordinates for the provided zip code and country code, 
    then uses those coordinates to retrieve the current weather information and five-day forecast from the OpenWeatherMap API. 

    :return: A rendered HTML template containing the current temperature, weather description, city name, and an icon representing the current weather condition, as well as a table of maximum and minimum temperatures with corresponding icons for each day of the five-day forecast.
    :rtype: str

    :raises: Exception: If the zip code or country code is invalid or cannot be found in the OpenWeatherMap database.
    """
    zip_code = 28027
    country_code = "US"
    latitude, longitude = get_coordinates(zip_code, country_code)

    weather_data = get_weather_data(latitude, longitude)
    temperature = round(weather_data['main']['temp'])
    description = weather_data['weather'][0]['description'].capitalize()

    city = weather_data['name']
    icon = weather_data['weather'][0]['icon']
    icon_url = url_for('static', filename=f'icons/{icon_filenames[icon]}.svg')

    forecast_data = get_forecast_data(latitude, longitude)
    weather_by_date = get_max_min_temp(forecast_data)

    return render_template('weather.html', temperature=temperature, description=description, city=city, icon_url=icon_url, weather_by_date=weather_by_date)


def get_coordinates(zip_code: Union[int, str], country_code: str) -> Tuple[float, float]:
    """
    Retrieves the latitude and longitude coordinates for a given zip code and country code using the TheZipCodes.com API.

    The function constructs a URL using the provided zip code and country code, and sends a GET request to the TheZipCodes.com API 
    to retrieve the corresponding latitude and longitude coordinates. The coordinates are then returned as a tuple.

    :param zip_code: A string or integer representing the zip code to retrieve coordinates for.
    :param country_code: A string representing the country code to retrieve coordinates for.
    :return: A tuple containing the latitude and longitude coordinates corresponding to the provided zip code and country code.

    :raises: Exception: If the zip code or country code is invalid or cannot be found in the TheZipCodes.com database.
    """
    URL = f"{ZIP_BASE_URL}zipCode={zip_code}&countryCode={country_code}&apiKey={ZIP_API_KEY}"
    response = requests.get(URL)
    response_json = response.json()
    latitude = response_json['location'][0]['latitude']
    longitude = response_json['location'][0]['longitude']
    return latitude, longitude


def get_weather_data(latitude : float, longitude : float) -> dict:
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
    URL = f"{OPENWEATHER_BASE_URL}lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(URL)
    return response.json()


def get_forecast_data(latitude : float, longitude : float) -> dict:
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
    forecast_url = f"{OPENWEATHER_FORECAST_URL}lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    forecast_data = requests.get(forecast_url)
    return forecast_data.json()


def get_max_min_temp(forecast_data : dict) -> dict:
    """
    Calculate the maximum and minimum temperature for each day from the provided forecast data.

    :param forecast_data: A dictionary containing weather forecast data.
    :type forecast_data: dict
    :return: A dictionary with the maximum and minimum temperature and the corresponding weather icon for each day.
    :rtype: dict
    """
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
        icon = temps_icons['icons'][0]
        icon = icon_filenames[icon]
        temp_by_date[date] = {'max_temp': max_temp,
                              'min_temp': min_temp, 'icon': icon}
    return temp_by_date


if __name__ == "__main__":
    app.run(debug=True)
