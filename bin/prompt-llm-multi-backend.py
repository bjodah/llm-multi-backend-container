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
import json
import traceback
import yaml
import warnings

try:
    import litellm
except ImportError:
    warnings.warn("Could not import litellm, install using e.g. pip")
    litellm = None


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

def _messages_zero_shot(content: str):
    assert len(content) > 0
    return [{"content": content, "role": "user"}]

def _litellm_completion_kw(*, model: str, opts: str, messages: list[dict[str, str]]):
    kw = dict(messages=messages)
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
        messages=_messages_zero_shot(_get_content(path=path, txt=txt)),
        opts=opts
    )
    respo = litellm.completion(**kw)
    if raw:
        return respo
    else:
        return respo.choices[0].message.content

def query_with_sympy(path: str='', txt: str='', model=models[0], opts='', raw: bool=False):
    from sympy import solve, parse_expr, Basic
    from sympy.parsing.sympy_parser import standard_transformations, convert_xor, implicit_multiplication
    def _parse(arg: str) -> Basic:
        return parse_expr(arg, transformations=standard_transformations+(convert_xor, implicit_multiplication))

    def sympy_solve_equations(exprs: str='[x**2 + y**2 - 1, x - 1/sqrt(2)]', wrt: str='x,y') -> str:
        s_exprs = list(map(_parse, exprs.lstrip('[').rstrip(']').split(',')))
        s_wrt = _parse(wrt)
        sols = solve(s_exprs, s_wrt, dict=True)
        return str(sols)

    if True:
        messages = []
    else: # TODO: get multi-shot with tool calling below to work to enhance accuracy.
        messages = [
            {"role": "user", "content": (
                "For a (unit) circle with radius one, centered in (x,y), (0,0)."
                " What are the allowed values x and y can take on if we require"
                " that y is equal two times x?")},
            {"role": "assistant", "tool_calls": [
                {"type": "function_call", "id": "fc_001", "call_id": "call_002", "name": "solve_equations",
                 'arguments': '{"exprs": "[x**2+y**2-1, y-2*x]", "with_respect_to": "x,y"}'}
            ]},
            # >>> solve(parse_expr('[x**2+y**2-1,y-2*x]'), parse_expr('[x,y]'), dict=True)
            # [{x: -sqrt(5)/5, y: -2*sqrt(5)/5}, {x: sqrt(5)/5, y: 2*sqrt(5)/5}]
            {"tool_call_id": "call_002", "role": "tool", "name": "solve_equations",
             "content": "[{x: -sqrt(5)/5, y: -2*sqrt(5)/5}, {x: sqrt(5)/5, y: 2*sqrt(5)/5}]"},
            {"role": "assistant", "content": "x can be either ±√5/5, for either of those values y takes one the value 2⋅x"}
        ]
    messages.append({"role": "user", "content": _get_content(path, txt)})
    kw = _litellm_completion_kw(
        model=model,
        messages=messages,
        opts=opts
    )
    kw['tools'] = [
        {
            "type": "function",
            "function": {
                "name": "solve_equations",
                "description": "Solve system of equation with respect to a set of symbols",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exprs": {
                            "type": "string",
                            "description": "the equation that are to be satisfied (=0).",
                        },
                        "with_respect_to": {
                            "type": "string",
                            "description": "comma separated list of symbol names to solve for (excluding parameters/constants such as 'pi')."
                        }
                    }
                }

            }
        }
    ]
    kw['tool_choice'] = 'auto'  # 'auto' is default, not strictly needed
    respo = [litellm.completion(**kw)]
    rc0_msg =  respo[-1].choices[0].message

    if rc0_msg.tool_calls:
        available_functions = {'solve_equations': sympy_solve_equations}
        messages.append(rc0_msg)
        for tcall in rc0_msg.tool_calls:
            f = available_functions[tcall.function.name]
            args = json.loads(tcall.function.arguments)
            ans: str = f(exprs=args.get("exprs"), wrt=args.get("with_respect_to"))
            print(f"{ans=}")##DEBUG PRINT STATEMENT, to be dropped
            messages.append({"tool_call_id": tcall.id, "role": "tool", "name": tcall.function.name, "content": ans})
        kw['messages'] = messages  # <-- this line is idempotent (?)
        respo.append(litellm.completion(**kw))
    if raw:
        return respo[-1]
    else:
        return respo[-1].choices[0].message.content


async def completion_call(content, model, opts=''):
    kw = _litellm_completion_kw(
        model=model,
        messages=_messages_zero_shot(content),
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
    asyncio.run(completion_call(content, model, opts))
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
        messages=_messages_zero_shot(_get_content(path, txt)),
        opts=opts
    )
    return _get_ranked_choices(kw, choices)

def multiple_choice(path: str='', txt: str='', choices: str='ABC', model: str=models[0], opts='', raw: bool=False):
    """Multi-shot prompt."""
    kw = _litellm_completion_kw(
        model=model,
        messages=[
            {"content": "What's the capital of France? X) Paris, Y) London, Z) Berlin. Answer with a single captial letter.", "role": "user"},
            {"content": "X", "role": "assistant"},
            {"content": "What's 2+2? P) 5, Q) 2, R) four, S) sqrt(2+2). Answer with a single captial letter.", "role": "user"},
            {"content": "R", "role": "assistant"},
            {"content": "What kind of celestial body is the sun? T) galaxy, U) star, V) moon, W) black hole. Answer with a single captial letter.", "role": "user"},
            {"content": "U", "role": "assistant"},
            {"content": content, "role": "user"}
        ],
        opts=opts
    )
    if raw:
        import litellm
        return litellm.completion(**kw, logprobs=True)
    else:
        return _get_ranked_choices(kw, choices)


if __name__ == '__main__':
    import argh
    argh.dispatch_commands([query, stream, logprobs, multiple_choice, query_with_sympy])
