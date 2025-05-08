# llm-multi-backend-container
Use llama-swap inside a container with vllm, llama.cpp, and exllamav2+tabbyAPI.

## Usage
```console
$ head ./bin/host-llm-multi-backend-container.sh
$ ./bin/host-llm-multi-backend-container.sh --build --force-recreate
```

## Useful(?) tools
```console
$ ./bin/prompt-llm-multi-backend.py stream --model llamacpp-gemma-3-27b-it \
-t "Write a poem about a bear on a unicycle" -o 'temperature=1.9;seed=42;top_p=0.99'
```
<details>
<summary>output</summary>

```
Old Barnaby Bear, a fluffy brown sight,
Had a passion unusual, with all of his might.
He didn't like fishing, or berries you see,
Barnaby dreamed of mobility!

He traded a honeycomb, sticky and sweet,
For a unicycle, two wheels 'neath his feet.
The villagers chuckled, "A bear on one wheel?
A comical vision, beyond the appeal!"

But Barnaby practiced, with wobble and sway,
Falling and grumbling, each and every day.
He'd bump into trees and tumble and roll,
But stubborn determination controlled his strong soul.

Then one sunny morning, a gasp filled the air,
As Barnaby pedaled, beyond all compare!
He zoomed 'round the meadow, a blur of brown fur,
A unicycling bear, a joyful murmur!

He balanced and wobbled, he laughed and he grinned,
A skill he'd perfected, from deep within.
He waved to the children, he honked a small horn,
A bear on a unicycle, freshly reborn!

Now Barnaby Bear, a legend he's grown,
Rides through the forest, entirely his own.
A lesson he teaches, with every slow spin,
That anything's possible, if you try from within!
```

</details>

multiple choice questions using logprobs:
```console
$ ./bin/prompt-llm-multi-backend.py multiple-choice --model llamacpp-gemma-3-4b-it -t "\
What animals are likely to take to the sky among (Vulture, Beaver, Shark, Owl)?\
 A) All of them,\
 B) All but Owl,\
 C) All but Shark,\
 D) All but Beaver,\
 E) All but Vulture,\
 F) Vulture & Beaver,\
 G) Vulture & Shark,\
 H) Beaver & Shark,\
 I) Vulture & Owl,\
 J) Beaver & Owl,\
 K) Shark & Owl,\
 L) Owl and Beaver,\
 M) only Vulture,\
 N) only Beaver,\
 O) just Shark,\
 P) none except Owl. \
Answer with a single captial letter."\
  -c 'ABCDEFGHIJKLMNOP' \
  -o 'temperature=0.5;seed=3' # --raw
{'I': -0.0008952451171353459, 'L': -7.637594699859619, 'J': -8.77194881439209, 'P': -9.472918510437012, 'M': -9.596308708190918, 'E': -10.473910331726074, 'K': -10.606471061706543, 'O': -11.581477165222168, 'A': -11.586169242858887, 'N': -11.649832725524902, 'F': -11.727849006652832, 'H': -12.113730430603027, 'G': -12.510756492614746, 'B': -12.937010765075684, 'D': -13.124835014343262, 'C': -13.154669761657715}
```

Tool usage (symbolic mathematics using SymPy):
```console
$ ( set -x; for meth in query query-with-sympy; do time ./bin/prompt-llm-multi-backend.py ${meth} --model llamacpp-Qwen3-4B -t "If x*x + 5 equals 3*y, and one plus the cube of x equals 2*x, then what are the possible sets of values (x, y) that satisfy these conditions?"; done )  # Qwen3 4B even without tool calling is quite impressive.
TODO (json encoding shenanigans?)
```

<details>
<summary>testing qwen2.5-coder-7b on port 2507</summary>

```console
$ ./scripts/host-qwen2.5-coder-7b_localhost_port2507.sh
$ env OPENAI_API_BASE=localhost:2507/v1 OPENAI_API_KEY=sk-empty \
    ./scripts/test-chat-completions.sh modelnameplaceholder "In python, how do I defer deletion of a specific path to end of program?" \
    | jq -r | batcat -pp -l md
```
</details>

## Testing
```console
$ bash -x scripts/test-chat-completions.sh
```

## Monitoring
```console
$ watch "ps aux | grep -E '(vllm|llama-|tabbyAPI)' | grep -v emacs | grep -v 'grep -E'"
$ while true; do clear; date; echo -n "currently loaded model: "; curl -s localhost:8686/running | jq -r '.running[0].model';  echo '...sleeping for 60 seconds'; sleep 60; done
$ curl -s localhost:8686/logs/stream/upstream
$ curl -s localhost:8686/logs/stream/proxy
```

## Notes
- For customization, you might want to grep for a few keywords:
```console
$ git grep 8686
$ git grep sk-empty
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
