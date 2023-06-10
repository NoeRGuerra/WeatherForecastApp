import datetime
import requests_mock
import unittest
import sys
import os

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project root) by going up one level
project_root = os.path.dirname(current_dir)

# Add the project root to the Python path
sys.path.insert(0, project_root)


from weather_app import get_weather_data, get_forecast_data, get_max_min_temp, validate_coordinates

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?"


class TestWeatherApp(unittest.TestCase):
    def test_get_weather_data(self):
        latitude = 40.7128
        longitude = 74.0060
        try:
            data = get_weather_data(latitude, longitude)
            self.assertIsInstance(data, dict)
        except Exception:
            self.fail('Failed to retrieve weather data')

        latitude = 100.0
        longitude = -200.0
        with self.assertRaises(ValueError):
            get_weather_data(latitude, longitude)

        latitude = 40.7128
        longitude = -74.0060
        # Simulate an API error response
        with requests_mock.Mocker() as mocker:
            mocker.get(OPENWEATHER_BASE_URL, status_code=401)
            with self.assertRaises(Exception):
                get_weather_data(latitude, longitude)

    def test_get_forecast_data(self):
        latitude = 40.7128
        longitude = 74.0060
        try:
            data = get_forecast_data(latitude, longitude)
            self.assertIsInstance(data, dict)
        except Exception:
            self.fail('Failed to retrieve weather data')

        latitude = 100.0
        longitude = -200.0
        with self.assertRaises(ValueError):
            get_forecast_data(latitude, longitude)

        latitude = 40.7128
        longitude = -74.0060
        # Simulate an API error response
        with requests_mock.Mocker() as mocker:
            mocker.get(OPENWEATHER_BASE_URL, status_code=401)
            with self.assertRaises(Exception):
                get_forecast_data(latitude, longitude)

    def test_get_max_min_temp(self):
        # Mock forecast data
        forecast_data = {
            'list': [
                {'dt': 1685977200, 'main': {'temp': -1.54}, # datetime.datetime(2023, 6, 5, 11, 0)
                    'weather': [{'icon': '13n'}]},
                {'dt': 1685988000, 'main': {'temp': -1.87}, # datetime.datetime(2023, 6, 5, 14, 0)
                    'weather': [{'icon': '04n'}]},
                {'dt': 1622440000, 'main': {'temp': 30}, # datetime.datetime(2021, 5, 31, 1, 46, 40)
                    'weather': [{'icon': '02d'}]},
                {'dt': 1622450000, 'main': {'temp': 28}, # datetime.datetime(2021, 5, 31, 4, 33, 20)
                    'weather': [{'icon': '03d'}]},
                {'dt': 1622460000, 'main': {'temp': 20}, #  datetime.datetime(2021, 5, 31, 7, 20)
                    'weather': [{'icon': '04d'}]},
            ]
        }

        # Call the function to get the result
        result = get_max_min_temp(forecast_data)

        # Assert the expected output
        expected_result = {
            datetime.date(2023, 6, 5): {'max_temp': -2, 'min_temp': -2, 'icon': 'snow'},
            datetime.date(2021, 5, 31): {'max_temp': 30, 'min_temp': 20, 'icon': 'cloudy'}
        }
        self.assertEqual(result, expected_result)

    def test_validate_coordinates(self):
        latitude = 40.7128
        longitude = 74.0060

        result = validate_coordinates(latitude, longitude)
        self.assertTrue(result)

        latitude = 100
        longitude = -74.0060
        
        result = validate_coordinates(latitude, longitude)
        self.assertFalse(result)

        latitude = "a"
        longitude = 32.4213

        with self.assertRaises(TypeError):
            result = validate_coordinates(latitude, longitude)



if __name__ == '__main__':
    unittest.main()
