#!/usr/bin/env python3
"""Shared helpers for the pravachan superskill scripts."""
from __future__ import annotations
import re
from pathlib import Path

AUDIO_EXTS = {".mp3", ".m4a", ".mp4", ".wav", ".aac", ".flac", ".ogg", ".opus", ".wma", ".webm"}

def log(tag, *a): print(f"[{tag}]", *a, flush=True)
def gcount(s: str) -> int: return len(re.findall(r"[઀-૿]", s or ""))

def is_audio(p: Path) -> bool:
    if p.suffix.lower() in AUDIO_EXTS:
        return True
    if p.suffix == "":                       # sniff extension-less files
        try: head = p.open("rb").read(16)
        except OSError: return False
        return (head[4:8] == b"ftyp" or head[:3] == b"ID3" or head[:4] == b"RIFF"
                or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2") or head[:4] == b"OggS")
    return False

def find_audio(root: Path):
    root = Path(root)
    if root.is_file():
        return [root] if is_audio(root) else []
    return sorted(p for p in root.rglob("*") if p.is_file() and is_audio(p)
                  and "_oversized" not in p.parts and "_orig" not in p.parts)
