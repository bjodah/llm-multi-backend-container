#!/bin/bash

# Sometimes we don't want to involve llama-swap, this is just an example
# of how to directly use one of the backends (exllamav2) in the container image.

repo_root_dir="$(realpath $(dirname $0)/..)"
if [ ! -d "$repo_root_dir"/env-llm-multi-backend ]; then
    >&2 echo "No such directory: $repo_root_dir/env-llm-multi-backend/"
    exit 1
fi

podrun \
    --net=host \
    -w "/" \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -v "$repo_root_dir/configs":/configs \
    -v "$repo_root_dir/configs/tabby-api_tokens.yml:/api_tokens.yml" \
    --entrypoint=/usr/bin/env \
    --cont-img-dir "$repo_root_dir/env-llm-multi-backend" \
    --device nvidia.com/gpu=all \
    --security-opt=label=disable \
    --ipc=host \
                   -- \
                   python3 /opt/tabbyAPI/main.py \
                   --config /configs/tabby-config-qwen25-coder-7b.yml
