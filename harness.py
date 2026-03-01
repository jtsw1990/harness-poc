import ollama

SYSTEM_PROMPT = """
You are a helpful assistant.
Only use tools when the user is explicitly asking for something a tool can provide.
If you can answer from your own knowledge, just answer directly without using any tools.
"""

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

def get_weather(city: str) -> str:
    return f"The weather in {city} is 22 C and sunny."

def run_tool(name: str, args: dict) -> str:
    if name == 'get_weather':
        return get_weather(**args)
    else:
        return f'Unknown tool: {name}'


user_message = input()

messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
]

response = ollama.chat(
    model="llama3.1",
    messages=messages,
    tools=tools,
    options={"verbose": True}
)

print("--- RAW RESPONSE ---")
print(response)
print("--- STOP REASON ---")
print(response['message'].get('tool_calls'))
print("--- RESPONSE ---")
print(response['message']['content'])