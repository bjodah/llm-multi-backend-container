import json
from pathlib import Path
from .refactored_readme import send_messages, load_system_prompt, Config

class CaseBase:
    cfg: Config
    SYSTEM_PROMPT: str
    messages: list[dict]
    tools: list[dict]
    expected_output_trace: list[dict]

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.SYSTEM_PROMPT = load_system_prompt("CHAT_SYSTEM_PROMPT.txt", model_name=cfg.model)
        folder = Path(__file__).parent
        filename = self.__class__.__name__.lower()[:6] + '.json'
        with (folder / filename).open('r') as ifh:
            src = ifh.read()  #  not actual json
            self.expected_output_trace = eval(src, dict(null=None))
        # rest of fields set by subclasses' __init__

    def __call__(self):
        respons_msgs = send_messages(messages=self.messages, tools=self.tools, cfg=self.cfg)
        # Fuzzy? compare with expected_output_trace:
        print(f"Got:\n{respons_msgs}\nExpected:\n{self.expected_output_trace}")
