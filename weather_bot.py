import requests

API_KEY = "9f4ec0d8b781f45ba6b26d7c23db81dc"
GEOCODINGAPI = "http://api.openweathermap.org/geo/1.0/direct?q="
CURRENTWEATHERAPI = "https://api.openweathermap.org/data/2.5/weather?"


class WeatherBot:
    def __init__(self, city_name: str, country_code: str, state_name: str):
        self._city_name = city_name
        self._country_code = country_code
        self._state_name = state_name

    def make_api_request(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("An error occurred during the API request:", str(e))

    def location(self):
        if self._state_name == '' or self._country_code != 'US':
            url = (
                f"{GEOCODINGAPI}{self._city_name},{self._country_code}"
                f"&limit=1&appid={API_KEY}"
            )
        else:
            url = (
                f"{GEOCODINGAPI}{self._city_name},{self._state_name},"
                f"{self._country_code}&limit=5&appid={API_KEY}"
            )

        response_data = self.make_api_request(url)

        if response_data:
            latitude = response_data[0]['lat']
            longitude = response_data[0]['lon']
            return latitude, longitude

    def current_weather(self, lat: float, lon: float):
        if self._state_name == '' or self._country_code != 'US':
            units = "&units=metric"
        else:
            units = ''

        url = (
            f"{CURRENTWEATHERAPI}lat={lat}&lon={lon}&appid={API_KEY}"
            f"{units}"
        )

        response_data = self.make_api_request(url)

        if response_data:
            return {
                "description": response_data["weather"][0]["description"],
                "temp": response_data["main"]["temp"],
                "feels_like": response_data["main"]["feels_like"],
                "humidity": response_data["main"]["humidity"],
                "wind_speed": response_data["wind"]["speed"]
            }

    def print_weather(self, weather_data: dict):
        if self._state_name == "" or self._country_code != "US":
            temperature_unit = "°C"
            speed_unit = "km/h"
        else:
            temperature_unit = "°F"
            speed_unit = "mph"

        print(f"Weather condition: {weather_data['description']}")
        print(f"Temperature: {weather_data['temp']}{temperature_unit}")
        print(f"Feels like: {weather_data['feels_like']}{temperature_unit}")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind: {weather_data['wind_speed']} {speed_unit}")


def main():
    print('Weather Bot')

    while True:
        print('For weather, please enter the following information')
        city_name = input("City name: ")
        state_name = input("State name (only if in the US): ")
        country_code = input("Country code (e.g., US, GB): ")

        weather_bot = WeatherBot(city_name, country_code, state_name)
        latitude, longitude = weather_bot.location()
        current_weather = weather_bot.current_weather(latitude, longitude)
        if current_weather:
            weather_bot.print_weather(current_weather)

        exit_or_continue = input('To continue, press C. To exit, press E: ')
        if exit_or_continue.lower() == "e":
            break


if __name__ == '__main__':
    main()
