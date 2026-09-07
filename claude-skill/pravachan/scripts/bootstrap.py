#!/usr/bin/env python3
"""
bootstrap.py — make the machine ready. Installs anything missing:
  • pip packages: selenium, yt-dlp, gdown, weasyprint, python-docx, beautifulsoup4, anthropic
  • system tools (via brew if present): ffmpeg, geckodriver, firefox, pango, Gujarati fonts
Prints a readiness report. Exit 0 = ready; exit 2 = manual action needed.

  python3 bootstrap.py            # install what's missing
  python3 bootstrap.py --check    # report only, install nothing
"""
from __future__ import annotations
import importlib.util, shutil, subprocess, sys

PIP = {"selenium": "selenium", "yt_dlp": "yt-dlp", "gdown": "gdown", "weasyprint": "weasyprint",
       "docx": "python-docx", "bs4": "beautifulsoup4", "anthropic": "anthropic"}
BREW_FORMULAE = {"ffmpeg": "ffmpeg", "geckodriver": "geckodriver", "pango": "pango"}
BREW_CASKS = {"firefox": ("firefox", "/Applications/Firefox.app"),
              "noto-serif-gujarati": ("font-noto-serif-gujarati", None),
              "noto-sans-gujarati": ("font-noto-sans-gujarati", None)}

def have_mod(m): return importlib.util.find_spec(m) is not None
def have_bin(b): return shutil.which(b) is not None
def run(cmd): return subprocess.run(cmd).returncode == 0

def ensure_pip(check):
    missing = [pkg for mod, pkg in PIP.items() if not have_mod(mod)]
    if not missing: print("pip deps: OK"); return True
    print("pip missing:", ", ".join(missing))
    if check: return False
    return run([sys.executable, "-m", "pip", "install", "--quiet", *missing])

def ensure_brew(check):
    brew = shutil.which("brew")
    ok = True
    for binname, formula in BREW_FORMULAE.items():
        if have_bin(binname): continue
        ok = False; print(f"missing tool: {binname}")
        if not check and brew: run(["brew", "install", formula])
    # firefox / fonts
    import os
    if not os.path.exists("/Applications/Firefox.app") and not have_bin("firefox"):
        ok = False; print("missing: Firefox")
        if not check and brew: run(["brew", "install", "--cask", "firefox"])
    for name, (cask, _) in list(BREW_CASKS.items())[1:]:
        if not check and brew: run(["brew", "install", "--cask", cask])
    if not brew and not ok:
        print("⚠️ Homebrew not found — install ffmpeg, geckodriver, firefox, pango + Noto Gujarati fonts manually.")
    return ok or (brew is not None and not check)

def main():
    check = "--check" in sys.argv
    print("=== pravachan bootstrap ===")
    a = ensure_pip(check)
    b = ensure_brew(check)
    # re-verify the essentials actually resolve now
    ready = all(have_mod(m) for m in PIP) and have_bin("ffmpeg") and \
            (have_bin("geckodriver")) and (have_bin("firefox") or __import__("os").path.exists("/Applications/Firefox.app"))
    print("=== ready:", ready, "===")
    sys.exit(0 if ready else 2)

if __name__ == "__main__":
    main()
