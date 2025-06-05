#!/bin/bash
set -e
model_name=$(curl -s localhost:8686/running | jq ".running[0].model")
if echo $model_name | grep -E "^null$" >/dev/null; then
   exit 1  # no model running
fi
if ! echo $model_name | grep -E '^"llamacpp-'; then
    echo "NIL"  # Not ImpLemented
    exit 0
fi
# it would be tempting to use llama-swap's /upstream/<model_name> endpoint here, but that
# could possibly reload the model if it just evicted (race-condition), instead, we figure out what
# port llama-server is running on 
podman exec -i llm-mb_llama-swapper /bin/bash <<-'EOF'
PORT=$(ps aux | grep ' llama-server' | grep -v 'grep ' | sed -E 's/.*--port ([^ ]+).*/\1/')
while true; do
    curl -sH "Authorization: Bearer sk-empty" http://localhost:${PORT}/slots | jq ".[0].next_token.n_decoded"
    sleep 1.0s
done
EOF
