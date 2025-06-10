import requests
import json

def main(model='llamacpp-Qwen3-8B', thinking_budget_tokens: int=50, max_tokens=2048):
    assert max_tokens > thinking_budget_tokens
    base_url = f'http://localhost:8686/upstream/{model}'
    def _post(endpoint: str, **kwargs):
        return requests.post(
            f'{base_url}/{endpoint}',
            data=json.dumps(kwargs),
            headers={"Authorization": "Bearer sk-empty"}
        )
    r0 = _post('apply-template', messages=[{"role": "user", "content": "What's the capital of France?"}])
    prompt1 = r0.json()['prompt']
    r1 = _post('completions', prompt=prompt1, max_tokens=thinking_budget_tokens, stop="</think>")
    body1 = r1.json()
    print(body1)
    if body1['stop_type'] == 'eos':
        reasoning_content, response_content = body1['content'].split('</think>', 1)
    elif body1['stop_type'] == 'limit' and 'qwen3' in model.lower():
        assert '</think>' not in body1['content']
        reasoning_content = body1['content']
        prompt2 = prompt1 + body1['content'] + "... Considering the limited time by the user, I have to give the solution based on the thinking directly now.\n</think>\n\n"
        print(f"{prompt2=}")
        r2 = _post('completions', prompt=prompt2, max_tokens=max_tokens - thinking_budget_tokens)
        reasoning_content = body1['content']
        response_content = r2.json()['content']
    else:
        raise NotImplementedError(f"Unhandled case: {body1['stop_type']}, {model}")
    print(f"{reasoning_content=}")
    print(f"{response_content=}")


if __name__ == '__main__':
    main()
