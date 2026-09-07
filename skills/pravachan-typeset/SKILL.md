---
name: pravachan-typeset
description: Typeset ONE Gujarati pravachan transcript into a house-style PDF + DOCX by applying the bundled jain-pravachan-transcript skill (clean → structure) and running build_doc.py. Handles a single transcript — dispatch one per file. Use when a transcript exists and needs to become a finished document.
---

# pravachan-typeset — one transcript → PDF + DOCX

This wraps **the original `jain-pravachan-transcript` skill** (bundled, unchanged) so
each transcript can be typeset by its own subagent. Repo root = two levels up from
this file (`$REPO`). Handle exactly ONE transcript per invocation.

## Read first (the actual skill you must follow)
1. `$REPO/skill/SKILL.md`
2. `$REPO/skill/references/corrections.md`
3. `$REPO/skill/references/structure.md`

## Procedure
1. Read the assigned transcript `<...>/transcripts/<name>.txt`.
2. Apply the skill: clean the ASR (fix Prakrit/Sanskrit terms per corrections.md),
   punctuate, structure into numbered Gujarati `<h2>` sections, Q&A as `<p class="q">`,
   enumerations in `<div class="box">`, gathas as `<div class="verse">`, editorial
   asides as `<p class="note">`; drop the trailing "Create an Audio Overview…" UI line
   and any spillover into another discourse. Output an HTML fragment (starts with `<h1>`).
3. **Title** by the chosen style — Gujarati numerals only, never Latin digits (N and
   date come from the filename):
   - `topic`   → `<h1>`=Gujarati topic from content; sub=date only. No speaker, no "Day N".
   - `numbered`→ `<h1>`=series/subject; sub=`વ્યાખ્યાન <N> · <date>`.
   - `granth`  → `<h1>`=granth's Gujarati name; sub=`ગ્રંથ પરિચય · વ્યાખ્યાન <N> · <date>`.
   - `day`     → `<h1>`=fixed set title (e.g. `ધ્યાન શિબિર`); sub=`દિવસ <N>`.
4. Build (A4 landscape, 2 columns, 18pt house default):
   ```
   python3 $REPO/skill/scripts/build_doc.py "<fragment.html>" \
     --out "<...>/pdfs/<name-without-.txt>"     # keep the basename EXACTLY (incl .mp3, spaces)
   ```
   Verify BOTH `.pdf` and `.docx` were written non-zero.

## Report
Chosen H1 + filename + PDF page count; flag anything dropped, suspect numbers, or
gathas reconstructed loosely.
