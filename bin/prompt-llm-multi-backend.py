#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "argh",
#     "litellm",
#     "pyyaml",
# ]
# ///
import asyncio
from pathlib import Path
import traceback
import yaml
import argh


def _get_content(path: str, txt: str) -> str:
    if (path == '' and txt == '') or (path != '' and txt != ''):
        raise ValueError("Need either path or txt")

    if txt == '':
        with open(path) as ifh:
            return ifh.read()
    elif path == '':
        return txt
    else:
        assert False  # unreachable code

with open(Path(__file__).parent / "../configs/llama-swap-config.yaml") as ifh:
    conf = yaml.safe_load(ifh)
    models = list(conf['models'].keys())

_known_opts = dict(  # a subset of kwargs accepted by litellm's `completion` function.
    temperature=float,
    top_p=float,
    n=int,
    max_completion_tokens=int,
    max_tokens=int,
    presence_penalty=float,
    frequency_penalty=float,
    logit_bias=lambda s: eval(s),
    seed=int,
    logprobs=bool
)

def _litellm_completion_kw(model: str, content: str, opts: str):
    assert len(content) > 0
    kw = dict(
        messages=[{"content": content, "role": "user"}]
    )
    if len(opts) > 0:
        for k, v in map(lambda kv: kv.split('='), opts.split(';')):
            kw[k] = _known_opts[k](v)
    if '/' in model:
        kw['model'] = model
        if model.startswith('openrouter/'):
            kw['extra_body'] = {
                "provider": {
                    "order": [
                        "lambda",
                        "nebius",
                        "novita",
                        "deepseek"
                    ]
                }
            }
    else:
        if model not in models:
            raise ValueError(f"Unknown model: {model}, choose from: {', '.join(models)}")
        kw |= dict(
            model=f"openai/{model}",
            api_base="http://localhost:8686/v1",
            api_key="sk-empty",
        )

    return kw

def query(path: str='', txt: str='', model=models[0], opts='', raw: bool=False):
    kw = _litellm_completion_kw(
        model=model,
        content=_get_content(path=path, txt=txt),
        opts=opts
    )
    import litellm
    respo = litellm.completion(**kw)
    if raw:
        return respo
    else:
        return respo.choices[0].message.content


async def completeion_call(content, model, opts=''):
    kw = _litellm_completion_kw(
        model=model,
        content=content,
        opts=opts
    )
    import litellm
    try:
        respo = await litellm.acompletion(
            **kw,
            stream=True,
            stream_options={'include_usage': True}
        )
        async for chunk in respo:
            cont = chunk.choices[0].delta.content
            if cont is not None:
                print(cont, end='')
    except Exception:
        print(traceback.format_exc())

def stream(path: str='', txt: str='', model: str=models[0], opts=''):
    content = _get_content(path, txt)
    asyncio.run(completeion_call(content, model, opts))
    print("") # prints a newline



def _get_ranked_choices(kw, choices):
    kw['logprobs'] = True
    import litellm
    respo = litellm.completion(**kw)
    top_logprobs_1st = respo.choices[0].logprobs.content[0].top_logprobs
    result = {tl.token: tl.logprob for tl in top_logprobs_1st if tl.token in choices and tl.token != ''}
    if choices:
        result = {k: v for k, v in result.items() if k in choices and k != ''}
        if len(result) == 0:
            # TODO: thinking tokens may interfere. as a fallback for now, inspect contents of body
            stripped_choice = respo.choices[0].message.content.strip()
            if stripped_choice in choices:
                result[stripped_choice] = 0.0
    return result


def logprobs(path: str='', txt: str='', choices: str='', model: str=models[0], opts=''):
    kw = _litellm_completion_kw(
        model=model,
        content=_get_content(path, txt),
        opts=opts
    )
    return _get_ranked_choices(kw, choices)

def multiple_choice(path: str='', txt: str='', choices: str='ABC', model: str=models[0], opts='', raw: bool=False):
    """Multi-shot prompt."""
    kw = _litellm_completion_kw(
        model=model,
        content=_get_content(path, txt),
        opts=opts
    )
    content = kw.pop('messages')[0]['content']
    kw['messages'] = [
        {"content": "What's the capital of France? X) Paris, Y) London, Z) Berlin. Answer with a single captial letter.", "role": "user"},
        {"content": "X", "role": "assistant"},
        {"content": "What's 2+2? P) 5, Q) 2, R) four, S) sqrt(2+2). Answer with a single captial letter.", "role": "user"},
        {"content": "R", "role": "assistant"},
        {"content": "What kind of celestial body is the sun? T) galaxy, U) star, V) moon, W) black hole. Answer with a single captial letter.", "role": "user"},
        {"content": "U", "role": "assistant"},
        {"content": content, "role": "user"}
    ]
    if raw:
        import litellm
        return litellm.completion(**kw, logprobs=True)
    else:
        return _get_ranked_choices(kw, choices)



if __name__ == '__main__':
    argh.dispatch_commands([query, stream, logprobs, multiple_choice])
