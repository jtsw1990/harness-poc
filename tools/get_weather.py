'''placeholder get weather tool for testing.'''


get_weather_tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the CURRENT real-time weather for a city. Only use this when the user asks about current weather conditions. DO NOT CALL THIS FUNCTION MORE THAN ONCE IN A LOOP",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name e.g London"
                    }
                }, "required": ["city"]
            }
        }
    }

def get_weather(city: str) -> str:
    return f"The weather in {city} is 22 C and sunny."