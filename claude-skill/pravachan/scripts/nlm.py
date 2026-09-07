#!/usr/bin/env python3
"""
NotebookLM transcription (Selenium + a DEDICATED Firefox automation profile).

Same approach used to build the original sets. SAFETY: dedicated profile only, never
the user's real Firefox profile; never quit their live Firefox.

  python3 nlm.py --login                       # one-time sign-in
  python3 nlm.py <audio_dir> <transcripts_dir> [--profile P] [--chunk 5]

Env: PRAVACHAN_NLM_PROFILE, PRAVACHAN_FF_BIN, PRAVACHAN_GECKODRIVER
"""
from __future__ import annotations
import os, sys, time, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import log, gcount, find_audio

GTHRESH = 400; WAIT_TRANSCRIPT = 900
DEFAULT_PROFILE = os.environ.get("PRAVACHAN_NLM_PROFILE",
                                 os.path.expanduser("~/.pravachan-notebooklm-firefox"))
def _clean(raw): return "\n".join(l.strip() for l in (raw or "").splitlines() if gcount(l) > 0).strip()

def _ff_bin():
    b = os.environ.get("PRAVACHAN_FF_BIN")
    if b and os.path.exists(b): return b
    for c in ("/Applications/Firefox.app/Contents/MacOS/firefox", "/usr/bin/firefox", shutil.which("firefox")):
        if c and os.path.exists(c): return c
    raise SystemExit("Firefox not found — set PRAVACHAN_FF_BIN")

def _gecko():
    g = os.environ.get("PRAVACHAN_GECKODRIVER") or shutil.which("geckodriver") or "/opt/homebrew/bin/geckodriver"
    if not os.path.exists(g): raise SystemExit("geckodriver not found — brew install geckodriver")
    return g

def _driver(profile):
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    o = Options(); o.binary_location = _ff_bin()
    o.add_argument("-profile"); o.add_argument(profile)
    d = webdriver.Firefox(service=Service(_gecko()), options=o); d.set_window_size(1400, 1000); return d

JS_BEST = r"""
const isG=c=>c>=0x0A80&&c<=0x0AFF;function gc(t){let n=0;for(const ch of t){if(isG(ch.codePointAt(0)))n++;}return n;}
let best='',bs=0;for(const el of document.querySelectorAll('div,section,article,p,span')){
const t=el.innerText||'';const g=gc(t);if(g>bs&&t.length<300000){bs=g;best=t;}}return best;"""

def _click(d, texts):
    from selenium.webdriver.common.by import By
    for t in texts:
        for xp in [f"//button[normalize-space()='{t}']", f"//*[normalize-space(text())='{t}']",
                   f"//button[contains(normalize-space(.),'{t}')]", f"//*[contains(normalize-space(text()),'{t}')]"]:
            for e in d.find_elements(By.XPATH, xp):
                if e.is_displayed():
                    try: e.click(); return True
                    except Exception:
                        try: d.execute_script("arguments[0].click();", e); return True
                        except Exception: pass
    return False

def _dismiss(d):
    from selenium.webdriver.common.by import By
    for xp in ["//button[@aria-label='Close']", "//button[contains(@aria-label,'Close')]",
               "//button[normalize-space()='Got it']"]:
        for e in d.find_elements(By.XPATH, xp):
            if e.is_displayed():
                try: e.click(); return True
                except Exception:
                    try: d.execute_script("arguments[0].click();", e); return True
                    except Exception: pass
    return False

def _ext(p: Path):
    if p.suffix: return p.suffix
    with p.open("rb") as fh: h = fh.read(16)
    return ".m4a" if h[4:8] == b"ftyp" else ".mp3"

