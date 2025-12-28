from functools import cache
from pathlib import Path
import os
import json
from openai import OpenAI
from typing import Any
from datetime import datetime, timedelta

from huggingface_hub import hf_hub_download


client = OpenAI(
    api_key=os.environ.get("MB_OPENAI_API_KEY", "sk-empty"),
    base_url=os.environ.get("MB_OPENAI_API_BASE", "http://localhost:8686/v1"),
)

class Config:
    model: str
    max_tokens: int
    temperature: float = 0.15

    def __init__(self, *, model, max_tokens):
        self.model = model
        self.max_tokens = max_tokens
        assert 'devstral-2' in model.lower() or 'devstral-small-2' in model.lower()



@cache
def load_system_prompt(filename: str, *, model_name: str) -> str:
    template_dir = Path(__file__).parent / "../../cot_proxy/examples/devstral-2"
    with (template_dir / filename).open("r") as ifh:
        system_prompt = ifh.read()
    today = datetime.today().strftime("%Y-%m-%d")
    yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    idx = model_name.lower().find('devstral')
    assert idx >= 0
    return system_prompt.format(name=model_name[idx:], today=today, yesterday=yesterday)


#SYSTEM_PROMPT = load_system_prompt("CHAT_SYSTEM_PROMPT.txt")


def add_number(a: float | str, b: float | str) -> float:
    a, b = float(a), float(b)
    return a + b


def multiply_number(a: float | str, b: float | str) -> float:
    a, b = float(a), float(b)
    return a * b


def substract_number(a: float | str, b: float | str) -> float:
    a, b = float(a), float(b)
    return a - b


def write_a_story() -> str:
    return "A long time ago in a galaxy far far away..."


def terminal(command: str, args: dict[str, Any] | str) -> str:
    return "found nothing"


def python(code: str, result_variable: str) -> str:
    data = {}
    exec(code, data)   # <-- !!! watch out, better run this in a sandboxed environment
    return str(data[result_variable])


MAP_FN = {
    "add_number": add_number,
    "multiply_number": multiply_number,
    "substract_number": substract_number,
    "write_a_story": write_a_story,
    "terminal": terminal,
    "python": python,
}

def send_messages(*, messages, cfg: Config, tools: list=[]):
    has_tool_calls = True
    origin_messages_len = len(messages)
    while has_tool_calls:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
        )
        tool_calls = response.choices[0].message.tool_calls
        content = response.choices[0].message.content
        messages.append(
            {
                "role": "assistant",
                "tool_calls": [tc.to_dict() for tc in tool_calls]
                if tool_calls
                else tool_calls,
                "content": content,
            }
        )
        results = []
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = tool_call.function.arguments
                result = MAP_FN[function_name](**json.loads(function_args))
                results.append(result)
            for tool_call, result in zip(tool_calls, results):
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": str(result),
                    }
                )
        else:
            has_tool_calls = False
    return messages[origin_messages_len:]


_default_tools = [
    {
        "type": "function",
        "function": {
            "name": "add_number",
            "description": "Add two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "string",
                        "description": "The second number.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_number",
            "description": "Multiply two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "string",
                        "description": "The second number.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "substract_number",
            "description": "Substract two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "string",
                        "description": "The first number.",
                    },
                    "b": {
                        "type": "string",
                        "description": "The second number.",
                    },
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_a_story",
            "description": "Write a story about science fiction and people with badass laser sabers.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "Perform operations from the terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command you wish to launch, e.g `ls`, `rm`, ...",
                    },
                    "args": {
                        "type": "string",
                        "description": "The arguments to pass to the command.",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "python",
            "description": "Call a Python interpreter with some Python code that will be ran.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to run",
                    },
                    "result_variable": {
                        "type": "string",
                        "description": "Variable containing the result you'd like to retrieve from the execution.",
                    },
                },
                "required": ["code", "result_variable"],
            },
        },
    },
]
