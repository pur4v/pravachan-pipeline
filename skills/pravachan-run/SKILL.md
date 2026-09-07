---
name: pravachan-run
description: End-to-end Jain pravachan pipeline inside Claude Code — take a Google Drive folder / YouTube link / local audio dir and produce typeset PDF+DOCX per talk, orchestrating a typeset subagent per transcript (the multi-agent flow). Use when the user gives a Drive/YouTube/audio source and wants finished pravachan documents.
---

# pravachan-run — full pipeline, orchestrated in Claude Code

You are the orchestrator. Drive the whole pipeline the multi-agent way: fetch →
transcribe → dispatch a **typeset subagent per transcript continuously as each
lands** (never batch, never idle) → split docs → verify. This mirrors the packaged
`pravachan` CLI but runs interactively so a human can watch and correct.

Repo root (this skill's package): the directory two levels up from this file —
call it `$REPO`. Key paths: `$REPO/pipeline.py`, `$REPO/skill/` (the
jain-pravachan-transcript skill), `$REPO/skill/scripts/build_doc.py`.

## Inputs to confirm with the user (once)
- **source**: Drive folder URL | YouTube video/playlist URL | local audio dir
- **set name**: output folder under the chosen output root
- **title style**: `topic` | `numbered` | `granth` | `day` (see the typeset skill)

## Steps

1. **Fetch + prep** (one shell call):
   ```
   python3 $REPO/pipeline.py "<source>" --out "<OUT>/<set>" \
     --source-type auto --only download
   ```
   This downloads (gdown / yt-dlp), transcodes m4a/AAC→mp3, and **compresses any
   file >190MB** (never splits). Confirm audio landed in `<OUT>/<set>/audio/`.

2. **Transcribe** (NotebookLM — requires a one-time `pravachan-nlm-login` on this machine):
   ```
   python3 $REPO/pipeline.py "<source>" --out "<OUT>/<set>" --only transcribe --transcriber notebooklm
   ```
   Uploads each mp3 to NotebookLM in a dedicated Firefox profile and writes
   `<OUT>/<set>/transcripts/<audio-name>.txt`. Poll for transcripts as they appear.
   (Google Cloud STT is an optional fallback: `--transcriber google`. No Whisper.)

3. **Typeset — the multi-agent stage.** As **each** transcript file appears, dispatch
   ONE subagent (do not wait for all): give it the `pravachan-typeset` skill (or its
   instructions), the single transcript path, the output dir `<OUT>/<set>/pdfs/`, and
   the chosen title style. Keep dispatching so free agents always have work. Each
   subagent produces `<name>.pdf` + `<name>.docx`.

4. **Split docs**: move every `*.docx` from `<OUT>/<set>/pdfs/` into a sibling
   `<OUT>/<set>_docs/` (PDFs stay in `pdfs/`).

5. **Verify** (report, don't assume): counts match (audio=transcripts=pdfs=docx);
   each subtitle's number/date matches its filename; Gujarati numerals only (no Latin
   digits); no short/empty transcripts. Then tell the user it's done.

## Rules
- Never touch the user's real browser profile if using NotebookLM (dedicated automation profile only).
- Never delete originals — move oversized/originals aside (`_oversized/`, `_orig/`).
- Ping the user only when the whole set is finished and verified.
