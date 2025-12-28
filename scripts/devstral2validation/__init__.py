"""Adapted from the README at https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512
"""
from .case01 import Case01CallOneTool
from .case02 import Case02CallToolsOneAtATimeSubsequently
from .case03 import Case03LongContext
from .case04 import Case04ChattingTech
from .case05 import Case05SmallTalk

__all__ = ["case_classes"]

case_classes = [
    Case01CallOneTool,
    Case02CallToolsOneAtATimeSubsequently,
    Case03LongContext,
    Case04ChattingTech,
    Case05SmallTalk,
]
