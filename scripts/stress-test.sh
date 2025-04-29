#!/bin/bash
set -euxo pipefail

# from https://github.com/mostlygeek/llama-swap/issues/100#issuecomment-2831191000
HOST=localhost:8686
ARGS='"max_tokens":50, "timings_per_token":true, "messages": [{"role": "user","content": "write a story about dogs"}]'
while true; 
do
    curl -s http://$HOST/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model":"vllm-SmolLM2-1.7B-Instruct", '"$ARGS"'}' | jq .timings

    curl -s http://$HOST/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model":"exllamav2-Qwen2.5-Coder-14B-Instruct", '"$ARGS"'}' | jq .timings       

    curl -s http://$HOST/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"model":"llamacpp-gemma-3-1b-it", '"$ARGS"'}' | jq .timings
done
