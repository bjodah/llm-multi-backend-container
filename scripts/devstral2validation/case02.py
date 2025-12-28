from .refactored_readme import Config
from ._case import CaseBase


class Case02CallToolsOneAtATimeSubsequently(CaseBase):
    def __init__(self, cfg: Config):
        super().__init__(cfg)
        self.messages = [
            {"role": "system", "content": CaseBase.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Compute the results steps by steps for the equations that involve only numbers displayed in the image. You have to call tools to perform the operations and can do one operation at a time per equation.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://math-coaching.com/img/fiche/46/expressions-mathematiques.jpg"
                        },
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
