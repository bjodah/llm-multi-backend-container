#!/usr/bin/env python
import yaml
from pathlib import Path

with open(Path(__file__).parent / '../configs/llama-swap-config.yaml') as ifh:
    conf = yaml.safe_load(ifh)
    models = conf['models'].keys()

def gptel():
    """See https://github.com/karthink/gptel"""
    return f"""
(gptel-make-openai "llm-multi-backend"
  :stream t
  :protocol "http"
  :host "localhost:8686"
  :key "sk-empty"
  :models '({' '.join(models)})
)
"""

def minuet():
    """See https://github.com/milanglacier/minuet-ai.el"""
    # from https://github.com/milanglacier/minuet-ai.el/blob/main/recipes.md#example-minuet-config
    model = next(filter(lambda s: 'qwen' in s.lower() and 'coder' in s.lower(), models))
    return f"""
(defun my-use-llm-multi-backend
    "Configures minuet to use local fim compatible model"
    (interactive)
    (setq minuet-provider 'openai-fim-compatible)
    (setq minuet-n-completions 1)
    (setq minuet-context-window 512)
    (plist-put minuet-openai-fim-compatible-options :end-point "http://localhost:8686/v1/completions")
    (plist-put minuet-openai-fim-compatible-options :name "llm-multi-backend")
    (plist-put minuet-openai-fim-compatible-options :api-key "sk-empty")
    (plist-put minuet-openai-fim-compatible-options :model "{model}")
    (minuet-set-optional-options minuet-openai-fim-compatible-options :suffix nil :template)
    (minuet-set-optional-options
     minuet-openai-fim-compatible-options
     :prompt
     (defun minuet-llama-cpp-fim-qwen-prompt-function (ctx)
         (format "<|fim_prefix|>%s\\n%s<|fim_suffix|>%s<|fim_middle|>"
                 (plist-get ctx :language-and-tab)
                 (plist-get ctx :before-cursor)
                 (plist-get ctx :after-cursor)))
     :template)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :max_tokens 56))
"""

if __name__ == '__main__':
    import argh
    argh.dispatch_commands([gptel, minuet])
