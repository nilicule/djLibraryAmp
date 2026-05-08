# Technical Details

## Architecture

| File | Responsibility |
|------|---------------|
| `cli.py` | Click entry point; parses arguments and delegates to `process_library` |
| `tags.py` | Reads ID3 tags via mutagen; falls back to filename pattern parsing |
| `organizer.py` | Builds destination paths; copies files; handles conflicts |

## Tag reading

Tags are read using mutagen's `easy=True` interface, which normalises ID3 frames to lowercase keys:

| Key | ID3 Frame | Used for |
|-----|-----------|----------|
| `artist` | TPE1 | Artist folder name |
| `album` | TALB | Album folder name |
| `title` | TIT2 | Filename |
| `tracknumber` | TRCK | Filename prefix (zero-padded to 2 digits) |

Track numbers stored as `N/total` (e.g. `3/12`) have the `/total` suffix stripped before use.

## Filename fallback

When artist or title tags are missing, the filename stem is split on ` - ` and the first two segments are used:

```
"Adam Beyer - Analyser - 5A - 140" → artist="Adam Beyer", title="Analyser"
```

If fewer than two segments are found, the file is placed in `_Unsorted/`.

## Destination path logic

```
target/Artist/Album/NN - Title.ext   # album tag present, track number present
target/Artist/Album/Title.ext        # album tag present, no track number
target/Artist/Singles/Title.ext      # no album tag
target/_Unsorted/original.ext        # artist or title could not be determined
```

Path components are sanitised by stripping characters illegal on macOS/Windows: `/ \ : * ? " < > |`

## Conflict handling

| Mode | Behaviour |
|------|-----------|
| `keep-both` (default) | Appends ` (2)`, ` (3)`, etc. until name is free |
| `skip` | Logs `[SKIP]` and leaves source file untouched |
| `overwrite` | Replaces the existing destination file |

## Running tests

```bash
uv run pytest -v
```
