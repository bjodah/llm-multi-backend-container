#!/bin/bash
#set -x
#MB_OPENAI_API_BASE=${MB_OPENAI_API_BASE:-"http://localhost:8686/v1"}
#MB_OPENAI_API_BASE=${MB_OPENAI_API_BASE:-"http://localhost:8687/v1"} # <-- 8687 is a logging version
MB_OPENAI_API_BASE=${MB_OPENAI_API_BASE:-"http://localhost:8688/v1"} # <-- 8688 also intercepts @no-think in model name
MB_OPENAI_API_KEY=${MB_OPENAI_API_KEY:-"sk-empty"}
query_chat() {
    logfile="/tmp/$(echo $1 | tr -d '/').log"
    if [ -e "$logfile" ]; then
        rm "$logfile"
    fi
    echo "$2"
    curl -s -X POST "$MB_OPENAI_API_BASE/chat/completions" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MB_OPENAI_API_KEY" \
         -d '{"model": "'"$1"'", "messages": [{"role": "user", "content": "'"$2"'"}]}' | tee $logfile | jq '.choices[0].message.content'
    retcode=${PIPESTATUS[0]}
    echo "curl's retcode=$retcode Full log found in: $logfile"
    return $retcode
}
if [ $# -eq 0 ]; then
    query_chat exllamav2-gemma-3-27b "Answer only with the missing word: The capital of Poland is"
    query_chat llamacpp-Qwen3-Coder-30B-A3B-it "Answer only with the missing word: The capital of Poland is"
    query_chat vllm-Qwen2.5-VL-7B "Answer only with the missing word: The capital of Poland is"
    exit
    #query_chat llamacpp-Qwen3-30B-A3B-it-2507 "What's the captial of Scandinavia? todays date is $(date --iso-8601)"
    #query_chat llamacpp-magistral-small-2507 "What's the captial of Scandinavia? todays date is $(date --iso-8601)"
    #query_chat llamacpp-devstral-small-2507 "What's the captial of Scandinavium? todays date is $(date --iso-8601)"
    query_chat llamacpp-Qwen3-30B-A3B@do-think "What's the captial of Scandinavia? todays date is $(date --iso-8601)" \
    && curl -s http://localhost:8687/lastlog | jq '.'
    exit
    query_chat llamacpp-mistral-small-3.2-24b-2506 "What's the captial of Scandinavia? /no_think"
    exit
    #curl -s http://localhost:8687/lastlog | jq '.'
    query_chat llamacpp-QwQ-32B@think-less "Answer only with the missing word: The capital of Germany is" \
    && curl -s http://localhost:8687/lastlog | jq '.'
    exit
    query_chat llamacpp-Qwen3-1.7B "What's the captial of Scandinavia? /no_think"
    query_chat llamacpp-Qwen3-4B   "What's the captial of Scandinavia? /no_think"
    query_chat llamacpp-devstral-small-2505 "Answer only with the missing word: The capital of Norway is"
    query_chat llamacpp-gemma-3-27b "Answer only with the missing word: The capital of Norway is"
    query_chat llamacpp-Phi-4 "What't the captial of Sweden?"
    query_chat llamacpp-gemma-3-1b"What't the captial of Sweden?"
    query_chat llamacpp-Qwen3-30B-A3B "/no_think Answer only with the missing word: The capital of Greece is"
    query_chat llamacpp-Qwen3-32B "/nothink Answer only with the missing word: The capital of Italy is"
    query_chat llamacpp-Qwen3-30B-A3B-Q6_K "/nothink Answer only with the missing word: The capital of Greece is"
    for quant in 30B-A3B 0.6B 1.7B 4B 4B-128K 8B 14B 32B; do
        query_chat llamacpp-Qwen3-${quant} "Answer only with the missing word: The capital of Belarus is"
    done
    query_chat llamacpp-cydonia-24b-v2.1 "Answer only with the missing word: The capital of Lithuania is"
    query_chat llamacpp-exaone-32b-deep "Answer only with the missing word: The capital of Iceland is"
    query_chat llamacpp-glm-4-32b-0414 "Answer only with the missing word: The capital of Latvia is"
    query_chat llamacpp-llama4-maverick "Answer only with the missing word: The capital of Estonia is"
    query_chat llamacpp-Ling-Coder-lite "Answer only with the missing word: The capital of the Netherlands is"
    query_chat llamacpp-gemma-3-4b"Answer only with the missing word: The capital of Belgium is"
    query_chat llamacpp-Qwen2.5-Coder-32B"Answer only with the missing word: The capital of Sweden is"
    query_chat llamacpp-Mistral-Small-3.1-24B-2503 "Answer only with the missing word: The capital of Finland is"
    query_chat vllm-Qwen-QwQ-32B "Answer only with the missing word: The capital of Latvia is"
else
    query_chat "${@}"
fi
