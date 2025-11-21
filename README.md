# llm-multi-backend-container
Use llama-swap inside a container with vllm, llama.cpp, and exllamav2+tabbyAPI. 

## Adapting for other machines
This repo is my working config, it's mainly used on a 16 core Ryzen machine with 64 GiB RAM and a single RTX 3090.
For customization, you might want to grep for a few keywords:
```console
$ git grep -E '\b868[6-8]\b'   # port numbers
$ git grep sk-empty            # API token/key
$ git grep -iE '(logging|loglevel|verbos)'
$ git grep -E "\b(8\.6|86)\b"  # CUDA compute arch, 8.6 == ampere (RTX 3090)
```

## Usage
```console
$ head ./bin/host-llm-multi-backend-container.sh
$ ./bin/host-llm-multi-backend-container.sh --build --force-recreate
```
See what model/backend combinations are available:
```console
$ curl -s -X GET -H "Authorization: Bearer sk-empty" http://localhost:8686/v1/models | jq -r '.data[].id' | grep -i 'qwen2.5-coder-7b'
vllm-Qwen2.5-Coder-7B
llamacpp-Qwen2.5-Coder-7B
exllamav2-Qwen2.5-Coder-7B
```

## Agentic coding
I've been experimenting with `codex`, `qwen-code` and `open-code`, given my modest system spec. (24GB vRAM 3090, 64GB dual ch DDR5 system ram)
there's a real struggle to make these tools perform adequately. The agents were run in a sandbox:
```console
$ cd /path/to/my/project
$ ~/llm-multi-backend-container/scripts/enter-sandbox.sh
podman build ...
podman run ...
root@3fd6c449735e:/work# cat ~/.bash_aliases.d/bash-aliases-agents.sh  # to survey configured agentic frameworks configured
```

<details>
<summary>Qwen3-Coder-30B</summary>

`llama.cpp` does not work satisfactorily (too many typos), using vllm does work much better.

```console
$ env \
  OPENAI_API_KEY=sk-empty \
  OPENAI_BASE_URL=http://host.docker.internal:8688/v1 \
  OPENAI_MODEL=vllm-Qwen3-Coder-30B \
  qwen 'run `git show 01e42d7`, study the changes, find remaining uses of hard-coded integer literals in yaml files in configs/ folder and apply this transformation to those files.'
```

using opencode also works quite well with this model:
```console
$ LLAMA_API_KEY=sk-empty opencode
```

using aider:
```console
$ alias aider-local  # short-hand for command below
$ env \
  OPENAI_API_KEY=sk-empty \
  OPENAI_API_BASE=http://host.docker.internal:8686/v1
  aider --model openai/vllm-Qwen3-Coder-30B
```

</details>

<details>
<summary>gpt-oss-20b</summary>

Nope, crashes llama.cpp due to malformated tool-calling, and even though vllm does not crash the model fails to follow through with its tasks:
the failure to complete tasks is seen in both `codex` and `opencode`.

</details>

<details>
<summary>gpt-oss-120b</summary>

This works quite alright with `codex`:

```console
$ LLAMA_API_KEY=sk-empty codex  # see .codex/config.toml
```

</details>

<details>
<summary>GLM-4.5-Air</summary>
Works decently using the qwen cli backed by llama.cpp:

```console
$ # npm install -g @qwen-code/qwen-code@latest
$ env \
    OPENAI_API_KEY=sk-empty \
    OPENAI_BASE_URL=http://host.docker.internal:8688/v1 \
    OPENAI_MODEL=llamacpp-glm-4.5-air \
    qwen
```

</details>


## Testing
```console
$ bash -x scripts/test-chat-completions.sh
+ curl -s -X POST http://localhost:8688/v1/chat/completions -H 'Content-Type: application/json' -H 'Authorization: Bearer sk-empty' -d '{"model": "llamacpp-glm-4.5-air", "messages": [{"role": "user", "content": "Answer only with the missing word: The capital of Sweden is"}]}'
+ jq '.choices[0].message.content'
"\n<think>We are to answer with only the missing word. The question is: \"The capital of Sweden is\"\n The capital of Sweden is Stockholm. Therefore, the missing word is \"Stockholm\".</think>Stockholm"
+ retcode=0
+ '[' 0 -ne 0 ']'
+ return 0
+ exit
```

