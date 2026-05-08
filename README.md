# djLibraryAmp

Organizes a flat collection of audio files into a Plexamp-compatible folder structure using ID3 tags.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
git clone <repo>
cd djLibraryAmp
uv sync
```

## Usage

```bash
uv run djlibraryamp SOURCE TARGET [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `SOURCE` | Directory to scan recursively for audio files |
| `TARGET` | Directory where organized files will be written |

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Print what would happen without copying anything |
| `--conflict skip\|overwrite\|keep-both` | How to handle filename conflicts (default: `keep-both`) |
| `--help` | Show help message |

### Examples

```bash
# Preview what would happen
uv run djlibraryamp ~/Music/Unsorted ~/Music/Library --dry-run

# Copy files, keeping both on conflict
uv run djlibraryamp ~/Music/Unsorted ~/Music/Library

# Copy files, skipping duplicates
uv run djlibraryamp ~/Music/Unsorted ~/Music/Library --conflict skip
```

## Output structure

```
Library/
├── Adam Beyer/
│   ├── Drumcode 08/
│   │   ├── 01 - Code Red.mp3
│   │   └── 02 - Analyser.mp3
│   └── Singles/
│       └── Discipline.mp3
└── _Unsorted/
    └── unrecognised_file.mp3
```

Supported formats: `.mp3` `.flac` `.aac` `.m4a` `.wav` `.ogg`

See [docs/TECHNICAL.md](docs/TECHNICAL.md) for implementation details.
