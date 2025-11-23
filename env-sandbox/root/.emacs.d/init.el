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

(load (expand-file-name (concat user-emacs-directory "lisp/use-gptel")))
(load (expand-file-name (concat user-emacs-directory "lisp/use-minuet")))
