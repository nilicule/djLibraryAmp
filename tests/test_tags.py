"""Tests for tags module"""
from pathlib import Path
from djlibraryamp.tags import TrackInfo, parse_filename


def test_parse_filename_standard():
    assert parse_filename("Adam Beyer - Analyser - 5A - 140") == ("Adam Beyer", "Analyser")


def test_parse_filename_exactly_two_segments():
    assert parse_filename("Adam Beyer - Analyser") == ("Adam Beyer", "Analyser")


def test_parse_filename_single_segment():
    assert parse_filename("Adam Beyer") == (None, None)


def test_parse_filename_empty():
    assert parse_filename("") == (None, None)


def test_parse_filename_strips_whitespace():
    assert parse_filename("Adam Beyer  -  Analyser  - 5A") == ("Adam Beyer", "Analyser")


from djlibraryamp.tags import read_tags


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


def test_read_tags_full_id3(tmp_path):
    mp3 = tmp_path / "track.mp3"
    _make_tagged_mp3(mp3, title="Analyser", artist="Adam Beyer", album="Drumcode 08", tracknumber="3/12")

    info = read_tags(mp3)

    assert info.title == "Analyser"
    assert info.artist == "Adam Beyer"
    assert info.album == "Drumcode 08"
    assert info.track_number == 3
    assert info.original_path == mp3


def test_read_tags_track_number_no_total(tmp_path):
    mp3 = tmp_path / "track.mp3"
    _make_tagged_mp3(mp3, title="Analyser", artist="Adam Beyer", tracknumber="5")

    info = read_tags(mp3)

    assert info.track_number == 5


def test_read_tags_falls_back_to_filename(tmp_path):
    mp3 = tmp_path / "Adam Beyer - Analyser - 5A - 140.mp3"
    mp3.write_bytes(b"\x00" * 100)

    info = read_tags(mp3)

    assert info.artist == "Adam Beyer"
    assert info.title == "Analyser"
    assert info.album is None
    assert info.track_number is None


def test_read_tags_no_tags_no_pattern(tmp_path):
    mp3 = tmp_path / "trackwithnoinfo.mp3"
    mp3.write_bytes(b"\x00" * 100)

    info = read_tags(mp3)

    assert info.artist is None
    assert info.title is None


def test_read_tags_malformed_track_number(tmp_path):
    mp3 = tmp_path / "track.mp3"
    _make_tagged_mp3(mp3, title="Analyser", artist="Adam Beyer", tracknumber="ABC/12")

    info = read_tags(mp3)

    assert info.track_number is None
    assert info.title == "Analyser"
