"""Tag reading and parsing functionality"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TrackInfo:
    artist: Optional[str]
    album: Optional[str]
    track_number: Optional[int]
    title: Optional[str]
    original_path: Path


def parse_filename(stem: str) -> tuple[Optional[str], Optional[str]]:
    parts = [p.strip() for p in stem.split(" - ")]
    if len(parts) >= 2 and parts[0] and parts[1]:
        return parts[0], parts[1]
    return None, None
