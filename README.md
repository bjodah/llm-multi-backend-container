# llm-multi-backend-container
Use llama-swap inside a container with vllm, llama.cpp, and exllamav2+tabbyAPI.

## Usage
```console
$ head ./bin/host-llm-multi-backend-container.sh
$ ./bin/host-llm-multi-backend-container.sh --build --force-recreate
```

## Testing
```console
$ bash -x scripts/test-chat-completions.sh
```

## Notes
Right now the config for vLLM and exllamav2 both struggle with allocating VRAM. Unclear why that is.
