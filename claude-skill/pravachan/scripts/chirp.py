#!/usr/bin/env python3
"""
Google Chirp transcription (Cloud Speech-to-Text v2, model `chirp_2`) — the OPTIONAL
fallback when NotebookLM isn't used. No Whisper.

Converts each file to FLAC (mono 16k), uploads to your GCS bucket, runs v2
batch_recognize with the Chirp 2 USM model, writes the transcript, cleans up.

  pip install google-cloud-speech google-cloud-storage
  export PRAVACHAN_GCP_PROJECT=my-proj  PRAVACHAN_GCS_BUCKET=my-bucket
  export GOOGLE_APPLICATION_CREDENTIALS=/path/sa.json  [PRAVACHAN_GCP_REGION=us-central1]

  python3 chirp.py <audio_dir> <transcripts_dir> [--lang gu-IN]
"""
from __future__ import annotations
import os, sys, subprocess, tempfile, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import log, find_audio

def _need(n):
    v = os.environ.get(n)
    if not v: raise SystemExit(f"chirp needs {n} set (see chirp.py header). Or use NotebookLM.")
    return v

def _flac(src: Path, dst: Path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1",
                    "-ar", "16000", "-c:a", "flac", str(dst)], check=True)

def transcribe_dir(audio_dir: Path, trans_dir: Path, lang: str = "gu-IN"):
    try:
        from google.cloud.speech_v2 import SpeechClient
        from google.cloud.speech_v2.types import cloud_speech as t
        from google.cloud import storage
    except ImportError:
        raise SystemExit("pip install google-cloud-speech google-cloud-storage")
    proj = _need("PRAVACHAN_GCP_PROJECT"); bucket_name = _need("PRAVACHAN_GCS_BUCKET"); _need("GOOGLE_APPLICATION_CREDENTIALS")
    region = os.environ.get("PRAVACHAN_GCP_REGION", "us-central1")
    if len(lang) == 2: lang = {"gu": "gu-IN", "hi": "hi-IN", "en": "en-IN"}.get(lang, lang)
    api = None if region == "global" else f"{region}-speech.googleapis.com"
    client = SpeechClient(client_options={"api_endpoint": api} if api else None)
    gcs = storage.Client(project=proj); bucket = gcs.bucket(bucket_name)
    recognizer = f"projects/{proj}/locations/{region}/recognizers/_"

    for a in find_audio(audio_dir):
        out = trans_dir / a.relative_to(audio_dir).with_suffix(a.suffix + ".txt")
        if out.exists() and out.stat().st_size > 0: continue
        with tempfile.TemporaryDirectory() as td:
            flac = Path(td) / "a.flac"; _flac(a, flac)
            key = f"pravachan-tmp/{uuid.uuid4().hex}.flac"; blob = bucket.blob(key)
            log("chirp", f"upload {a.name} → gs://{bucket_name}/{key}"); blob.upload_from_filename(str(flac))
            try:
                cfg = t.RecognitionConfig(
                    auto_decoding_config=t.AutoDetectDecodingConfig(),
                    model="chirp_2", language_codes=[lang],
                    features=t.RecognitionFeatures(enable_automatic_punctuation=True))
                req = t.BatchRecognizeRequest(
                    recognizer=recognizer, config=cfg,
                    files=[t.BatchRecognizeFileMetadata(uri=f"gs://{bucket_name}/{key}")],
                    recognition_output_config=t.RecognitionOutputConfig(
                        inline_response_config=t.InlineOutputConfig()))
                log("chirp", f"transcribing {a.name} …")
                resp = client.batch_recognize(request=req).result(timeout=6000)
                text = ""
                for _uri, fr in resp.results.items():
                    for r in fr.transcript.results:
                        if r.alternatives: text += r.alternatives[0].transcript.strip() + "\n"
                text = text.strip()
            finally:
                try: blob.delete()
                except Exception: pass
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text, encoding="utf-8")
        log("chirp", f"  ✓ {out.name} ({len(text)} chars)")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_dir"); ap.add_argument("trans_dir"); ap.add_argument("--lang", default="gu-IN")
    a = ap.parse_args(); transcribe_dir(Path(a.audio_dir), Path(a.trans_dir), a.lang)

if __name__ == "__main__":
    main()
