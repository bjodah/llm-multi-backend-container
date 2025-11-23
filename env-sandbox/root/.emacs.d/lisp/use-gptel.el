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

;; Gemini 3 Pro helped writing the dynamic fetching of model info below:

(require 'json)
(require 'map)

(defun llama-swap-get-host ()
  "Return the appropriate host address based on the container environment."
  (if (string= (getenv "container") "podman")
      "host.docker.internal"
    "localhost"))

(defun llama-swap-fetch-models ()
  "Dynamically fetch models from llama-swap.
Parses keys as keywords to ensure plist-get works correctly."
  (let ((url (format "http://%s:8686/v1/models" (llama-swap-get-host)))
        (curl-args '("-s" "-X" "GET" "-H" "Authorization: Bearer sk-empty")))
    (condition-case err
        (with-temp-buffer
          (apply #'call-process "curl" nil t nil (append curl-args (list url)))
          (goto-char (point-min))
          
          ;; Debugging: Uncomment the next line if you still get issues
          ;; (message "Raw JSON: %s" (buffer-string))

          (if (= (point-min) (point-max))
              (error "Empty response from llama-swap")
            (let* ((json-object-type 'plist)
                   (json-array-type 'list)
                   (json-key-type 'keyword)
                   (resp (json-read))
                   (data (plist-get resp :data)))
              
              (unless data
                (error "JSON parsed, but :data field was missing or nil"))

              (mapcar (lambda (m)
                        (let ((id (intern (plist-get m :id)))
                              (ctx (map-nested-elt m '(:meta :llamaswap :context_window))))
                          (if ctx
                              (list id :context-window ctx :capabilities '(tool))
                            id)))
                      data))))
      (error
       (message "gptel: Model fetch error: %s" err)
       ;; Return a minimal fallback so gptel doesn't break completely
       '(vllm-Qwen3-Coder-30B llamacpp-gpt-oss-120b)))))

(setq gptel-backend
      (gptel-make-openai "llm-multi-backend"
        :stream t
        :protocol "http"
        :host (format "%s:8688" (llama-swap-get-host))
        :key "sk-empty"
        :models (llama-swap-fetch-models)))

