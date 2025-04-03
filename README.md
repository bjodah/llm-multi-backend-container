# llm-multi-backend-container
Use llama-swap inside a container with vllm, llama.cpp, and exllamav2+tabbyAPI.

## Usage
```console
$ head ./bin/host-llm-multi-backend-container.sh
$ ./bin/host-llm-multi-backend-container.sh --build --force-recreate
```

## Useful(?) tools
```console
$ ./bin/prompt-llm-multi-backend.py stream --model llamacpp-gemma-3-27b-it -t "Write a poem about a
bear on a unicycle" --
```

## Testing
```console
$ bash -x scripts/test-chat-completions.sh
```

## Notes
- Right now the config for vLLM struggle with allocating VRAM. Unclear why that is.
- For customization, you might want to grep for a few keywords:
```console
$ git grep 8686
$ git grep sk-empty
```
- Does not seem like `seed` is working?
```console
./bin/prompt-llm-multi-backend.py stream -t "write a poem about a bear on a unicycle" --opts 'temperature=2.0;max_tokens=1000;seed=42'
```
