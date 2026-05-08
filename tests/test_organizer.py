"""Tests for organizer module"""
from pathlib import Path
import pytest
from djlibraryamp.tags import TrackInfo
from djlibraryamp.organizer import sanitize, build_dest_path


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
