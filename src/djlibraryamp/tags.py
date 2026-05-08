"""Tag reading and parsing functionality"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


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


def read_tags(path: Path) -> TrackInfo:
    artist = album = title = None
    track_number = None

    easy_tags = None
    try:
        result = mutagen.File(path, easy=True)
        if result is not None:
            easy_tags = result
    except Exception:
        pass

    if easy_tags is None:
        try:
            easy_tags = EasyID3(str(path))
        except ID3NoHeaderError:
            pass
        except Exception:
            pass

    if easy_tags is not None:
        artist = (easy_tags.get("artist") or [None])[0]
        album = (easy_tags.get("album") or [None])[0]
        title = (easy_tags.get("title") or [None])[0]
        trck = (easy_tags.get("tracknumber") or [None])[0]
        if trck:
            try:
                track_number = int(trck.split("/")[0])
            except ValueError:
                pass

    if not artist or not title:
        parsed_artist, parsed_title = parse_filename(path.stem)
        if not artist:
            artist = parsed_artist
        if not title:
            title = parsed_title

    return TrackInfo(
        artist=artist or None,
        album=album or None,
        track_number=track_number,
        title=title or None,
        original_path=path,
    )
