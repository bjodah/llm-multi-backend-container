#!/bin/bash
OPENAI_API_BASE=http://localhost:8686/v1 #${OPENAI_API_BASE:-http://localhost:8686/v1}
OPENAI_API_KEY=sk-empty # ${OPENAI_API_KEY:-sk-empty}
query_chat() {
    logfile="/tmp/$(echo $1 | tr -d '/').log"
    if [ -e "$logfile" ]; then
        rm "$logfile"
    fi
    curl -s -X POST "$OPENAI_API_BASE/chat/completions" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $OPENAI_API_KEY" \
         -d '{"model": "'"$1"'", "messages": [{"role": "user", "content": "'"$2"'"}]}' | tee $logfile | jq '.choices[0].message.content'
    echo "Full log found in: $logfile"
}
if [ $# -eq 0 ]; then
    query_chat exllamav2-gemma-3-27b "What't the captial of Sweden?"
    exit
    query_chat llamacpp-Phi-4 "What't the captial of Sweden?"
    query_chat llamacpp-gemma-3-1b-it "What't the captial of Sweden?"
    query_chat llamacpp-Qwen3-30B-A3B "/no_think Answer only with the missing word: The capital of Greece is"
    query_chat llamacpp-Qwen3-1.7B "/no_think What't the captial of Sweden?"
    query_chat llamacpp-Qwen3-32B "/nothink Answer only with the missing word: The capital of Italy is"
    query_chat llamacpp-Qwen3-30B-A3B-Q6_K "/nothink Answer only with the missing word: The capital of Greece is"
    for quant in 30B-A3B 0.6B 1.7B 4B 4B-128K 8B 14B 32B; do
        query_chat llamacpp-Qwen3-${quant} "Answer only with the missing word: The capital of Belarus is"
    done
    query_chat llamacpp-cydonia-24b-v2.1 "Answer only with the missing word: The capital of Lithuania is"
    query_chat llamacpp-exaone-32b-deep "Answer only with the missing word: The capital of Iceland is"
    query_chat llamacpp-glm-4-32b-0414 "Answer only with the missing word: The capital of Latvia is"
    query_chat llamacpp-llama4-maverick "Answer only with the missing word: The capital of Estonia is"
    query_chat vllm-Qwen-QwQ-32B "Answer only with the missing word: The capital of Latvia is"
    query_chat llamacpp-Ling-Coder-lite "Answer only with the missing word: The capital of the Netherlands is"
    query_chat vllm-SmolLM2-1.7B-Instruct "Answer only with the missing word: The capital of Poland is"
    query_chat llamacpp-gemma-3-4b-it "Answer only with the missing word: The capital of Belgium is"
    query_chat llamacpp-Qwen2.5-Coder-32B-Instruct "Answer only with the missing word: The capital of Sweden is"
    query_chat llamacpp-QwQ-32B "Answer only with the missing word: The capital of Germany is"
    query_chat llamacpp-gemma-3-27b-it "Answer only with the missing word: The capital of Norway is"
    query_chat llamacpp-Mistral-Small-3.1-24B-Instruct-2503 "Answer only with the missing word: The capital of Finland is"
else
    query_chat "${@}"
fi
