#!/usr/bin/env python3
"""
NotebookLM transcription engine (Selenium + a DEDICATED Firefox automation profile).

This is the same approach used to build the original sets: drive NotebookLM ("Gemini
Notebook") in a persistent Firefox profile, upload each audio file, and read the clean
Gujarati transcript from the viewer that auto-opens right after upload (the only reliable
state — switching sources corrupts/duplicates). Rotates to a fresh notebook every
`chunk` files so no notebook exceeds the source limit. Resumable.

SAFETY: use a DEDICATED automation profile, never the user's real Firefox profile, and
never quit their live Firefox. Log in once (see `pravachan-nlm-login`).

Config (env overrides, else auto-detected):
    PRAVACHAN_NLM_PROFILE   Firefox profile dir  (default ~/.pravachan-notebooklm-firefox)
    PRAVACHAN_FF_BIN        Firefox binary       (default /Applications/Firefox.app/…/firefox)
    PRAVACHAN_GECKODRIVER   geckodriver path     (default: `which geckodriver`)
"""
from __future__ import annotations
import os, re, sys, time, shutil, shlex, subprocess
from pathlib import Path

GTHRESH = 400            # min Gujarati chars for a transcript to count as real
WAIT_TRANSCRIPT = 900    # seconds to wait for NotebookLM to render a transcript

DEFAULT_PROFILE = os.path.expanduser("~/.pravachan-notebooklm-firefox")

def log(*a): print("[nlm]", *a, flush=True)
def gcount(s): return len(re.findall(r"[઀-૿]", s or ""))
def clean(raw): return "\n".join(l.strip() for l in (raw or "").splitlines() if gcount(l) > 0).strip()

def _ff_bin():
    b = os.environ.get("PRAVACHAN_FF_BIN")
    if b and os.path.exists(b): return b
    for c in ("/Applications/Firefox.app/Contents/MacOS/firefox",
              "/usr/bin/firefox", shutil.which("firefox")):
        if c and os.path.exists(c): return c
    raise SystemExit("Firefox not found — set PRAVACHAN_FF_BIN")

def _geckodriver():
    g = os.environ.get("PRAVACHAN_GECKODRIVER") or shutil.which("geckodriver") or "/opt/homebrew/bin/geckodriver"
    if not os.path.exists(g): raise SystemExit("geckodriver not found — `brew install geckodriver` or set PRAVACHAN_GECKODRIVER")
    return g

def _driver(profile: str):
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.service import Service
    opts = Options(); opts.binary_location = _ff_bin()
    opts.add_argument("-profile"); opts.add_argument(profile)
    d = webdriver.Firefox(service=Service(_geckodriver()), options=opts)
    d.set_window_size(1400, 1000)
    return d

JS_BEST = r"""
const isG=c=>c>=0x0A80&&c<=0x0AFF;
function gc(t){let n=0;for(const ch of t){if(isG(ch.codePointAt(0)))n++;}return n;}
let best='',bs=0;
for(const el of document.querySelectorAll('div,section,article,p,span')){
 const t=el.innerText||'';const g=gc(t);
 if(g>bs&&t.length<300000){bs=g;best=t;}}
return best;
"""

def _click_text(d, texts):
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

def _dismiss_modal(d):
    from selenium.webdriver.common.by import By
    for xp in ["//button[@aria-label='Close']", "//button[contains(@aria-label,'Close')]",
               "//button[.//*[text()='close']]", "//button[normalize-space()='Got it']"]:
        for e in d.find_elements(By.XPATH, xp):
            if e.is_displayed():
                try: e.click(); return True
                except Exception:
                    try: d.execute_script("arguments[0].click();", e); return True
                    except Exception: pass
    return False

def _stage_ext(path: Path) -> str:
    ext = path.suffix
    if ext: return ext
    with path.open("rb") as fh: h = fh.read(16)          # sniff extension-less files
    return ".m4a" if h[4:8] == b"ftyp" else ".mp3"

