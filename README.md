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

## Downloading models
Downloading Unsloth's Maverick:
```console
$ HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download unsloth/Llama-4-Maverick-17B-128E-Instruct-GGUF --exclude "*.gguf"
$ HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download unsloth/Llama-4-Maverick-17B-128E-Instruct-GGUF --include "UD-Q2_K_XL/*.gguf"
```
Downloading Unsloth's Q2_K_XL quants (248 GB) of DeepSeek V3 0324:
```console
$ HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download unsloth/DeepSeek-V3-0324-GGUF --exclude "*.gguf" \
&& HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download unsloth/DeepSeek-V3-0324-GGUF --include "UD-Q2_K_XL/*.gguf"
```


## Unused configurations
<details>
<summary>deepseek-v3 (I only have 64GB of RAM, which is not enough)</summary>

```
  # notes:
  #  1. maybe use:
  #      - https://huggingface.co/ubergarm/DeepSeek-V3-0324-GGUF
  #      - https://github.com/ikawrakow/ik_llama.cpp/discussions/258
  llamacpp-deepseek-v3-0324:
    cmd: >
      /opt/llama.cpp/build/bin/llama-server
        --port 8017
        --ctx-size 16384
        --seed "-1"
        --prio 2
        --temp 0.3
        --min-p 0.01
        --model /root/.cache/huggingface/hub/models--unsloth--DeepSeek-V3-0324-GGUF/snapshots/b3e19c41e42074be413d73f1d0e1b7f2be9e60c3/UD-IQ2_XXS/DeepSeek-V3-0324-UD-IQ2_XXS-00001-of-00005.gguf  # ~219GB for 1..5
        --n-gpu-layers 1
        --ubatch-size 1
        --jinja
    #--model /root/.cache/huggingface/hub/models--unsloth--DeepSeek-V3-0324-GGUF/snapshots/b3e19c41e42074be413d73f1d0e1b7f2be9e60c3/UD-Q2_K_XL/DeepSeek-V3-0324-UD-Q2_K_XL-00001-of-00006.gguf  # zombie process after reading 231G (of 248G)
    proxy: http://127.0.0.1:8017
    ttl: 3600
```

</details>

<details>
<summary>24GB of VRAM is not enough for Qwen2.5-VL-32B it seems</summary>

```
  llamacpp-Qwen2.5-VL-32B:
    cmd: >
      /opt/llama.cpp/build/bin/llama-server
        --port 8013
        --ctx-size 4096
        --cache-type-k q8_0
        --cache-type-v q4_0
        --flash-attn
        --n-gpu-layers 64
        --hf-repo mradermacher/Qwen2.5-VL-32B-Instruct-i1-GGUF:i1-IQ3_S
        --temp 0.15
    proxy: http://127.0.0.1:8013
    ttl: 3600
```

</details>

<details>
<summary>Instead of using vLLM, we could probably use phildougherty python app (see submodule), currently not yet working though...</summary>

```
  phildougherty-Qwen2.5-VL-7B:
    cmd: >
      python3 /phildougherty-qwen-vl-api/app.py
          --model Qwen2.5-VL-7B-Instruct
          --port 8015
          --quant int8
          # --quant int4
    proxy: http://127.0.0.1:8015
    ttl: 3600

```

</details>
