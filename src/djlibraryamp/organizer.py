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
    title = sanitize(info.title)

    if not artist or not title:
        return target / "_Unsorted" / info.original_path.name

    album = sanitize(info.album) if info.album else "Singles"
    ext = info.original_path.suffix

    if info.track_number is not None:
        filename = f"{info.track_number:02d} - {title}{ext}"
    else:
        filename = f"{title}{ext}"

    return target / artist / album / filename


def resolve_conflict(dest: Path, mode: str) -> Optional[Path]:
    if not dest.exists():
        return dest
    if mode == "skip":
        return None
    if mode == "overwrite":
        return dest
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def process_library(source: Path, target: Path, dry_run: bool, conflict: str) -> None:
    files = sorted(
        f for f in source.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    counts: dict[str, int] = {"copy": 0, "skip": 0, "unsorted": 0}

    for src_file in files:
        info = read_tags(src_file)
        dest = build_dest_path(info, target)
        is_unsorted = dest.relative_to(target).parts[0] == "_Unsorted"
        final_dest = resolve_conflict(dest, conflict)

        if is_unsorted:
            print(f"[UNSORTED] {src_file.name}")
            counts["unsorted"] += 1
            if not dry_run and final_dest is not None:
                final_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, final_dest)
        elif final_dest is None:
            print(f"[SKIP]     {dest.relative_to(target)}")
            counts["skip"] += 1
        else:
            if final_dest != dest:
                print(f"[CONFLICT] {dest.relative_to(target)} → {final_dest.name}")
            else:
                label = "[DRY RUN]" if dry_run else "[COPY]   "
                print(f"{label}  {dest.relative_to(target)}")
            counts["copy"] += 1
            if not dry_run:
                final_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, final_dest)

    if not dry_run:
        print(f"\nDone: {counts['copy']} copied, {counts['skip']} skipped, {counts['unsorted']} unsorted")
