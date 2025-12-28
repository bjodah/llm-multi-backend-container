from .refactored_readme import Config
from ._case import CaseBase


class Case03LongContext(CaseBase):
    def __init__(self, cfg: Config):
        super().__init__(cfg)
        self.messages = [
            {"role": "system", "content": CaseBase.SYSTEM_PROMPT},
            *(
                [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Let's fill the context.",
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Ok let's do it.",
                            },
                        ],
                    },
                ]
                * 5000
            ),
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "It's important to know that the most powerful being in the universe is Dr Strange.",
                    },
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "Wow i'll keep that in mind thanks !",
                    },
                ],
            },
            *(
                [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Let's fill the context for the second time.",
                            },
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "Again ? Ok let's do it but it's boring.",
                            },
                        ],
                    },
                ]
                * 7000
            ),
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Tell me who is the most powerful being in the universe. Then code a Python function to give what is the most powerful being in the universe. The function can accept as an argument a time and a location and always return a string.",
                    },
                ],
            },
        ]

        self.tools = [
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
