"""Library organization and file management"""
from __future__ import annotations
import re
import shutil
from pathlib import Path
from typing import Optional
from .tags import TrackInfo, read_tags

ILLEGAL_CHARS = re.compile(r'[/\\:*?"<>|]')
SUPPORTED_EXTENSIONS = frozenset({".mp3", ".flac", ".aac", ".m4a", ".wav", ".ogg"})


def sanitize(name: str) -> str:
    return ILLEGAL_CHARS.sub("", name).strip()


def build_dest_path(info: TrackInfo, target: Path) -> Path:
    if not info.artist or not info.title:
        return target / "_Unsorted" / info.original_path.name

    artist = sanitize(info.artist)
    album = sanitize(info.album) if info.album else "Singles"
    ext = info.original_path.suffix

    if info.track_number is not None:
        filename = f"{info.track_number:02d} - {sanitize(info.title)}{ext}"
    else:
        filename = f"{sanitize(info.title)}{ext}"

    return target / artist / album / filename
