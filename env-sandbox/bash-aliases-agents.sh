alias aider-local="env OPENAI_API_KEY=sk-empty OPENAI_API_BASE=http://host.docker.internal:8686/v1 aider --model openai/vllm-Qwen3-Coder-30B --no-gitignore"
alias claude-code-local="ccr code"  # see .claude-code-router/config.json
alias codex-q3c="codex --model vllm-Qwen3-Coder-30B"  # see .codex/config.toml
alias opencode-local="opencode --model llamaswap/vllm-Qwen3-Coder-30B"  # see opencode/config.json
alias qwen-local="env OPENAI_API_KEY=sk-empty OPENAI_BASE_URL=http://host.docker.internal:8688/v1 OPENAI_MODEL=vllm-Qwen3-Coder-30B qwen"
