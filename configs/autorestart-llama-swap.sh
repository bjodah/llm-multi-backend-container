#!/bin/bash
#
#  From: https://github.com/mostlygeek/llama-swap/tree/main/examples/restart-on-config-change
#
# A simple watch and restart llama-swap when its configuration
# file changes. Useful for trying out configuration changes
# without manually restarting the server each time.
if [ $# -ne 2 ]; then
    echo "Usage: $0 <path to config.yaml> /path/to/output.log"
    exit 1
fi

# temp_file="/tmp/watch-and-restart-llama-swap_$$"
while true; do
    # Start the process again
    >&2 echo -n "Starting llama-swap..."
    /usr/local/bin/llama-swap -config $1 -listen :8686 2>&1 >$2 &
    PID=$!
    sleep 0.1
    # Check if process exists before sending signal
    if kill -0 $PID 2>/dev/null; then
        >&2 echo "successfully started with pid: $PID"
        wait $PID
    else
        >&2 echo "failed to start llama-swap, dumping log and exiting:"
        cat $2 >&2
        exit 1
    fi
    sleep 0.1
done
