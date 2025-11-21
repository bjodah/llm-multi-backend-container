#!/bin/bash
if ! which podrun 2>/dev/null; then
    >&2 echo "Could not find 'podrun', see github.com/bjodah/bjodah-tools"
    exit 1
fi
REPO_ROOT="$(realpath $(dirname "${BASH_SOURCE}")/..)"
if [ ! -d "$REPO_ROOT/env-sandbox" ]; then
    >&2 echo "Could not find directory 'env-sandbox' repo-root(?): $REPO_ROOT"
    exit 1
fi
podrun \
    --no-mount-cwd \
    -v $(pwd):/work \
    -w /work \
    -v $REPO_ROOT/configs/.codex:/root/.codex \
    -v $REPO_ROOT/configs/opencode:/root/.config/opencode \
    -v $REPO_ROOT/config/.aider.model.metadata.json:/root/.aider.model.metadata \
    -e TZ \
    -e AIDER_DARK_MODE=true \
    -e LLAMA_API_KEY=sk-empty \
    --cont-img-dir $REPO_ROOT/env-sandbox
