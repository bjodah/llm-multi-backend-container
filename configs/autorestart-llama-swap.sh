#!/bin/bash
# Automatically restart llama-swap when it is killed (e.g. to reload config file).
if [ $# -ne 2 ]; then
    echo "Usage: $0 <path to config.yaml> /path/to/output.log"
    exit 1
fi

main() {
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
}

{
    main $*
    exit 0;
}
