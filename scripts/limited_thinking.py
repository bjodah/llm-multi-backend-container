import dataclasses as dcs
import requests
import json
from typing import Any
from pydantic import BaseModel


@dcs.dataclass
class _Client:
    model: str
    api_base: str = 'http://localhost:8686/upstream'
    headers: dict[str, str] = dcs.field(default_factory=lambda: {"Authorization": "Bearer sk-empty"})

    @property
    def endpoint_base(self) -> str:
        return self.api_base

    def _post(self, endpoint: str, /, **kwargs) -> requests.Response:
        return requests.post(
            f'{self.endpoint_base}/{endpoint}',
            data=json.dumps(kwargs),
            headers=self.headers
        )

class LlamaCppClient(_Client):

    def __post_init__(self):
        super().__post_init__()
        assert self.model.startswith('llamacpp-')


    @property
    def endpoint_base(self) -> str:
        return f"{self.api_base}/{self.model}"

    def apply_template(self, *, messages: list[dict], **kwargs):
        return self._post('apply-template', messages=messages, **kwargs)

    def completion(self, *, prompt: str, **kwargs):
        return self._post('completion', prompt=prompt, **kwargs)

    # def prompt_text(self, txt: str, **kwargs) -> dict:
    #     resp = self._completions(prompt=txt, **kwargs)
    #     return resp.json()



def get_client(model: str) -> _Client:
    if model.startswith('llamacpp-'):
        return LlamaCppClient(model=model)
    else:
        raise NotImplementedError(...)

class Message(BaseModel):
    role: str
    content: str

class Chat(BaseModel):
    messages: list[Message]

    @classmethod
    def from_text(cls, arg: str, /) -> "Chat":
        return cls(messages=[Message(role="user", content=arg)])


@dcs.dataclass
class Moderator:
    client: LlamaCppClient

    def _pre_process_chat(self, chat: Chat) -> Chat:
        return chat

    def _post_process_completions_response(self, resp_c: requests.Response, *, prompt: str) -> dict:
        return resp_c.json()

    def _kw_completions(self, prompt: str) -> dict[str, Any]:
        return {'prompt': prompt}

    def prompt_chat(self, chat: Chat, **kwargs) -> dict:
        _chat = self._pre_process_chat(chat)
        resp_t = self.client.apply_template(**_chat.model_dump())
        resp_t_j = resp_t.json()
        resp_c = self.client.completion(**self._kw_completions(**resp_t_j), **kwargs)
        return self._post_process_completions_response(resp_c, **resp_t_j)


@dcs.dataclass
class Qwen3Mode:
    thinking_budget_tokens: int=-1

    @property
    def do_think(self):
        return self.thinking_budget_tokens != 0

    @classmethod
    def never_think(cls) -> "Qwen3Mode":
        return cls(0)

    @classmethod
    def think_indefinitely(cls) -> "Qwen3Mode":
        return cls(-1)

    @classmethod
    def think_limited(cls, *, token_limit: int) -> "Qwen3Mode":
        return cls(token_limit)




_cut_thinking_short = "... Considering the limited time by the user, I have to give the solution based on the thinking directly now.\n</think>\n\n"

@dcs.dataclass
class ModeratorQwen3(Moderator):
    mode: Qwen3Mode

    @property
    def think_tags(self) -> tuple[str, str]:
        return ("<think>", "</think>")

    def _strip_leading_empty_thinking_tags(self, content: str):
        _, resp_content = content.split(self.think_tags[1], 1)
        a, b = _.split(self.think_tags[0])
        assert len(a.strip()) == 0 and len(b.strip()) == 0
        return resp_content

    def _pre_process_chat(self, chat: Chat) -> Chat:
        assert chat.messages[-1].role == 'user'
        think_imperative = {False: '/no_think', True: '/think'}
        last_msg_cont = chat.messages[-1].content
        for imper in think_imperative.values():
            assert imper not in last_msg_cont
        return Chat(messages=chat.messages[:-1] + [
            Message(role='user', content=last_msg_cont + ' ' + think_imperative[self.mode.do_think])
        ])

    def _kw_completions(self, prompt: str) -> dict[str, Any]:
        kw = dict(prompt=prompt)
        if self.mode.do_think:
            kw['stop'] = '</think>'
            if self.mode.thinking_budget_tokens > 0:
                kw['max_tokens'] = self.mode.thinking_budget_tokens
        return kw

    def _post_process_completions_response(self, resp_c: requests.Response, *, prompt: str) -> dict:
        body = resp_c.json()
        content = body.pop('content')
        if not self.mode.do_think:
            body['response_content'] = self._strip_leading_empty_thinking_tags(content)
            return body

        if body['stop_type'] == 'eos':
            # extract thinking part into reasoning_content:
            assert content.count(self.think_tags[1]) == 1
            body['reasoning_content'], body['response_content'] = content.split(self.think_tags[1], 1)
            body['reasoning_content'].lstrip('\n')
            if body['reasoning_content'].startswith(self.think_tags[0]):
                body['reasoning_content'] = body['reasoning_content'][len(self.think_tags[0]):]
                body['reasoning_content'].lstrip('\n')
        elif body['stop_type'] == 'limit':
            resp_c2 = self.client.completion(prompt=prompt + content + _cut_thinking_short)
            body['reasoning_content'] = content
            body['response_content'] = resp_c2.json()['content']
        return body


def main(
        model='llamacpp-Qwen3-8B',
        user_prompt: str="What's the capital of France?",
        thinking_budget_tokens: int=50,
        max_tokens=2048
):
    assert max_tokens > thinking_budget_tokens
    client = get_client(model)
    assert 'Qwen3' in model
    modr = ModeratorQwen3(client=client, mode=Qwen3Mode(thinking_budget_tokens))
    chat = Chat.from_text(user_prompt)
    body = modr.prompt_chat(chat)
    print(body)
    print("\n\n")
    print(f"{body['reasoning_content']=}")
    print(f"{body['response_content']=}")


if __name__ == '__main__':
    main()
