import dataclasses as dcs
import requests
import json
import typing
from typing import Any
import warnings
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


class LlamaCppCompletionOptTypes:
    # see llama.cpp/tools/server/README.md
    prompt: str | list[str|int]
    cache_prompt: bool = True

    seed: int = -1
    temperature: float = 0.8
    top_k: int = 40
    top_p: float = 0.95
    min_p: float = 0.05
    typical_p: float = 1.0
    repeat_penalty: float = 1.1
    repeat_last_n: int = 64
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    dry_multiplier: float = 0.0
    dry_base: float = 1.75
    dry_allowed_length: int = 2
    dry_penalty_last_n: int = -1
    dry_sequence_breakers: list[str] = ['\n', ':', '"', '*']
    xtc_probability: float = 0.0
    xtc_threshold: float = 0.1
    mirostat: int = 0
    mirostat_tau: float = 5.0
    mirostat_eta: float = 0.1

    grammar: None = None  # ?
    json_schema: dict | None = None

    ignore_eos: bool = False
    logit_bias: list[list] = []
    n_probs: int = 0  #
    min_keep: int = 0
    t_max_predict_ms: float = 0.0

    image_data: str | None = None
    id_slot: int = -1
    return_tokens: bool = False
    samplers: list[str] = ["dry", "top_k", "typ_p", "top_p", "min_p", "xtc", "temperature"]
    timings_per_token: bool = False
    post_sampling_probs: bool = False
    response_fields: list[str] | None = None
    lora: list[dict] = []

    n_predict: int = -1  # infinity,
    stop: list[str] = []
    stream: bool = False

    dynatemp_range: float = 0.0  # disabled
    dynatemp_exponent: float = 1.0
    n_indent: int = 0  # for code completion?
    n_keep: int = 0

    max_tokens: int = -1  # weaker than n_predict, used for its default

    @classmethod
    def find_invalid(cls, opts: dict[str, Any], /) -> list[str]:
        invalid = []
        for k, v in opts.items():
            t = cls.__annotations__[k]
            origin = typing.get_origin(t) or t
            if not isinstance(v, origin):
                invalid.append(k)
        return invalid


class LlamaCppCompletionResponseStreamDelta:
    content: str
    tokens: str
    stop: bool

class LlamaCppProbBase(BaseModel):
    id: int
    token: str
    bytes: list[int]

class LlamaCppLogprob(LlamaCppProbBase):
    logprob: float

class LlamaCppProbsPreSampling(LlamaCppLogprob):
    top_logprobs: list[LlamaCppLogprob]


class LlamaCppProb(LlamaCppProbBase):
    prob: float

class LlamaCppProbsPostSampling(LlamaCppProb):
    top_probs: list[LlamaCppProb]

class LlamaCppTimings(BaseModel):
    prompt_n: int
    prompt_ms: float
    prompt_per_token_ms: float
    prompt_per_second: float
    predicted_n: int
    predicted_ms: float
    predicted_per_token_ms: float
    predicted_per_second: float

class LlamaCppCompletionResponse(BaseModel):
    completion_probabilities: list[LlamaCppProbsPreSampling|LlamaCppProbsPostSampling] | None = None
    index: int
    content: str  # empty for stream
    tokens: list[int]  # empty for stream
    id_slot: int
    stop: bool
    model: str
    tokens_predicted: int  # n_decoded
    tokens_evaluated: int  # n_prompt_tokens
    generation_settings: dict
    #{'n_predict': 50, 'seed': 4294967295, 'temperature': 0.699999988079071, 'dynatemp_range': 0.0, 'dynatemp_exponent': 1.0, 'top_k': 40, 'top_p': 0.9700000286102295, 'min_p': 0.004999999888241291, 'top_n_sigma': -1.0, 'xtc_probability': 0.0, 'xtc_threshold': 0.10000000149011612, 'typical_p': 1.0, 'repeat_last_n': 16, 'repeat_penalty': 1.0099999904632568, 'presence_penalty': 0.05000000074505806, 'frequency_penalty': 0.004999999888241291, 'dry_multiplier': 0.699999988079071, 'dry_base': 1.75, 'dry_allowed_length': 4, 'dry_penalty_last_n': 2048, 'dry_sequence_breakers': ['\n', ':', '"', '*'], 'mirostat': 0, 'mirostat_tau': 5.0, 'mirostat_eta': 0.10000000149011612, 'stop': [], 'max_tokens': 50, 'n_keep': 0, 'n_discard': 0, 'ignore_eos': False, 'stream': False, 'logit_bias': [], 'n_probs': 0, 'min_keep': 0, 'grammar': '', 'grammar_lazy': False, 'grammar_triggers': [], 'preserved_tokens': [], 'chat_format': 'Content-only', 'reasoning_format': 'deepseek', 'reasoning_in_content': False, 'thinking_forced_open': False, 'samplers': ['penalties', 'dry', 'top_n_sigma', 'top_k', 'typ_p', 'top_p', 'min_p', 'xtc', 'temperature'], 'speculative.n_max': 16, 'speculative.n_min': 0, 'speculative.p_min': 0.75, 'timings_per_token': False, 'post_sampling_probs': False, 'lora': []}
    prompt: str
    has_new_line: bool
    truncated: bool
    stop_type: str # "eos", "word", "limit", "none"
    stopping_word: str
    tokens_cached: int
    timings: LlamaCppTimings


