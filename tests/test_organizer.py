"""Tests for organizer module"""
from pathlib import Path
import pytest
from djlibraryamp.tags import TrackInfo
from djlibraryamp.organizer import sanitize, build_dest_path, resolve_conflict


def _info(artist=None, album=None, track_number=None, title=None, path=Path("track.mp3")):
    return TrackInfo(artist=artist, album=album, track_number=track_number, title=title, original_path=path)


def test_sanitize_removes_illegal_chars():
    assert sanitize("Artist: Name/Test") == "Artist NameTest"


def test_sanitize_strips_whitespace():
    assert sanitize("  Name  ") == "Name"


def test_sanitize_leaves_clean_string_unchanged():
    assert sanitize("Adam Beyer") == "Adam Beyer"


def test_build_dest_full(tmp_path):
    info = _info("Adam Beyer", "Drumcode 08", 3, "Analyser")
    assert build_dest_path(info, tmp_path) == tmp_path / "Adam Beyer" / "Drumcode 08" / "03 - Analyser.mp3"


def test_build_dest_no_album(tmp_path):
    info = _info("Adam Beyer", None, None, "Analyser")
    assert build_dest_path(info, tmp_path) == tmp_path / "Adam Beyer" / "Singles" / "Analyser.mp3"


def test_build_dest_no_track_number(tmp_path):
    info = _info("Adam Beyer", "Drumcode 08", None, "Analyser")
    assert build_dest_path(info, tmp_path) == tmp_path / "Adam Beyer" / "Drumcode 08" / "Analyser.mp3"


def test_build_dest_missing_artist_goes_to_unsorted(tmp_path):
    info = _info(None, "Drumcode 08", 1, "Analyser", Path("original.mp3"))
    assert build_dest_path(info, tmp_path) == tmp_path / "_Unsorted" / "original.mp3"


def test_build_dest_missing_title_goes_to_unsorted(tmp_path):
    info = _info("Adam Beyer", None, None, None, Path("original.mp3"))
    assert build_dest_path(info, tmp_path) == tmp_path / "_Unsorted" / "original.mp3"


def test_build_dest_sanitizes_illegal_chars(tmp_path):
    info = _info("Artist: Name", "Album/One", None, "Track: Title")
    result = build_dest_path(info, tmp_path)
    assert result == tmp_path / "Artist Name" / "AlbumOne" / "Track Title.mp3"


def test_build_dest_artist_all_illegal_chars_goes_to_unsorted(tmp_path):
    info = _info("///<>|", "Album", None, "Track", Path("original.mp3"))
    assert build_dest_path(info, tmp_path) == tmp_path / "_Unsorted" / "original.mp3"


def test_resolve_conflict_no_existing_file(tmp_path):
    dest = tmp_path / "track.mp3"
    assert resolve_conflict(dest, "keep-both") == dest


def test_resolve_conflict_skip_returns_none(tmp_path):
    dest = tmp_path / "track.mp3"
    dest.touch()
    assert resolve_conflict(dest, "skip") is None


def test_resolve_conflict_overwrite_returns_same_path(tmp_path):
    dest = tmp_path / "track.mp3"
    dest.touch()
    assert resolve_conflict(dest, "overwrite") == dest


def test_resolve_conflict_keep_both_appends_number(tmp_path):
    dest = tmp_path / "track.mp3"
    dest.touch()
    assert resolve_conflict(dest, "keep-both") == tmp_path / "track (2).mp3"


def test_resolve_conflict_keep_both_increments(tmp_path):
    dest = tmp_path / "track.mp3"
    dest.touch()
    (tmp_path / "track (2).mp3").touch()
    assert resolve_conflict(dest, "keep-both") == tmp_path / "track (3).mp3"


from djlibraryamp.organizer import process_library


def _make_tagged_mp3(path: Path, title=None, artist=None, album=None, tracknumber=None):
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK
    path.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 200)
    tags = ID3()
    if title:
        tags.add(TIT2(encoding=3, text=[title]))
    if artist:
        tags.add(TPE1(encoding=3, text=[artist]))
    if album:
        tags.add(TALB(encoding=3, text=[album]))
    if tracknumber:
        tags.add(TRCK(encoding=3, text=[tracknumber]))
    tags.save(str(path))


def test_process_library_dry_run_prints_not_copies(tmp_path, capsys):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _make_tagged_mp3(source / "track.mp3", title="Analyser", artist="Adam Beyer",
                     album="Drumcode 08", tracknumber="5")

    process_library(source, target, dry_run=True, conflict="keep-both")

    out = capsys.readouterr().out
    assert "[DRY RUN]" in out
    assert "Adam Beyer" in out
    assert not target.exists()


def test_process_library_copies_file(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _make_tagged_mp3(source / "track.mp3", title="Analyser", artist="Adam Beyer",
                     album="Drumcode 08", tracknumber="5")

    process_library(source, target, dry_run=False, conflict="keep-both")

    assert (target / "Adam Beyer" / "Drumcode 08" / "05 - Analyser.mp3").exists()
    assert (source / "track.mp3").exists()


def test_process_library_unsorted_when_no_tags_or_pattern(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    (source / "unknowntrack.mp3").write_bytes(b"\x00" * 100)

    process_library(source, target, dry_run=False, conflict="keep-both")

    assert (target / "_Unsorted" / "unknowntrack.mp3").exists()


def test_process_library_conflict_skip(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _make_tagged_mp3(source / "track.mp3", title="Analyser", artist="Adam Beyer", album="Drumcode 08")
    dest = target / "Adam Beyer" / "Drumcode 08" / "Analyser.mp3"
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"existing")

    process_library(source, target, dry_run=False, conflict="skip")

    assert dest.read_bytes() == b"existing"


def test_process_library_conflict_keep_both(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    _make_tagged_mp3(source / "track.mp3", title="Analyser", artist="Adam Beyer", album="Drumcode 08")
    dest = target / "Adam Beyer" / "Drumcode 08" / "Analyser.mp3"
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"existing")

    process_library(source, target, dry_run=False, conflict="keep-both")

    assert dest.exists()
    assert (target / "Adam Beyer" / "Drumcode 08" / "Analyser (2).mp3").exists()
