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
main() {
    declare -a srcs
    set -e
    $repo_root/scripts/regenerate-llama-swap-conf.sh
    ( if [[ $(compgen -G "$repo_root"/logs/*.log.bak.~*~) != "" ]]; then set -x; rm "$repo_root"/logs/*.log.bak.~*~; fi )
    ( set -xo pipefail; cd $repo_root; \
      podman build \
             --device nvidia.com/gpu=all \
             --build-arg="TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST:-8.6}" \
             --build-arg="CUDA_ARCHITECTURES=${CUDA_ARCHITECTURES:-86}" \
             env-llm-multi-backend/ 2>&1 | tee ./logs/image-build.log
    )

    trap "$COMPOSE_CMD --file ${repo_root}/compose.yml down" TERM INT
    echo "You can view open-webui: $ xdg-open http://localhost:33033/"
    ( set -x; env \
                  HOST_CACHE_HUGGINGFACE="$(realpath $HOME/.cache/huggingface)" \
                  HOST_CACHE_LLAMACPP="$(realpath $HOME/.cache/llama.cpp)" \
                  $COMPOSE_CMD --file "$repo_root"/compose.yml up "$@" ) 
}
{
    main "${@}"
    exit 0;
}
