import requests
import json


user_message = input()

SYSTEM_PROMPT = """
You are a helpful assistant.
Only use tools when the user is explicitly asking for something a tool can provide.
If you can answer from your own knowledge, just answer directly without using any tools.
"""

messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the CURRENT real-time weather for a city. Only use this when the user asks about current weather conditions.",
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
]

payload = {
    "model": "llama3.1",
    "messages": messages,
    "tools": tools,
    "stream": False
}

print("--- WHAT WE'RE SENDING ---")
print(json.dumps(payload, indent=2))

response = requests.post("http://localhost:11434/api/chat", json=payload)
print("--- RAW RESPONSE ---")
print(json.dumps(response.json(), indent=2))