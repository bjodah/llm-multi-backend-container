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
CACHE_DIR="$HOME/.cache/llm-multi-backend-container"
if [ ! -d "$CACHE_DIR" ]; then
    mkdir -p "$CACHE_DIR"
fi
main() {
    export GIT_AUTHOR_EMAIL="$(git config user.email)"
    export GIT_AUTHOR_NAME="$(git config user.name)"
    podrun \
        --no-mount-cwd \
        -v $(pwd):/work \
        -w /work \
        -v $CACHE_DIR:/cache \
        -v $REPO_ROOT/env-sandbox/root/.emacs.d/init.el:/root/.emacs.d/init.el \
        -v $REPO_ROOT/configs/.codex:/root/.codex \
        -v $REPO_ROOT/configs/opencode:/root/.config/opencode \
        -v $REPO_ROOT/configs/.aider.model.metadata.json:/root/.aider.model.metadata.json \
        -v $REPO_ROOT/configs/.claude-code-router:/root/.claude-code-router \
        -e AIDER_DARK_MODE=true \
        -e LLAMA_API_KEY=sk-empty \
        -e GIT_AUTHOR_EMAIL \
        -e GIT_AUTHOR_NAME \
        --cont-img-dir $REPO_ROOT/env-sandbox \
        -- bash "$@"
}
{
    main "$@"
    exit $?
}
