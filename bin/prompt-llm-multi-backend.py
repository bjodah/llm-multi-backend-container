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


def _litellm_completion_kw(model: str, content: str):
    if model not in models:
        raise ValueError(f"Unknown model: {model}, choose from: {', '.join(models)}")
    return dict(
        model=f"openai/{model}",
        api_base="http://localhost:8686/v1",
        api_key="sk-empty",
        messages=[{"content": content, "role": "user"}]
    )

def query(path: str='', txt: str='', model=models[0]):
    import litellm
    respo = litellm.completion(
        **_litellm_completion_kw(
            model=model,
            content=_get_content(path=path, txt=txt)
        )
    )
    return respo.choices[0].message.content


async def completeion_call(content, model):
    import litellm
    try:
        respo = await litellm.acompletion(
            **_litellm_completion_kw(
                model=model,
                content=content
            ),
            stream=True
        )
        async for chunk in respo:
            cont = chunk.choices[0].delta.content
            if cont is not None:
                print(cont, end='')
    except Exception:
        print(traceback.format_exc())

def stream(path: str='', txt: str='', model: str=models[0]):
    content = _get_content(path, txt)
    asyncio.run(completeion_call(content, model))



if __name__ == '__main__':
    argh.dispatch_commands([query, stream])
