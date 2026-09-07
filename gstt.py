#!/usr/bin/env python3
"""
Google Cloud Speech-to-Text transcription — the OPTIONAL fallback when NotebookLM
isn't available. NotebookLM (nlm.py) is the primary engine; this exists only as a
managed alternative. There is deliberately no Whisper path.

Long pravachan audio (>60s) needs Google's async long-running recognize, which reads
from a GCS bucket — so this converts each file to FLAC (mono 16k), uploads it to your
bucket, transcribes, then cleans the temp object up.

Requires:
    pip install google-cloud-speech google-cloud-storage
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    PRAVACHAN_GCS_BUCKET=your-bucket-name
"""
from __future__ import annotations
import os, subprocess, tempfile, uuid
from pathlib import Path

def log(*a): print("[gstt]", *a, flush=True)

def _need(name):
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"google transcriber needs {name} set "
                         "(also GOOGLE_APPLICATION_CREDENTIALS). Or use --transcriber notebooklm.")
    return v

def _to_flac(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-ac", "1", "-ar", "16000", "-c:a", "flac", str(dst)], check=True)

def transcribe_dir(audio_dir: Path, trans_dir: Path, lang: str = "gu-IN"):
    from pipeline import find_audio
    try:
        from google.cloud import speech, storage
    except ImportError:
        raise SystemExit("pip install google-cloud-speech google-cloud-storage")
    bucket_name = _need("PRAVACHAN_GCS_BUCKET"); _need("GOOGLE_APPLICATION_CREDENTIALS")
    if len(lang) == 2:                      # accept 'gu' shorthand
        lang = {"gu": "gu-IN", "hi": "hi-IN", "en": "en-IN"}.get(lang, lang)
    sc = speech.SpeechClient(); gcs = storage.Client(); bucket = gcs.bucket(bucket_name)

    audio = find_audio(audio_dir)
    for a in audio:
        rel = a.relative_to(audio_dir)
        out = trans_dir / rel.with_suffix(rel.suffix + ".txt")
        if out.exists() and out.stat().st_size > 0:
            continue
        with tempfile.TemporaryDirectory() as td:
            flac = Path(td) / "a.flac"; _to_flac(a, flac)
            key = f"pravachan-tmp/{uuid.uuid4().hex}.flac"; blob = bucket.blob(key)
            log(f"upload → gs://{bucket_name}/{key}  ({a.name})")
            blob.upload_from_filename(str(flac))
            try:
                cfg = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
                    sample_rate_hertz=16000, language_code=lang,
                    enable_automatic_punctuation=True)
                op = sc.long_running_recognize(
                    config=cfg, audio=speech.RecognitionAudio(uri=f"gs://{bucket_name}/{key}"))
                log(f"  transcribing {a.name} …")
                resp = op.result(timeout=6000)
            finally:
                try: blob.delete()
                except Exception: pass
            text = "\n".join(r.alternatives[0].transcript.strip()
                             for r in resp.results if r.alternatives).strip()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        log(f"  ✓ {out.name} ({len(text)} chars)")
