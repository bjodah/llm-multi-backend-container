#!/bin/bash
podrun \
    --device nvidia.com/gpu=all \
    --security-opt=label=disable \
    --ipc=host \
    -e NVIDIA_VISIBLE_DEVICES=all \
    --gpu \
    --image localhost/llm-multi-backend-container_llama-swapper:2025-11-09 \
    --entrypoint env \
    -- 'python3 -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_capability(None))"'
