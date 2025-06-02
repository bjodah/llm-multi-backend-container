#!/bin/bash
podman exec --detach-keys=ctrl-\]  -it llm-mb_llama-swapper "${@:-/bin/bash}"
