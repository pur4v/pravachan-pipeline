#!/usr/bin/env python3
"""
fetch.py — get audio ready for transcription.

  <source> may be: a YouTube video/playlist URL, a Google Drive folder URL, a local
  audio file, or a local directory of audio.

Pipeline: download (yt-dlp / gdown / copy) → convert every file to MP3 → COMPRESS any
file over the cap (mono, lower bitrate — inaudible for speech) → only if it is STILL
over the cap, SPLIT it (lossless stream-copy) into <cap parts. Originals kept aside.

Usage:
  python3 fetch.py <source> --out <audio_dir> [--source-type auto|youtube|drive|local]
                   [--cap-mb 190] [--no-split]
"""
from __future__ import annotations
import argparse, os, re, subprocess, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import log, find_audio, is_audio

def sh(cmd, **kw): return subprocess.run(cmd, **kw)

def detect(src: str) -> str:
    if re.search(r"(youtube\.com|youtu\.be)", src): return "youtube"
    if re.match(r"https?://", src): return "drive"
    return "local"

def dl_youtube(url, adir):
    log("fetch", "yt-dlp → mp3 →", adir)
    sh([sys.executable, "-m", "yt_dlp", "-x", "--audio-format", "mp3", "--audio-quality",
        "192K", "--embed-metadata", "-o", str(adir / "%(title)s.%(ext)s"), url], check=True)

def dl_drive(url, adir):
    log("fetch", "gdown Drive folder →", adir)
    r = sh([sys.executable, "-m", "gdown", "--folder", url, "-O", str(adir), "--remaining-ok"])
    if r.returncode != 0 or not find_audio(adir):
        sh([sys.executable, "-m", "gdown", "--folder", url, "-O", str(adir)], check=True)

def dl_local(src, adir):
    src = Path(src).expanduser().resolve()
    if src.is_file():
        shutil.copy2(src, adir / src.name); return
    for p in find_audio(src):
        dst = adir / p.relative_to(src); dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists(): shutil.copy2(p, dst)

def to_mp3(adir: Path):
    """Convert any non-mp3 (m4a/aac/mp4/…/extension-less) to mp3; keep original aside."""
    for a in find_audio(adir):
        if a.suffix.lower() == ".mp3":
            continue
        out = a.with_suffix(".mp3")
        if out.exists():
            continue
        log("fetch", "convert →", out.name)
        r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a), "-vn",
                "-acodec", "libmp3lame", "-b:a", "192k", str(out)])
        if r.returncode == 0:
            keep = adir / "_orig"; keep.mkdir(exist_ok=True)
            a.replace(keep / a.name)

def dur(p: Path) -> float:
    try:
        o = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                "csv=p=0", str(p)], capture_output=True, text=True)
        return max(1.0, float(o.stdout.strip() or 1))
    except Exception:
        return 1.0

def compress(a: Path, cap: int) -> Path:
    """Re-encode mono at a bitrate chosen to land under cap MB. Returns the file path."""
    br = int((cap * 8 * 1024 * 1024) / (dur(a) * 1000) * 0.92); br = max(32, min(128, br))
    keep = a.parent / "_oversized"; keep.mkdir(exist_ok=True)
    if not (keep / a.name).exists(): shutil.copy2(a, keep / a.name)
    tmp = a.with_suffix(".cmp.mp3")
    log("fetch", f"compress {a.name} ({a.stat().st_size//1048576}MB) → mono {br}k")
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a), "-vn", "-ac", "1",
            "-acodec", "libmp3lame", "-b:a", f"{br}k", str(tmp)])
    if r.returncode == 0:
        tmp.replace(a)
    else:
        tmp.unlink(missing_ok=True)
    return a

def split(a: Path, cap: int):
    """Lossless stream-copy split into <cap parts (last resort). Original moved aside."""
    total = a.stat().st_size; parts = (total // (cap * 1024 * 1024)) + 1
    seg = dur(a) / parts + 1
    log("fetch", f"split {a.name} into {parts} parts (~{int(seg)}s each)")
    patt = str(a.with_suffix("")) + ".part%02d.mp3"
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(a), "-f", "segment",
            "-segment_time", str(int(seg)), "-c", "copy", patt])
    if r.returncode == 0:
        keep = a.parent / "_oversized"; keep.mkdir(exist_ok=True)
        a.replace(keep / a.name)

def enforce_cap(adir: Path, cap: int, allow_split: bool):
    capb = cap * 1024 * 1024
    for a in list(find_audio(adir)):
        if a.stat().st_size <= capb:
            continue
        compress(a, cap)
        if a.exists() and a.stat().st_size > capb and allow_split:
            split(a, cap)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source"); ap.add_argument("--out", required=True)
    ap.add_argument("--source-type", default="auto", choices=["auto", "youtube", "drive", "local"])
    ap.add_argument("--cap-mb", type=int, default=190)
    ap.add_argument("--no-split", action="store_true")
    a = ap.parse_args()
    adir = Path(a.out).expanduser().resolve(); adir.mkdir(parents=True, exist_ok=True)
    st = a.source_type if a.source_type != "auto" else detect(a.source)
    {"youtube": dl_youtube, "drive": dl_drive, "local": dl_local}[st](a.source, adir)
    to_mp3(adir)
    enforce_cap(adir, a.cap_mb, allow_split=not a.no_split)
    files = find_audio(adir)
    log("fetch", f"ready: {len(files)} mp3 file(s) in {adir}")
    for f in files:
        flag = "  ⚠️STILL OVER CAP" if f.stat().st_size > a.cap_mb * 1024 * 1024 else ""
        print(f"  {f.stat().st_size//1048576:>4}MB  {f.name}{flag}")

if __name__ == "__main__":
    main()
