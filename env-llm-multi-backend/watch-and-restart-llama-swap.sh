#!/bin/bash
#
#  From: https://github.com/mostlygeek/llama-swap/tree/main/examples/restart-on-config-change
#
# A simple watch and restart llama-swap when its configuration
# file changes. Useful for trying out configuration changes
# without manually restarting the server each time.
if [ -z "$1" ]; then
    echo "Usage: $0 <path to config.yaml>"
    exit 1
fi

while true; do
    # Start the process again
    /usr/local/bin/llama-swap -config $1 -listen :8686 &
    PID=$!
    >&2 echo "Started llama-swap with PID $PID"

    # Wait for modifications in the specified directory or file
    inotifywait -e modify "$1"

    # Check if process exists before sending signal
    if kill -0 $PID 2>/dev/null; then
        >&2 echo "Sending SIGTERM to $PID (timeout 10s)"
        timeout 10s kill -SIGTERM $PID
        wait $PID
        if kill -0 $PID 2>/dev/null; then
            >&2 echo "Sending SIGKILL to $PID"
            kill -SIGKILL $PID
        fi
        wait $PID
    else
        echo "Process $PID no longer exists"
    fi
    sleep 1
done