def transcribe_dir(audio_dir: Path, trans_dir: Path, profile: str = DEFAULT_PROFILE,
                   chunk: int = 5, wait: int = WAIT_TRANSCRIPT):
    """Transcribe every audio file under audio_dir into trans_dir (mirrored tree),
    resumable. Requires the profile to be logged into NotebookLM already."""
    from selenium.webdriver.common.by import By
    from pipeline import find_audio                       # reuse the audio discovery
    audio = find_audio(audio_dir)
    todo = []
    for a in audio:
        rel = a.relative_to(audio_dir)
        out = trans_dir / rel.with_suffix(rel.suffix + ".txt")
        if out.exists() and gcount(out.read_text(encoding="utf-8")) >= GTHRESH:
            continue
        todo.append((a, out))
    log(f"notebooklm: {len(todo)}/{len(audio)} to transcribe (profile={profile}, chunk={chunk})")
    if not todo: return
    stage = Path(profile + "_stage"); stage.mkdir(parents=True, exist_ok=True)

    d = _driver(profile)
    notebook = {"url": None}
    seen = set()

    def new_notebook():
        d.get("https://notebook.google.com"); time.sleep(8)
        if "accounts.google.com" in d.current_url:
            raise SystemExit("NotebookLM profile is NOT logged in — run `pravachan-nlm-login` first.")
        _click_text(d, ["Create new notebook", "Create new"]); time.sleep(7)
        if _dismiss_modal(d): time.sleep(2)
        url = d.current_url.split("?")[0]
        if "/notebook/" not in url:            # create failed — almost always the notebook cap
            page = ""
            try: page = d.find_element("tag name", "body").text
            except Exception: pass
            if "maximum number of notebooks" in page or "Failed to create notebook" in page:
                raise SystemExit(
                    "NotebookLM ACCOUNT IS AT ITS NOTEBOOK LIMIT (couldn't create a new notebook).\n"
                    "Fix: run `pravachan-nlm-login` and sign in with a DIFFERENT Google account\n"
                    "(a fresh account has an empty notebook quota) — or delete old notebooks / upgrade.")
            raise SystemExit(f"NotebookLM did not open a new notebook (still at {url}). "
                             "Try `pravachan-nlm-login` with a different account.")
        notebook["url"] = url
        log("new notebook", notebook["url"])

    try:
        for i, (a, out) in enumerate(todo):
            if i % chunk == 0:
                new_notebook(); seen = set()
            tag = f"pv{i:03d}{_stage_ext(a)}"
            sp = stage / tag; shutil.copy2(a, sp)
            d.get(notebook["url"]); time.sleep(7)
            if _dismiss_modal(d): time.sleep(2)
            # A fresh notebook auto-opens the upload dialog (no 'Add sources' button); an
            # existing one needs the button. Click best-effort, then find the file input
            # directly — the dialog may already be open.
            _click_text(d, ["Add sources", "add a source"]); time.sleep(3)   # open source dialog
            _click_text(d, ["Upload files", "Upload"]); time.sleep(3)         # choose 'Upload files' → reveals input
            finp = None
            for _ in range(15):
                inps = d.find_elements(By.CSS_SELECTOR, "input[type=file]")
                if inps: finp = inps[-1]; break
                _click_text(d, ["Upload files", "Upload"]); time.sleep(2)
            if not finp: log("no file input for", a.name); continue
            finp.send_keys(str(sp)); log("uploaded", a.name); time.sleep(8)
            _click_text(d, [tag]); time.sleep(4)
            best = ""; dl = time.time() + wait
            while time.time() < dl:
                _click_text(d, [tag])
                try: best = d.execute_script(JS_BEST) or ""
                except Exception: best = ""
                if gcount(best) >= GTHRESH and best not in seen: break
                time.sleep(15)
            c = clean(best)
            if gcount(c) >= GTHRESH and best not in seen:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(c, encoding="utf-8"); seen.add(best)
                log(f"  ✓ {out.name} ({gcount(c)} guj chars)")
            else:
                log(f"  ✗ {a.name}: short/dup ({gcount(c)} chars)")
    finally:
        try: d.quit()
        except Exception: pass

def login(profile: str = DEFAULT_PROFILE):
    """Open the dedicated profile as a NORMAL Firefox instance (NOT Selenium) so Google
    permits sign-in — webdriver-controlled browsers are blocked at login. Selenium then
    reuses this logged-in profile for transcription."""
    import subprocess
    os.makedirs(profile, exist_ok=True)
    url = "https://notebook.google.com"
    log(f"opening dedicated profile as a normal Firefox window: {profile}")
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-n", "-a", "Firefox", "--args",
                          "-profile", profile, "-no-remote", url])
    else:
        subprocess.Popen([_ff_bin(), "-profile", profile, "-no-remote", url])
    print("\n>>> A normal Firefox window opened on the dedicated profile.")
    print(">>> Sign in to Google/NotebookLM there; the login is saved to this profile and")
    print(">>> transcription reuses it. Close the window once signed in.\n")

def login_main():
    import argparse
    ap = argparse.ArgumentParser(description="One-time NotebookLM login for the automation profile")
    ap.add_argument("--profile", default=os.environ.get("PRAVACHAN_NLM_PROFILE", DEFAULT_PROFILE))
    login(ap.parse_args().profile)

def _main():
    import argparse
    ap = argparse.ArgumentParser(description="Transcribe an audio dir via NotebookLM")
    ap.add_argument("audio_dir"); ap.add_argument("trans_dir")
    ap.add_argument("--profile", default=os.environ.get("PRAVACHAN_NLM_PROFILE", DEFAULT_PROFILE))
    ap.add_argument("--chunk", type=int, default=5)
    a = ap.parse_args()
    transcribe_dir(Path(a.audio_dir), Path(a.trans_dir), a.profile, a.chunk)

if __name__ == "__main__":
    _main()
