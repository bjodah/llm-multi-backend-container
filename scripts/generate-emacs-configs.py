#!/usr/bin/env python
import dataclasses as dcs
import yaml
from pathlib import Path

DEFAULT_PORT=8686
DEFAULT_API_KEY="sk-empty"

@dcs.dataclass
class EmacsConfigElispExporter:
    models: list[str]
    api_key: str = DEFAULT_API_KEY

    def _endpoint(self, *, trailing, port, protocol: str='http'):
        if port is not None:
            port = f':{port}'
        return f'(concat (if (string= (getenv "container") "podman") "{protocol}://host.docker.internal" "{protocol}://localhost") "{port}{trailing}")'

    def gptel(self, port: int=DEFAULT_PORT) -> str:
        """See https://github.com/karthink/gptel"""
        return f"""
(gptel-make-openai "llm-multi-backend"
  :stream t
  :protocol "http"
  :host {self._endpoint(trailing="", port=port)}
  :key "{self.api_key}"
  :models '({' '.join(self.models)})
)
"""

    def minuet(self, port: int=DEFAULT_PORT):
        """See https://github.com/milanglacier/minuet-ai.el"""
        # from https://github.com/milanglacier/minuet-ai.el/blob/main/recipes.md#example-minuet-config
        model = next(filter(lambda s: 'qwen' in s.lower() and 'coder' in s.lower(), self.models))
        return f"""
(defun my-use-llm-multi-backend
    "Configures minuet to use local fim compatible model"
    (interactive)
    (setq minuet-provider 'openai-fim-compatible)
    (setq minuet-n-completions 1)
    (setq minuet-context-window 512)
    (plist-put minuet-openai-fim-compatible-options :end-point {self._endpoint(trailing="/v1/completions", port=port)})
    (plist-put minuet-openai-fim-compatible-options :name "llm-multi-backend")
    (plist-put minuet-openai-fim-compatible-options :api-key "{self.api_key}")
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
    (minuet-set-optional-options minuet-openai-fim-compatible-options :temperature 0.05)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :min_p 0.005)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :top_p 0.95))
"""

    def semext(self, port: int=DEFAULT_PORT):
        #model = next(filter(lambda s: 'gemma-3' in s.lower() and '-1b' in s.lower(), self.models))
        model = next(filter(lambda s: 'qwen3' in s.lower() and '-30b-a3b' in s.lower(), self.models))
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
                           :url {self._endpoint(trailing="/v1/", port=port)}
                           :chat-model "{model}"
                           :key "{self.api_key}"
                           ))
  (cl-defmethod llm-capabilities ((provider llm-openai-compatible))
    '(streaming embeddings tool-use streaming-tool-use json-response model-list image-input))
  (setq llm-warn-on-nonfree nil)
)
"""

if __name__ == '__main__':
    import argh
    with open(Path(__file__).parent / '../configs/llama-swap-config.yaml') as ifh:
        conf = yaml.safe_load(ifh)
    ecee = EmacsConfigElispExporter(models=list(conf['models'].keys()))
    argh.dispatch_commands([ecee.gptel, ecee.minuet, ecee.semext])
