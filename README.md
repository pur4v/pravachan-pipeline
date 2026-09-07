# pravachan-pipeline

Turn **Jain pravachan audio** — a Google Drive folder, a YouTube link, or local files —
into clean, typeset Gujarati **PDF + DOCX** documents, end to end.

Each talk is fetched, transcribed via **NotebookLM**, cleaned + structured + typeset by the
bundled `jain-pravachan-transcript` skill through **Claude** (A4-landscape, two-column, ASR
terms fixed, sections, gathas restored, Gujarati numerals), then checked by a **scripture
verifier** against the Jain canon. Everything runs **on your own machine, on your own Claude
and your own NotebookLM login** — no data leaves, no per-seat bill.

## Three ways to run

### 1. Claude Code superskill (self-contained)
Drop `claude-skill/pravachan` into `~/.claude/skills/` and paste a link or path:
```bash
claude-skill/install.sh
```
The `pravachan` superskill then runs the whole pipeline in **multi-agent mode** (a typeset
subagent per transcript + a verifier subagent per doc): bootstrap deps → fetch → transcribe
→ typeset → **scripture-verify** → PDF/DOCX. It asks for configuration (title style,
transcriber, concurrency, verifier passes) and installs anything missing.

### 2. CLI
```bash
pravachan "https://drive.google.com/drive/folders/XXXX" --out ./out/aagam --title-style numbered
pravachan "https://youtube.com/playlist?list=YYYY"        --out ./out/talks --title-style topic
pravachan ./local_audio_dir --out ./out/granth --title-style granth
```

### 3. Web app
```bash
pravachan-web            # → http://127.0.0.1:8765
```
Paste a Drive/YouTube link or upload audio, pick a set name + title style, queue the job,
and download PDF/DOCX/zip from the dashboard.

## Install
```bash
brew install ffmpeg pango geckodriver
brew install --cask firefox
brew install --cask font-noto-serif-gujarati font-noto-sans-gujarati
pip install -e .                          # installs `pravachan`, `pravachan-web`, `pravachan-nlm-login`
export ANTHROPIC_API_KEY=sk-ant-...       # or: ant auth login
pravachan-nlm-login                       # one-time: sign in to NotebookLM in a dedicated profile
```

## Transcription = NotebookLM (Selenium)

The same approach used to build the original sets. Sign-in is a **two-phase** flow:

- **`pravachan-nlm-login`** opens a **normal Firefox window** on a dedicated automation
  profile (never your real profile) — you sign into NotebookLM there. Google blocks sign-in
  inside an automated browser, which is why login is a separate manual step. The session is
  saved to the profile.
- Transcription then drives that already-logged-in profile with Selenium (upload → read the
  transcript from the viewer that auto-opens). One reliable session; a fresh Google account
  has a fresh notebook quota.

Google Cloud Speech-to-Text (`--transcriber google`, model `chirp_2`) is an optional
fallback. There is no Whisper.

## Options
```
--source-type auto|drive|youtube|local    # default auto-detects from the URL
--title-style topic|numbered|granth|day|auto
--target-mb 190                           # compress (not split) audio larger than this
--transcriber notebooklm|google
--format both|pdf|docx   --columns 2  --size 18  --portrait
--workers 4              # parallel Claude build workers
--model claude-opus-5    # skill model (claude-sonnet-5 is cheaper/faster)
--only download,transcribe,build          # run a subset of stages
```

## Title styles
- **topic** — H1 from the talk's content; date-only subtitle. No speaker, no day number.
- **numbered** — `વ્યાખ્યાન N · date`.
- **granth** — `ગ્રંથ પરિચય · વ્યાખ્યાન N · date`.
- **day** — `ધ્યાન શિબિર` / `દિવસ N`.

All numbers/dates render in **Gujarati numerals**, derived from the filename.

## Layout
```
pravachan-pipeline/
  pipeline.py          # engine: fetch → transcribe → Claude typeset → PDF/DOCX (CLI: `pravachan`)
  nlm.py               # NotebookLM transcriber (Selenium + Firefox profile); `pravachan-nlm-login`
  gstt.py              # optional Google Cloud STT (chirp_2) fallback
  webapp/              # FastAPI web app + dashboard (`pravachan-web`)
  skill/               # the jain-pravachan-transcript skill: SKILL.md, corrections, structure, build_doc.py
  skills/              # per-step Claude Code skills: pravachan-run / -fetch / -transcribe / -typeset
  claude-skill/        # self-contained `pravachan` superskill (fetch→transcribe→typeset→verify) + install.sh
```

## Notes
- Transcripts are machine ASR; the skill fixes common misrecognitions and the verifier
  checks canon (gathas, Tirthankara/agam names, standard numbers), but a human proofread is
  wise before authoritative use.
- Audio over ~200 MB is **compressed** (mono, lower bitrate — inaudible for speech), not
  split; the original is kept in `audio/_oversized/`. Splitting is a last resort.
- Public Drive folders work directly; private folders need a service-account Drive API fetch.

## License
MIT — see [LICENSE](LICENSE).
