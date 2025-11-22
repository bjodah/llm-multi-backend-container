;;; init.el

(require 'package)
(add-to-list 'package-archives
             '("melpa" . "https://melpa.org/packages/") t)
(add-to-list 'package-archives
             '("gnu" . "http://elpa.gnu.org/packages/") t)
(package-initialize)

(unless (package-installed-p 'use-package)
  (progn
    (package-refresh-contents)
    (package-install 'use-package)))

(use-package emacs
  :ensure nil
  :custom
  (kill-do-not-save-duplicates t)
  (add-hook 'text-mode-hook 'visual-line-mode)
  (require-theme 'modus-themes)
  (setq modus-themes-common-palette-overrides
        modus-themes-preset-overrides-intense)
  :config
  (load-theme 'modus-vivendi-tritanopia)
  )

(use-package gptel
  :vc (:url "https://github.com/karthink/gptel"
            :rev :newest
            :branch "main")
  :ensure t
  :config
  (setq
   gptel-api-key (lambda () (getenv "OPENAI_API_KEY"))
   gptel-model 'vllm-Qwen3-Coder-30B
   gptel-expert-commands t
   )
  :bind (("C-c M-." . 'gptel-send)
         ("C-c M-/" . 'gptel-rewrite)
         ("C-c M->" . (lambda ()
                      (interactive)
                      (let ((buffer (get-buffer "*gptel*")))
                        (if buffer
                            (let ((window (get-buffer-window buffer)))
                              (if window
                                  (select-window window)
                                (gptel "*gptel*")
                                ))
                          (gptel "*gptel*"))
                        (let ((window (get-buffer-window "*gptel*")))
                          (if window (select-window window)
                            (switch-to-buffer "*gptel*")))))))
  )

(setq gptel-backend
      (gptel-make-openai "llm-multi-backend"
        :stream t
        :protocol "http"
        :host (concat (if (string= (getenv "container") "podman") "host.docker.internal" "localhost") ":8688")
        :key "sk-empty"
        :models '(vllm-Qwen3-Coder-30B llamacpp-gpt-oss-120b llamacpp-glm-4.5-air)))

(use-package minuet
  :vc (
       :url "https://github.com/milanglacier/minuet-ai.el"
            :rev :newest
            :branch "main"
            )
  :ensure t
  :bind
  (("C-c M-O" . #'minuet-complete-with-minibuffer) ;; use minibuffer for completion
   ("M-I" . #'minuet-show-suggestion) ;; use overlay for completion
   ("C-c M-P" . #'minuet-configure-provider)
     :map minuet-active-mode-map
     ;; These keymaps activate only when a minuet suggestion is displayed in the current buffer
     ("M-p" . #'minuet-previous-suggestion) ;; invoke completion or cycle to next completion
     ("M-n" . #'minuet-next-suggestion) ;; invoke completion or cycle to previous completion
     ("M-A" . #'minuet-accept-suggestion) ;; accept whole completion
     ;; Accept the first line of completion, or N lines with a numeric-prefix:
     ;; e.g. C-u 2 M-a will accepts 2 lines of completion.
     ("M-a" . #'minuet-accept-suggestion-line)
     ("M-e" . #'minuet-dismiss-suggestion))

    :init
    ;; if you want to enable auto suggestion.
    ;; Note that you can manually invoke completions without enable minuet-auto-suggestion-mode

    :config
    (setq minuet-n-completions 4)
    
    (plist-put minuet-openai-fim-compatible-options :end-point
               (concat (if (string= (getenv "container") "podman") "http://host.docker.internal" "http://localhost")
                       ":8686/v1/completions"))
    (plist-put minuet-openai-fim-compatible-options :name "llama-swap-completions")
    (plist-put minuet-openai-fim-compatible-options :api-key (defun my-llama-swap-key () "sk-empty"))
    (plist-put minuet-openai-fim-compatible-options :model "vllm-Qwen3-Coder-30B")
    (minuet-set-optional-options minuet-openai-fim-compatible-options :temperature 0.05)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :suffix nil :template)
    (minuet-set-optional-options
     minuet-openai-fim-compatible-options
     :prompt
     (defun minuet-llama-cpp-fim-qwen-prompt-function (ctx)
         (format "<|fim_prefix|>%s\n%s<|fim_suffix|>%s<|fim_middle|>"
                 (plist-get ctx :language-and-tab)
                 (plist-get ctx :before-cursor)
                 (plist-get ctx :after-cursor)))
     :template)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :max_tokens 256) ; tg ~= 35 t/s
    (minuet-set-optional-options minuet-openai-fim-compatible-options :temperature 0.07)
    (minuet-set-optional-options minuet-openai-fim-compatible-options :seed 42) ; deterministic
    (setq minuet-n-completions 2)
    (setq minuet-context-window 8192) ;; pp ~= 800 t/s, 4k chars ~= 1000 tokens
    (setq minuet-provider 'openai-fim-compatible)
    (setq minuet-auto-suggestion-throttle-delay 0.5)
    (setq minuet-auto-suggestion-debounce-delay 0.2)
    (setq minuet-request-timeout 7.0)
    ;; You can use M-x minuet-configure-provider to interactively configure provider and model
    )
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(package-selected-packages nil)
 '(package-vc-selected-packages
   '((minuet :url "https://github.com/milanglacier/minuet-ai.el" :branch
	     "main")
     (gptel :url "https://github.com/karthink/gptel" :branch "main"))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
