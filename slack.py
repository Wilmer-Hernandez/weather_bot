from slack_sdk import WebClient
import os
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from weather_bot import WeatherBot
from spellchecker import SpellChecker

load_dotenv()

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ.get('SIGNING_SECRET'),
    '/slack/events',
    app
)

token = os.environ.get('SLACK_TOKEN')
client = WebClient(token=token)

BOT_ID = client.api_call("auth.test")['user_id']

spell = SpellChecker()


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if BOT_ID != user_id and text[0] != '/':
        client.chat_postMessage(
            channel=channel_id,
            text=(
                "This chat is for asking the weather only.\n"
                "Please use the '/weather' command for weather any a location."
            )
        )


@app.route('/weather', methods=['POST'])
def weather():
    data = request.form
    channel_id = data.get('channel_id')
    text_from_command = data.get('text')

    location = text_from_command.strip().split(",")
    city_name = location[0]
    state_name = ''
    if location[-1].upper().strip() != 'US':
        country_code = location[1].upper()
        unit_system = "metric"
    else:
        state_name = location[1]
        country_code = location[2].upper()
        unit_system = "imperial"

    weather_bot = WeatherBot(city_name, country_code, state_name)
    latitude, longitude = weather_bot.location()
    current_weather = weather_bot.current_weather(
        latitude,
        longitude,
        unit_system=unit_system
    )

    client.chat_postMessage(
            channel=channel_id,
            text=(
                f"Weather condition: {current_weather['description']}\n"
                f"Temperature:{current_weather['temp']}"
                f"{current_weather['temperature_unit']}\n"

                f"Feels like: {current_weather['feels_like']}"
                f"{current_weather['temperature_unit']}\n"

                f"Humidity: {current_weather['humidity']}%\n"

                f"Wind: {current_weather['wind_speed']}"
                f"{current_weather['speed_unit']}"
            )
    )
    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
