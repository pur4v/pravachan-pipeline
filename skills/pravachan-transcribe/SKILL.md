---
name: pravachan-transcribe
description: Transcribe pravachan audio to Gujarati text via NotebookLM (Selenium + a dedicated Firefox profile). Produces one <audio-name>.txt per file under transcripts/. Google Cloud STT is an optional fallback. Use after audio is fetched and before typesetting.
---

# pravachan-transcribe — audio → Gujarati transcript (NotebookLM)

Runs stage 2. Repo root = two levels up from this file (`$REPO`). Output goes to
`<OUT>/<set>/transcripts/<audio-name>.txt` (mirrors the audio tree). Resumable —
existing transcripts (≥400 Gujarati chars) are skipped.

## One-time login (on THIS machine)
NotebookLM runs in a **dedicated** Firefox automation profile — never the user's real
profile. Sign in once:
```
pravachan-nlm-login              # opens the profile at NotebookLM; sign in, press Enter
```

## Transcribe (NotebookLM — primary)
```
python3 $REPO/pipeline.py "<audio-dir-or-source>" --out "<OUT>/<set>" \
  --only transcribe --transcriber notebooklm --nlm-chunk 5
```
- Uploads each mp3, reads the clean Gujarati transcript from the viewer that auto-opens
  right after upload (the only reliable state), rotates to a fresh notebook every 5 files.
- Files must be <200MB — the fetch stage already compresses oversized audio.
- Single browser session is the reliable mode (Google logs out concurrent sessions).

## Optional fallback (Google Cloud STT — NOT Whisper)
```
pip install "google-cloud-speech" "google-cloud-storage"
export GOOGLE_APPLICATION_CREDENTIALS=/path/sa.json  PRAVACHAN_GCS_BUCKET=your-bucket
python3 $REPO/pipeline.py "<...>" --out "<OUT>/<set>" --only transcribe --transcriber google --lang gu
```

## After
Report transcripts vs audio count; flag short/empty ones. Next: `pravachan-typeset`.
