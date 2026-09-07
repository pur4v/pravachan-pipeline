---
name: pravachan
description: Turn Jain pravachan audio into typeset Gujarati PDF+DOCX, end to end. Give it a YouTube link, a Google Drive folder/file link, or a local audio file/dir path and it self-contains the whole pipeline — convert→mp3, compress/split if oversized, transcribe via NotebookLM (Selenium, auto-installed) or Google Chirp, clean+structure+typeset with the bundled jain-pravachan-transcript skill, and run a scripture verifier loop — all in multi-agent mode. Use whenever the user provides pravachan/discourse audio (or a link to it) and wants finished documents. Triggers: "pravachan", "pravachan pdf", "transcribe this talk", a Drive/YouTube link to Gujarati discourses, an audio folder of talks.
---

# pravachan — self-contained audio → typeset PDF/DOCX superskill

You are the **orchestrator**. From a link or path, drive the entire pipeline and produce
one typeset PDF+DOCX per talk. This skill is self-contained: every script and reference
it needs is bundled under this skill's own directory (call it `$SKILL`). It composes four
sub-steps — **fetch → transcribe → typeset → verify** — the last two run **multi-agent**.

`$SKILL` = the directory containing this file. Scripts: `$SKILL/scripts/*`. References:
`$SKILL/references/*` (the original typeset skill is `references/typeset-skill.md` +
`corrections.md` + `structure.md`; the verifier reference is `references/scriptures.md`).

## Step 0 — Make the machine ready (install if missing)
Run once: `python3 $SKILL/scripts/bootstrap.py`. It pip-installs selenium, yt-dlp, gdown,
weasyprint, python-docx, beautifulsoup4, anthropic, and (via Homebrew if present) ffmpeg,
geckodriver, Firefox, pango, Noto Gujarati fonts. If it exits non-zero, tell the user
exactly what to install manually (e.g. Homebrew) and stop.

## Step 1 — Gather configuration (ASK the user)
Use AskUserQuestion to collect anything not already given. Defaults in **bold**:
- **Source(s)** — the YouTube / Drive link(s) or local path(s). (required)
- **Set name** — output folder name under the output root.
- **Output root** — **`~/pravachan-output`**.
- **Title style** — `topic` (H1 from content, no speaker/day, date-only sub) |
  `numbered` (`વ્યાખ્યાન N · date`) | `granth` (`ગ્રંથ પરિચય · વ્યાખ્યાન N · date`) |
  `day` (`ધ્યાન શિબિર` / `દિવસ N`). Numbers/dates always in **Gujarati numerals**.
- **Transcriber** — **`notebooklm`** (Selenium + dedicated Firefox profile) | `chirp`
  (Google Cloud STT v2, model chirp_2). No Whisper.
- **Concurrency** — number of parallel subagents for the typeset+verify stages.
  **Default 40.** Confirm the user's machine/plan can sustain it; offer 10/20/40/custom.
- **Verifier loop** — **on** | off; and **max passes = 2**.
- **Layout** — **A4 landscape, 2 columns, 18pt** | custom (portrait / columns / size).
- **Language** — **Gujarati (gu)**.

If the user already gave a link and said "just do it", use the defaults and proceed —
only ask for the source and title style if genuinely missing.

## Step 2 — Fetch + prep (one call per source)
```
python3 $SKILL/scripts/fetch.py "<SOURCE>" --out "<ROOT>/<set>/audio" --cap-mb 190
```
Downloads (yt-dlp / gdown / local copy), converts every file to **mp3**, **compresses**
anything >190MB (mono, lower bitrate), and **splits** (lossless) only if a file is still
over the cap. Originals kept in `audio/_orig/` and `audio/_oversized/`. Confirm the file
list it prints; none should say "STILL OVER CAP".

## Step 3 — Transcribe

### NotebookLM (default) — a ONE-TIME login, then automated
NotebookLM sign-in is a **two-phase** flow. Read this to the user clearly:

**Phase A — log in ONCE (a normal browser window; do this yourself, human):**
```
python3 $SKILL/scripts/nlm.py --login
```
- This opens a **normal Firefox window** on a **dedicated automation profile**
  (`~/.pravachan-notebooklm-firefox` — NEVER your real Firefox profile, and your real
  Firefox is left untouched).
- **Sign in to Google / NotebookLM in that window.** ⚠️ You MUST do the sign-in in this
  normal window — Google **blocks** sign-in inside an automated (Selenium) browser
  ("this browser or app may not be secure"). That is why login is a separate manual step.
