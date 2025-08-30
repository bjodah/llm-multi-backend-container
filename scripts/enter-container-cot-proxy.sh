#!/bin/bash
podman exec --detach-keys=ctrl-\]  -it llm-mb_cot-proxy "${@:-/bin/bash}"
