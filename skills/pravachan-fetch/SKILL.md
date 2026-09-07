---
name: pravachan-fetch
description: Fetch pravachan audio into the pipeline — download a Google Drive folder (gdown) or YouTube video/playlist (yt-dlp→mp3), transcode m4a/AAC to mp3, and compress any file over ~190MB instead of splitting. Use when the user has a Drive/YouTube source to pull audio from before transcription.
---

# pravachan-fetch — get audio into `<out>/audio/`

Runs stage 1 of the pipeline. Repo root = two levels up from this file (`$REPO`).

## Run
```
python3 $REPO/pipeline.py "<SOURCE>" --out "<OUT>/<set>" --source-type auto --only download
```
- `auto` detects: `youtube.com`/`youtu.be` → yt-dlp (mp3 192k); other `http(s)` → gdown Drive folder; else a local dir is mirrored in.
- After download it **transcodes** extension-less / m4a / AAC files and **compresses** anything `> --target-mb` (default 190) to mono mp3 — originals kept in `audio/_oversized/`. It never splits.

## Notes
- Public Drive folders work directly. Private folders need auth (service-account Drive API) — say so rather than failing silently.
- Verify with `ls "<OUT>/<set>/audio"` and report the count + any file still >190MB.
- Next step: `pravachan-transcribe`.