class LlamaCppCompletionResponseStreamLast:
    pass


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
        if (invalid := LlamaCppCompletionOptTypes.find_invalid(kwargs)):
            warnings.warn(f"Invalid values for keys: {invalid}")
        return self._post('completion', prompt=prompt, **kwargs)

    # def prompt_text(self, txt: str, **kwargs) -> dict:
    #     resp = self._completion(prompt=txt, **kwargs)
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
class OperationalMode:
    n_probs: int = 0


@dcs.dataclass
class Moderator:
    client: LlamaCppClient
    operational_mode: OperationalMode


    def _pre_process_chat(self, chat: Chat) -> Chat:
        return chat

    def _post_process_completion_response(self, resp_c: requests.Response, *, prompt: str) -> dict:
        body = resp_c.json()
        body['response_content'] = body.pop('content')  # we're unifying thinking and non-thinking models here...
        return body

    def _kw_completion(self, prompt: str) -> dict[str, Any]:
        kw = {'prompt': prompt}
        if self.operational_mode.n_probs:
            kw['n_probs'] = self.operational_mode.n_probs
            kw['n_predict'] = 1
        return kw

    def prompt_chat(self, chat: Chat, **kwargs) -> dict:
        _chat = self._pre_process_chat(chat)
        resp_t = self.client.apply_template(**_chat.model_dump())
        resp_t_j = resp_t.json()
        resp_c = self.client.completion(**self._kw_completion(**resp_t_j), **kwargs)
        return self._post_process_completion_response(resp_c, **resp_t_j)


@dcs.dataclass
class ThinkingMode:
    thinking_budget_tokens: int=-1

    @property
    def do_think(self):
        return self.thinking_budget_tokens != 0

    @classmethod
    def never_think(cls) -> "ThinkingMode":
        return cls(0)

    @classmethod
    def think_indefinitely(cls) -> "ThinkingMode":
        return cls(-1)

    @classmethod
    def think_limited(cls, *, token_limit: int) -> "ThinkingMode":
        return cls(token_limit)


_cut_thinking_short_pre = "... Considering the limited time by the user, I have to give the solution based on the thinking directly now."

