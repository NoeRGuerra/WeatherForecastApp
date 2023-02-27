from flask import Flask, render_template, url_for
import requests
import config
import datetime

app = Flask(__name__)
OPENWEATHER_API_KEY = config.OPENWEATHER_API_KEY
ZIP_API_KEY = config.ZIP_API_KEY
ZIP_BASE_URL = "https://thezipcodes.com/api/v1/search?"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"

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
    weather_by_date = get_max_min_temp(forecast_data) # Get max and min temperatures for each day with icons

    return render_template('weather.html', temperature=temperature, description=description, city=city, icon_url=icon_url, weather_by_date=weather_by_date)



def get_coordinates(zip_code, country_code):
    URL = f"{ZIP_BASE_URL}zipCode={zip_code}&countryCode={country_code}&apiKey={ZIP_API_KEY}"
    response = requests.get(URL)
    response_json = response.json()
    latitude = response_json['location'][0]['latitude']
    longitude = response_json['location'][0]['longitude']
    return latitude, longitude


def get_weather_data(latitude, longitude):
    URL = f"{OPENWEATHER_BASE_URL}lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(URL)
    return response.json()


def get_forecast_data(latitude, longitude):
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric"
    forecast_data = requests.get(forecast_url)
    return forecast_data.json()

def get_max_min_temp(forecast_data):
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
        temp_by_date[date] = {'max_temp': max_temp, 'min_temp': min_temp, 'icon': icon}
    return temp_by_date


if __name__ == "__main__":
    app.run(debug=True)
