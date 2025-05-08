#!/bin/bash
repo_root="$(cd $(dirname $(realpath "$BASH_SOURCE")); git rev-parse --show-toplevel 2>/dev/null)"
cat $repo_root/configs/llama-swap-config-*.yaml >$repo_root/configs/llama-swap-config.yaml
