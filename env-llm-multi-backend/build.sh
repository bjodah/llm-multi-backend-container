#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    >&2 echo "Expected exactly one arg"
    exit 1
fi

declare -A builds=(
    [00]=cu132
    [01]=vllm
    [02]=llamacpp
    [03]=llama-swap
    [04]=f2k4b
    [05]=sdcpp
)

num="$1"

if [[ -z "${builds[$num]:-}" ]]; then
    >&2 echo "Unknown build target: $num"
    >&2 echo "Valid targets: ${!builds[*]}"
    exit 1
fi

name="${builds[$num]}"
containerfile="Containerfile.${num}-bjodah-${name}"

podman build \
       --device nvidia.com/gpu=all \
       -t "bjodah/${name}" \
       -f "$containerfile" \
    | tee "$(dirname $0)/../logs/image-build-${num}-bjodah-${name}.log"
