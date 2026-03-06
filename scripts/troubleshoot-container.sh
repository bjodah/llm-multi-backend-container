#!/bin/bash
podrun \
    --device nvidia.com/gpu=all \
    --security-opt=label=disable \
    --ipc=host \
    -e NVIDIA_VISIBLE_DEVICES=all \
    --gpu \
    --image localhost/llm-multi-backend-container_llama-swapper:latest \
    --entrypoint env \
    -- 'python3 -c "import torch; print(\"torch\", torch.__version__); print(\"torch cuda\", torch.version.cuda)"
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
ls -l /usr/local/cuda/compat/libcuda.so* 2>/dev/null || true
LD_DEBUG=libs python3 -c "import torch; import torch.cuda; torch.cuda.is_available()" 2>&1 | grep -E "libcuda\.so|compat" | tail -n 20'
