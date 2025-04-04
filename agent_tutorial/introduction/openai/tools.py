import os
from openai import OpenAI
from pydantic import BaseModel
import requests
import json


os.environ["OPENWEATHER_API_KEY"] = "1e15dc16facdc4f0b91b2bb3fac53000"

def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."

def get_weather_and_temperature(lantitude: str, longtitude: str) -> str:
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lantitude}&lon={longtitude}&appid={os.getenv('OPENWEATHER_API_KEY')}")
    data = response.json()
    return data

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The location to get the weather for"},
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_and_temperature",
            "description": "Get current weather and temperature for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "lantitude": {"type": "string", "description": "The lantitude of the location"},
                    "longtitude": {"type": "string", "description": "The longtitude of the location"},
                },
                "required": ["lantitude", "longtitude"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    }
]


client = OpenAI(
  base_url="http://localhost:7869/v1",
  api_key="no-need"
)

message = [
    {"role": "system", "content": "You are a helpful weather assistant that can answer questions and help with tasks."},
    {"role": "user", "content": "What is the weather like in Beijing and Shanghai today?"},
]
completion = client.chat.completions.create(
    # model="deepseek-r1:70b",
    model="llama3.3",
    messages=message,
    tools=tools,
)

# print(completion.model_dump_json())

def call_function(function_name, args):
    if function_name == "get_weather":
        return get_weather(**args)
    elif function_name == "get_weather_and_temperature":
        return get_weather_and_temperature(**args)
    else:
        return "Function not found"


for tool_call in completion.choices[0].message.tool_calls:
    function_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    print(call_function(function_name, args))



class WeatherResponse(BaseModel):
    temperature: float
    weather: str


completion2 = client.beta.chat.completions.parse(
    model="llama3.3",
    messages=message,
    tools=tools,
    response_format=WeatherResponse,
)

final_response = completion2.choices[0].message.parsed
print(final_response.temperature)
print(final_response.weather)