- Your session is saved to the profile on disk. **Close the window** when NotebookLM home
  has loaded. You only do this once (until Google eventually expires the session).

**Phase B — transcribe (automated; Selenium reuses the logged-in profile):**
```
python3 $SKILL/scripts/nlm.py "<ROOT>/<set>/audio" "<ROOT>/<set>/transcripts" --chunk 5
```
- The login window from Phase A must be CLOSED first — one Firefox instance per profile.
- Selenium now drives the already-logged-in profile (uploads each mp3, reads the transcript
  from the viewer that auto-opens right after upload, rotates notebook every `--chunk` files).
  This is NOT blocked — only interactive login is. Single session is the reliable mode.
- Resumable; poll transcripts as they land.

**Error handling the user must know about:**
- If Phase B prints **"NotebookLM profile is NOT logged in"** → the user skipped/needs to
  redo Phase A. Never try to log in via Selenium — it is blocked.
- If Phase B prints **"NotebookLM ACCOUNT IS AT ITS NOTEBOOK LIMIT"** (free accounts cap the
  number of notebooks, ~100) → tell the user to run `python3 $SKILL/scripts/nlm.py --login`
  and **sign in with a DIFFERENT Google account** (a fresh account has an empty notebook
  quota), then re-run Phase B. Alternatives: delete old notebooks in NotebookLM, or upgrade.
  (The transcripts already saved to disk are safe regardless.)

### Chirp (optional fallback, no login UI)
```
python3 $SKILL/scripts/chirp.py "<ROOT>/<set>/audio" "<ROOT>/<set>/transcripts" --lang gu-IN
```
Needs `PRAVACHAN_GCP_PROJECT`, `PRAVACHAN_GCS_BUCKET`, `GOOGLE_APPLICATION_CREDENTIALS`.

Each transcript is `<ROOT>/<set>/transcripts/<audio-name>.txt`. Resumable.

## Step 4 — Typeset  (MULTI-AGENT)
As **each** transcript appears, dispatch ONE subagent — up to **<concurrency>** running at
once; as any finishes, dispatch the next; never idle. Give each subagent:
- the single transcript path, the output dir `<ROOT>/<set>/pdfs/`, the chosen title style;
- instructions to **apply the bundled typeset skill**: read `$SKILL/references/typeset-skill.md`,
  `$SKILL/references/corrections.md`, `$SKILL/references/structure.md`; clean the ASR,
  structure it, apply the title convention (Gujarati numerals; N/date from the filename),
  drop the "Create an Audio Overview…" line, output an HTML fragment (starts with `<h1>`);
- then build: `python3 $SKILL/scripts/build_doc.py "<fragment.html>" --out "<ROOT>/<set>/pdfs/<name-without-.txt>"`
  (A4 landscape, 2 columns, 18pt unless the user chose custom). Keep the basename EXACTLY.
- Subagent reports: H1, page count, and anything dropped / reconstructed loosely.

## Step 5 — Verifier loop  (MULTI-AGENT, if enabled)
For each finished document, dispatch a **verifier subagent** (again up to <concurrency>):
- Read `$SKILL/references/scriptures.md` + `corrections.md`. Check the transcript/fragment
  for canonical errors: garbled gathas/sutras, wrong Tirthankara/agam names, off canonical
  numbers, doctrinal-term errors, foreign-discourse bleed, UI text, missing closing.
- Return `VERDICT: clean | fixed | flagged`. If **fixed**, it edits the HTML fragment and
  **rebuilds** that doc (re-run build_doc.py). Loop that doc until `clean` or **max passes**.
- NEVER alter the speaker's own opinions, stories, asides, jokes, or code-switching — only
  canonical/factual corrections. Collect all `flagged` items for the final report.

## Step 6 — Assemble + verify + report
- Move every `*.docx` from `<ROOT>/<set>/pdfs/` into a sibling `<ROOT>/<set>_docs/` (PDFs stay).
- Final check (report, don't assume): counts match (audio=transcripts=pdfs=docx); each
  subtitle's number/date matches its filename; Gujarati numerals only (no Latin digits);
  no short/empty transcripts. List every verifier `flagged` item for a human.
- Tell the user where the outputs are and what (if anything) needs a human eye.

## Hard rules
- NotebookLM: dedicated automation profile only — never the user's real Firefox profile,
  never quit their live Firefox.
- Never delete originals — move oversized/originals aside (`_oversized/`, `_orig/`).
- Everything runs on the user's machine, on the user's own Claude and their own NotebookLM /
  Google login. Ping the user only when the whole set is finished and verified.
