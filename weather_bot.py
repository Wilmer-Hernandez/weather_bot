import requests
import pycountry
import os
from dotenv import load_dotenv


class WeatherBot:
    '''
    WeatherBot:
        class represents a bot that retrieves and displays weather information.
    http://api.openweathermap.org/geo/1.0/direct?q=gainesville,ga,us&limit=1&appid=9f4ec0d8b781f45ba6b26d7c23db81dc
    '''
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    GEOCODINGAPI = "http://api.openweathermap.org/geo/1.0/direct?q="
    CURRENTWEATHERAPI = "https://api.openweathermap.org/data/2.5/weather?"

    def __init__(self, city_name: str, country_code: str, state_name: str):
        '''
        Initializes a new instance of the WeatherBot class.
        '''
        self._city_name = city_name
        self._country_code = country_code
        self._state_name = state_name

    def make_api_request(self, url: str) -> dict:
        '''
        Makes an API request and returns the response as JSON.
        '''
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(
                f"HTTP error occurred: {str(e)}"
            )

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the API request: {str(e)}")

        except ValueError as e:
            print(
                f"An error occurred while parsing the API response: {str(e)}"
            )

    def validate_country_code(self):
        '''
        Validates the country code
        '''
        try:
            pycountry.countries.get(alpha_2=self._country_code)
        except LookupError:
            raise Exception("Invalid country code")

    def validate_state_name(self):
        '''
        Validates state name in the United States
        '''
        if self._country_code == 'US':
            try:
                pycountry.subdivisions.get(code=f"US-{self._state_name}")
            except LookupError:
                raise Exception("Invalid state name")

    def location(self) -> tuple:
        '''
        Retrieves the latitude and longitude coordinates for the location.
        '''

        if self._state_name == '' or self._country_code != 'US':
            url = (
                f"{WeatherBot.GEOCODINGAPI}{self._city_name},"
                f"{self._country_code}&limit=1&appid={WeatherBot.API_KEY}"
            )
        else:
            url = (
                f"{WeatherBot.GEOCODINGAPI}{self._city_name},"
                f"{self._state_name},{self._country_code}"
                f"&limit=1&appid={WeatherBot.API_KEY}"
            )

        response_data = self.make_api_request(url)

        if response_data:
            latitude = response_data[0]['lat']
            longitude = response_data[0]['lon']
            return latitude, longitude

        raise Exception(
            "Location data not found for the provided city, country, "
            "and/or state"
        )

    def current_weather(
            self, lat: float, lon: float, unit_system: str
    ) -> dict:
        '''
        Retrieves the current weather information.
        '''
        if unit_system == 'metric':
            units = f"&units={unit_system}"
            temperature_unit = "°C"
            speed_unit = "km/h"
        else:
            units = f'&units={unit_system}'
            temperature_unit = "°F"
            speed_unit = "mph"

        url = (
            f"{WeatherBot.CURRENTWEATHERAPI}lat={lat}&lon={lon}"
            f"&appid={WeatherBot.API_KEY}{units}"
        )

        response_data = self.make_api_request(url)

        if response_data:
            return {
                "description": response_data["weather"][0]["description"],
                "temp": response_data["main"]["temp"],
                "feels_like": response_data["main"]["feels_like"],
                "temperature_unit": temperature_unit,
                "humidity": response_data["main"]["humidity"],
                "wind_speed": response_data["wind"]["speed"],
                "speed_unit": speed_unit
            }

    def print_weather(self, weather_data: dict):
        '''
        Prints the weather information to the console.
        '''
        if self._state_name == "" or self._country_code != "US":
            temperature_unit = "°C"
            speed_unit = "km/h"
        else:
            temperature_unit = "°F"
            speed_unit = "mph"

        print("")
        print(f"Weather condition: {weather_data['description']}")
        print(f"Temperature: {weather_data['temp']}{temperature_unit}")
        print(f"Feels like: {weather_data['feels_like']}{temperature_unit}")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind: {weather_data['wind_speed']} {speed_unit}")


def main():
    '''
    Entry point of the program
    Message to programmer: change code to accomodate new current
    weather function
    '''
    print('Weather Bot')
    while True:
        print(
            'For weather of any place, please enter the following information'
        )

        try:
            city_name = input("City name: ")
            state_name = ''
            country_code = input("Country code (e.g., US, GB): ").upper()

            if country_code == 'US':
                state_name = input("State name: ")

            weather_bot = WeatherBot(city_name, country_code, state_name)

            latitude, longitude = weather_bot.location()

            current_weather = weather_bot.current_weather(
                latitude, longitude, "imperial"
            )
            if current_weather:
                weather_bot.print_weather(current_weather)
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

        while True:
            exit_or_continue = input(
                'To continue, press C. To exit, press E: '
            )

            if (exit_or_continue.lower() == 'c' or
                    exit_or_continue.lower() == 'e'):
                break

            else:
                print("Invalid input. To continue, press C. To exit, press E.")

        if exit_or_continue.lower() == 'e':
            break


if __name__ == '__main__':
    main()
