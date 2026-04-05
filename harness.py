from urllib import response
from system import SYSTEM_PROMPT as SYSTEM_PROMPT

from tools.fs import write_file_tool, write_file
from tools.get_weather import get_weather_tool, get_weather

import ollama
import json
import wave
from faster_whisper import WhisperModel
import sounddevice as sd
import soundfile as sf


tools = [
    get_weather_tool,
    write_file_tool
]

def record_audio(filename='temp_audio.wav', duration=5):
    '''Record audio from microphone for a set duration and save to a file.'''
    fs = 16000  # Sample rate
    print("Recording...")
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    print("Finished recording.")
    sf.write(filename, myrecording, fs)

def transcribe_audio(filename='temp_audio.wav'):
    '''transcribe audio file to text using faster-whisper.'''
    model = WhisperModel("small")
    segments, info = model.transcribe(filename)
    text = " ".join(segment.text for segment in segments)
    return text.strip()

def run_tool(name: str, args: dict) -> str:
    if name == 'get_weather':
        return get_weather(**args)
    elif name == 'write_file':
        return write_file(**args)
    else:
        return f'Unknown tool: {name}'


class AgentHooks:
    '''
    Right now they just print, but in a real system you'd use them to:

    on_user_input → validate, sanitize, or log the input
    on_model_response → track token usage, latency, costs
    on_tool_call → log to a database, add auth checks before running tools
    on_final_answer → send to a UI, save to history, trigger another agent

    The core loop never changes — you just plug different hook logic in.
    '''
    def on_user_input(self, message: str):
        print(f'\n[HOOK] User input received: {message}')

    def on_model_response(self, response):
        tool_calls = response['message'].get('tool_calls')
        if tool_calls:
            print(f"[HOOK] Model responded with tool call")
        else:
            print(f"[HOOK] Model responded with text")

    def on_tool_call(self, name: str, args: dict, result: str):
        print(f"[HOOK] Tool '{name}' called with {args} → returned: '{result}'")

    def on_final_answer(self, answer: str):
        print(f"[HOOK] Final answer ready ({len(answer)} chars)")


def parse_output(raw: str) -> dict:
    try:
        # Strip any accidental markdown code fences
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # If model didn't follow instructions, wrap it gracefully
        return {
            "answer": raw,
            "tools_used": [],
            "confidence": "low"
        }


def run_agent(user_message: str, hooks: AgentHooks = None):

    if hooks: 
        hooks.on_user_input(user_message)

    messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
    ]
    print(f"\nUser: {user_message}")

    while True:
        response = ollama.chat(
            model="llama3.1",
            messages=messages,
            tools=tools,
        )
        message = response['message']

        tool_calls = response['message'].get('tool_calls')

        if hooks:
            hooks.on_model_response(response)

        if tool_calls:
            print(len(tool_calls))
            messages.append(response['message'])
            for tool_call in tool_calls:
                name = tool_call['function']['name']
                args = tool_call['function']['arguments']

                result = run_tool(name, args)
                if hooks:
                    hooks.on_tool_call(name, args, result=result)

                messages.append({"role": "tool", "name": name, "content": result})

        else:
        # Pass 2 — separate call with no tools, just format the answer as JSON
                format_messages = [
                    {
                        "role": "system",
                        "content": """Format the following answer as JSON exactly like this:
                    {
                        "answer": "the answer here",
                        "tools_used": ["tool1"] or [],
                        "confidence": "high" or "medium" or "low"
                    }
                    No text outside the JSON. No markdown fences."""
                    },
                    {
                        "role": "user",
                        "content": message['content'] if message['content'] else messages[-1]['content']
                    }
                ]

                format_response = ollama.chat(
                    model="llama3.1",
                    messages=format_messages
                    # no tools here intentionally
                )

                structured = parse_output(format_response['message']['content'])

                if hooks:
                    hooks.on_final_answer(structured)

                    print(f"\nUser: {user_message}")
                    print(f"Answer:      {structured['answer']}")
                    print(f"Tools used:  {structured['tools_used']}")
                    print(f"Confidence:  {structured['confidence']}")
                    break

                else:
                    print(f"[WARN] Agent hit max iterations ({max_iterations}) without a final answer.")


if __name__ == "__main__":
    hooks = AgentHooks()
    input("Press Enter to start recording (5 seconds)...")
    record_audio()
    user_text = transcribe_audio()
    print(f"Transcribed: {user_text}")
    run_agent(user_text, hooks=hooks)