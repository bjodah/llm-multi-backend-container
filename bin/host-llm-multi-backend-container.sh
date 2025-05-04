#!/bin/bash
set -u
show_help() {
    echo "Usage:"
    echo "  \$ $(basename $0) --detach --build --force-recreate"
}
repo_root="$(cd $(dirname $(realpath "$BASH_SOURCE")); git rev-parse --show-toplevel 2>/dev/null)"

if [ ! -e "$repo_root"/compose.yml ]; then
    >&2 echo "$BASH_SOURCE:$BASH_LINENO: Could not find the compose.yml file in: $repo_root"
    exit 1
fi
if which podman 2>&1 >/dev/null; then
    if podman compose --help 2>&1 >/dev/null; then
        COMPOSE_CMD="podman compose"
    else
        if ! which podman-compose 2>&1 >/dev/null; then
            uv pip install podman-compose  # maybe too helpful?
        fi
        COMPOSE_CMD="podman-compose"
    fi
else
    COMPOSE_CMD="docker-compose"
fi
if [ ! -v HUGGING_FACE_HUB_TOKEN ]; then
    >&2 echo "No environment variable HUGGING_FACE_HUB_TOKEN?"
    exit 1
fi
declare -a srcs

if [ -e "$repo_root/configs/llama-swap-config-local.yaml" ]; then
    srcs+=( "$repo_root/configs/llama-swap-config-local.yaml" )
fi
cat ${srcs[@]} >$repo_root/configs/llama-swap-config.yaml

echo "You can view open-webui: $ xdg-open http://localhost:33033/"
( set -x; env \
    HOST_CACHE_HUGGINGFACE="$(realpath $HOME/.cache/huggingface)" \
    HOST_CACHE_LLAMACPP="$(realpath $HOME/.cache/llama.cpp)" \
    $COMPOSE_CMD \
    --file "$repo_root"/compose.yml \
    up "$@" )


