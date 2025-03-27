#!/bin/bash
OPENAI_API_BASE=${OPENAI_API_BASE:-http://localhost:8686/v1}
OPENAI_API_KEY=${OPENAI_API_KEY:-duck123}
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
query_chat llamacpp-Qwen2.5-Coder-32B-Instruct "Answer only with the missing word: The capital of Sweden is"
query_chat llamacpp-QwQ-32B "Answer only with the missing word: The capital of Germany is"
query_chat llamacpp-gemma-3-27b-it "Answer only with the missing word: The capital of Norway is"
query_chat llamacpp-Mistral-Small-3.1-24B-Instruct-2503 "Answer only with the missing word: The capital of Finland is"

# query_chat exllamav2-Qwen2.5-Coder-14B-Instruct "Answer only with the missing word: The capital of Iceland is"

# query_chat vllm-SmolLM2-1.7B-Instruct "Answer only with the missing word: The capital of Poland is"
# query_chat exllamav2-QwQ-32B "Answer only with the missing word: The capital of Denmark is"