def transcribe_dir(audio_dir: Path, trans_dir: Path, profile=DEFAULT_PROFILE, chunk=5, wait=WAIT_TRANSCRIPT):
    from selenium.webdriver.common.by import By
    audio = find_audio(audio_dir)
    todo = [(a, trans_dir / a.relative_to(audio_dir).with_suffix(a.suffix + ".txt")) for a in audio]
    todo = [(a, o) for a, o in todo if not (o.exists() and gcount(o.read_text(encoding="utf-8")) >= GTHRESH)]
    log("nlm", f"{len(todo)}/{len(audio)} to transcribe (profile={profile}, chunk={chunk})")
    if not todo: return
    stage = Path(profile + "_stage"); stage.mkdir(parents=True, exist_ok=True)
    d = _driver(profile); nb = {"url": None}; seen = set()

    def new_nb():
        d.get("https://notebook.google.com"); time.sleep(8)
        if "accounts.google.com" in d.current_url:
            raise SystemExit("NotebookLM profile is NOT logged in — run: python3 nlm.py --login")
        _click(d, ["Create new notebook", "Create new"]); time.sleep(7)
        if _dismiss(d): time.sleep(2)
        url = d.current_url.split("?")[0]
        if "/notebook/" not in url:            # create failed — almost always the notebook cap
            page = ""
            try: page = d.find_element("tag name", "body").text
            except Exception: pass
            if "maximum number of notebooks" in page or "Failed to create notebook" in page:
                raise SystemExit(
                    "NotebookLM ACCOUNT IS AT ITS NOTEBOOK LIMIT (couldn't create a new notebook).\n"
                    "Fix: run `python3 nlm.py --login` and sign in with a DIFFERENT Google account\n"
                    "(a fresh account has an empty notebook quota) — or delete old notebooks / upgrade.")
            raise SystemExit(f"NotebookLM did not open a new notebook (still at {url}). "
                             "Try `python3 nlm.py --login` with a different account.")
        nb["url"] = url; log("nlm", "new notebook", nb["url"])
    try:
        for i, (a, out) in enumerate(todo):
            if i % chunk == 0: new_nb(); seen = set()
            tag = f"pv{i:03d}{_ext(a)}"; sp = stage / tag; shutil.copy2(a, sp)
            d.get(nb["url"]); time.sleep(7)
            if _dismiss(d): time.sleep(2)
            # A fresh notebook auto-opens the upload dialog (no 'Add sources' button); an
            # existing one needs the button. Try to click it (best effort), then find the
            # file input directly — the dialog may already be open.
            _click(d, ["Add sources", "add a source"]); time.sleep(3)   # open the source dialog
            _click(d, ["Upload files", "Upload"]); time.sleep(3)         # choose 'Upload files' → reveals input
            finp = None
            for _ in range(15):
                inps = d.find_elements(By.CSS_SELECTOR, "input[type=file]")
                if inps: finp = inps[-1]; break
                _click(d, ["Upload files", "Upload"]); time.sleep(2)
            if not finp: log("nlm", "no file input for", a.name); continue
            finp.send_keys(str(sp)); log("nlm", "uploaded", a.name); time.sleep(8)
            _click(d, [tag]); time.sleep(4)
            best = ""; dl = time.time() + wait
            while time.time() < dl:
                _click(d, [tag])
                try: best = d.execute_script(JS_BEST) or ""
                except Exception: best = ""
                if gcount(best) >= GTHRESH and best not in seen: break
                time.sleep(15)
            c = _clean(best)
            if gcount(c) >= GTHRESH and best not in seen:
                out.parent.mkdir(parents=True, exist_ok=True); out.write_text(c, encoding="utf-8")
                seen.add(best); log("nlm", f"  ✓ {out.name} ({gcount(c)} chars)")
            else:
                log("nlm", f"  ✗ {a.name}: short/dup ({gcount(c)} chars)")
    finally:
        try: d.quit()
        except Exception: pass

def login(profile=DEFAULT_PROFILE):
    """Open the dedicated profile as a NORMAL Firefox instance (NOT Selenium) so Google
    permits sign-in — webdriver-controlled browsers are blocked at login. Selenium then
    reuses this logged-in profile for transcription."""
    import subprocess, sys as _sys
    os.makedirs(profile, exist_ok=True)
    url = "https://notebook.google.com"
    log("nlm", f"opening dedicated profile as a normal Firefox window: {profile}")
    if _sys.platform == "darwin":
        subprocess.Popen(["open", "-n", "-a", "Firefox", "--args",
                          "-profile", profile, "-no-remote", url])
    else:
        subprocess.Popen([_ff_bin(), "-profile", profile, "-no-remote", url])
    print("\n>>> A normal Firefox window opened on the dedicated profile.")
    print(">>> Sign in to Google/NotebookLM there. Your login is saved to this profile;")
    print(">>> transcription will reuse it. You can close the window when signed in.\n")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_dir", nargs="?"); ap.add_argument("trans_dir", nargs="?")
    ap.add_argument("--login", action="store_true")
    ap.add_argument("--profile", default=DEFAULT_PROFILE); ap.add_argument("--chunk", type=int, default=5)
    a = ap.parse_args()
    if a.login: login(a.profile); return
    if not a.audio_dir or not a.trans_dir: raise SystemExit("usage: nlm.py <audio_dir> <trans_dir>  (or --login)")
    transcribe_dir(Path(a.audio_dir), Path(a.trans_dir), a.profile, a.chunk)

if __name__ == "__main__":
    main()