@dcs.dataclass
class ModeratorQwen3(Moderator):
    thinking_mode: ThinkingMode

    @property
    def think_tags(self) -> tuple[str, str]:
        return ("<think>", "</think>")

    @property
    def think_tags_full(self) -> tuple[str, str]:
        "For adding to *stripped* strings"
        return ("<think>\n", "\n</think>\n\n")

    def _cut_thinking_short_full(self):
        return _cut_thinking_short_pre + self.think_tags_full[1]

    def _extract_reasoning(self, content: str) -> tuple[str, str]:
        a, _ = content.split(self.think_tags[0], 1)
        b, c = _.split(self.think_tags[1], 1)
        assert len(a.strip()) == 0
        return b.lstrip(), c.lstrip()

    # def _strip_leading_empty_thinking_tags(self, content: str) -> str:
    #     _, resp_content = content.split(self.think_tags[1], 1)
    #     a, b = _.split(self.think_tags[0])
    #     assert len(a.strip()) == 0 and len(b.strip()) == 0
    #     return resp_content

    # def _strip_thinking_tags(self, arg: str) -> str:
    #     arg = arg.lstrip('\n')
    #     if body['reasoning_content'].startswith(self.think_tags[0]):
    #         body['reasoning_content'] = body['reasoning_content'][len(self.think_tags[0]):]
    #         body['reasoning_content'].lstrip('\n')

    def _pre_process_chat(self, chat: Chat) -> Chat:
        assert chat.messages[-1].role == 'user'
        think_imperative = {False: '/no_think', True: '/think'}
        last_msg_cont = chat.messages[-1].content
        for imper in think_imperative.values():
            assert imper not in last_msg_cont
        return Chat(messages=chat.messages[:-1] + [
            Message(role='user', content=last_msg_cont + ' ' + think_imperative[self.thinking_mode.do_think])
        ])

    def _kw_completion(self, prompt: str) -> dict[str, Any]:
        kw = dict(prompt=prompt)
        if self.thinking_mode.do_think:
            kw['stop'] = ['</think>']
            if self.thinking_mode.thinking_budget_tokens > 0:
                kw['max_tokens'] = self.thinking_mode.thinking_budget_tokens
        else:
            if self.operational_mode.n_probs:
                kw['n_probs'] = self.operational_mode.n_probs
                kw['n_predict'] = 1
        return kw

    def _kw_completion2(self) -> dict[str, Any]:
        assert self.thinking_mode.do_think  # only used for second phase of thinking
        if self.operational_mode.n_probs:
            return dict(n_probs=self.operational_mode.n_probs, n_predict=1)
        else:
            return {}

    def _post_process_completion_response(self, resp_c: requests.Response, *, prompt: str) -> dict:
        body = resp_c.json()
        content = body.pop('content')
        if not self.thinking_mode.do_think:
            reasoning, body['response_content'] = self._extract_reasoning(content)
            assert len(reasoning) == 0
            return body

        if body['stop_type'] == 'eos':
            # extract thinking part into reasoning_content:
            assert content.count(self.think_tags[1]) == 1
            body['reasoning_content'], body['response_content'] = content.split(self.think_tags[1], 1)
            body['reasoning_content'] = self._strip_thinking_tags(body['reasoning_content'])
            return body

        if body['stop_type'] in ('limit', 'word'):
            assert content.count(self.think_tags[1]) == 0
            _, reasoning = map(str.lstrip, content.split(self.think_tags[0], 1))
            assert self.think_tags[1] not in reasoning
            if body['stop_type'] == 'limit':
                reasoning = reasoning + _cut_thinking_short_pre
                new_prompt = prompt + content + self._cut_thinking_short_full()
            else:
                new_prompt = prompt + content.strip() + self.think_tags_full[1]
            resp_c2 = self.client.completion(prompt=new_prompt, **self._kw_completion2())
            body2 = resp_c2.json()
            body2['reasoning_content'] = reasoning
            body2['response_content'] = body2.pop('content')
            return body2

        raise NotImplementedError(...)




def main(
        model='llamacpp-Qwen3-8B',
        user_prompt: str="What's the capital of France? A) Paris B) Lyon C) Marseille. Answer with a single letter.",
        thinking_budget_tokens: int=50,
        max_tokens=2048,
        n_probs: int = 5
):
    assert max_tokens > thinking_budget_tokens
    client: LlamaCppClient = get_client(model)
    op_mode=OperationalMode(n_probs)
    if 'Qwen3' in model:
        modr = ModeratorQwen3(
            client=client,
            operational_mode=op_mode,
            thinking_mode=ThinkingMode(thinking_budget_tokens),
        )
    else:
        modr = Moderator(client=client, operational_mode=op_mode)
    chat = Chat.from_text(user_prompt)
    body = modr.prompt_chat(chat)
    if 'reasoning_content' in body:
        print(f"{body['reasoning_content']=}")

    if op_mode.n_probs:
        tlps = {tlp['token']: tlp['logprob']  for tlp in body['completion_probabilities'][0]['top_logprobs']}
        print(tlps)
    else:
        print(f"{body['response_content']=}")


if __name__ == '__main__':
    import argh
    argh.dispatch_command(main, output_file=None)
