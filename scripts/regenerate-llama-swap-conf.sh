#!/bin/bash
repo_root="$(cd $(dirname $(realpath "$BASH_SOURCE")); git rev-parse --show-toplevel 2>/dev/null)"

conf() {
    echo "$repo_root/configs/llama-swap-config-$1.yaml"
}
srcs+=( $(conf base) )
if [ -e $(conf local) ]; then
    srcs+=( $(conf local) )
fi
cat "${srcs[@]}" >$repo_root/configs/llama-swap-config.yaml
