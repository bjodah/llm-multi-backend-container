#!/usr/bin/env python
import yaml
from pathlib import Path

API_KEY="sk-empty"
def _endpoint(*, trailing):
    return f'(concat (if (string= (getenv "container") "podman") "http://host.docker.internal" "http://localhost") ":8686{trailing}")'
with open(Path(__file__).parent / '../configs/llama-swap-config.yaml') as ifh:
    conf = yaml.safe_load(ifh)
    models = conf['models'].keys()

def gptel():
    """See https://github.com/karthink/gptel"""
    return f"""
(gptel-make-openai "llm-multi-backend"
  :stream t
  :protocol "http"
  :host {_endpoint(trailing="")}
  :key "{API_KEY}"
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
    (plist-put minuet-openai-fim-compatible-options :end-point {_endpoint(trailing="/v1/completions")})
    (plist-put minuet-openai-fim-compatible-options :name "llm-multi-backend")
    (plist-put minuet-openai-fim-compatible-options :api-key "{API_KEY}")
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
    (minuet-set-optional-options minuet-openai-fim-compatible-options :max_tokens 56)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :temperature 0.123)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :min_p 0.0)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :top_p 0.95))
"""

def semext():
    model = next(filter(lambda s: 'gemma-3' in s.lower() and '-1b' in s.lower(), models))
    return f"""
(use-package semext
  :vc (
       :url "https://github.com/ahyatt/semext"
            :rev :newest
            :branch "main"
            )
  :ensure t
  :init
  (require 'llm-openai) ;; <- provides "make-llm-openai-compatible"
  ;; Replace provider with whatever you want, see https://github.com/ahyatt/llm
  (setopt semext-provider (make-llm-openai-compatible
                           :url {_endpoint(trailing="/v1/")}
                           :chat-model "{model}"
                           :key "{API_KEY}"
                           ))
  (cl-defmethod llm-capabilities ((provider llm-openai-compatible))
    '(streaming embeddings tool-use streaming-tool-use json-response model-list image-input))
  (setq llm-warn-on-nonfree nil)
)
"""

if __name__ == '__main__':
    import argh
    argh.dispatch_commands([gptel, minuet, semext])