## Monitoring
```console
$ ./scripts/enter-container-llama-swap.sh watch "ps aux | grep -E '(vllm|llama-|tabbyAPI)' | grep -v emacs | grep -v 'grep -E'"
$ while true; do clear; date; echo -n "currently loaded model: "; curl -s localhost:8686/running | jq -r '.running[0].model';  echo '...sleeping for 60 seconds'; sleep 60; done
$ curl -s localhost:8686/logs/stream/upstream
$ curl -s localhost:8686/logs/stream/proxy
$ ./scripts/enter-container-llama-swap.sh tail -F /tmp/llama-server-stdout-stderr.log
```

## Working directly with underlying end-point:
```console
$ curl -H "Authorization: Bearer sk-empty" http://localhost:8686/upstream/llamacpp-Qwen3-30B-A3B/health
$ curl -H "Authorization: Bearer sk-empty" http://localhost:8686/upstream/llamacpp-Qwen3-30B-A3B/slots | jq
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
    cmd: |
      /opt/llama.cpp/build/bin/llama-server
        --port ${PORT}
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
    proxy: http://127.0.0.1:${PORT}
    ttl: 3600
```

</details>

<details>
<summary>24GB of VRAM is not enough for Qwen2.5-VL-32B it seems</summary>

```
  llamacpp-Qwen2.5-VL-32B:
    cmd: |
      /opt/llama.cpp/build/bin/llama-server
        --port ${PORT}
        --ctx-size 4096
        --cache-type-k q8_0
        --cache-type-v q4_0
        --flash-attn
        --n-gpu-layers 64
        --hf-repo mradermacher/Qwen2.5-VL-32B-Instruct-i1-GGUF:i1-IQ3_S
        --temp 0.15
    proxy: http://127.0.0.1:${PORT}
    ttl: 3600
```

</details>

<details>
<summary>Instead of using vLLM, we could probably use phildougherty python app (see submodule), currently not yet working though...</summary>

```
  phildougherty-Qwen2.5-VL-7B:
    cmd: |
      python3 /phildougherty-qwen-vl-api/app.py
          --model Qwen2.5-VL-7B-Instruct
          --port ${PORT}
          --quant int8
          # --quant int4
    proxy: http://127.0.0.1:${PORT}
    ttl: 3600

```

</details>

<details>
<summary>draft model for QwQ-32B (I need an additional GPU for it to make sense)</summary>
```
        #--hf-repo-draft mradermacher/Qwen2.5-Coder-0.5B-QwQ-draft-i1-GGUF:Q4_K_M  # <-- token 151665 content differs - target '<tool_response>', draft ''
        --hf-repo-draft bartowski/InfiniAILab_QwQ-0.5B-GGUF:Q8_0
        --n-gpu-layers-draft 99
        --override-kv tokenizer.ggml.bos_token_id=int:151643
        # --draft-max 16
        # --draft-min 5
        # --draft-p-min 0.5
```
</details>

## Tidbits
<details>
<summary>testing qwen2.5-coder-7b on port 11902</summary>

```console
$ ./scripts/host-qwen2.5-coder-7b_localhost_port11902.sh
$ env OPENAI_API_BASE=localhost:11902/v1 OPENAI_API_KEY=sk-empty \
    ./scripts/test-chat-completions.sh modelnameplaceholder "In python, how do I defer deletion of a specific path to end of program?" \
    | jq -r | batcat -pp -l md
```
</details>

When debugging CUDA shenanigans, here a brain-dump of relevant commands:
```shell-session
$ sudo apt-get install nvidia-driver nvidia-driver-cuda 
$ sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
$ bash ./scripts/troubleshoot-container.sh 
```
