import pytest
from pathlib import Path


@pytest.fixture
def make_tagged_mp3():
    def _make(path: Path, title=None, artist=None, album=None, tracknumber=None):
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
    return _make
