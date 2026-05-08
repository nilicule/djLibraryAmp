import click
from pathlib import Path
from .organizer import process_library


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("target", type=click.Path(file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Print what would happen, copy nothing")
@click.option(
    "--conflict",
    type=click.Choice(["skip", "overwrite", "keep-both"]),
    default="keep-both",
    show_default=True,
    help="How to handle destination conflicts",
)
def main(source: Path, target: Path, dry_run: bool, conflict: str) -> None:
    """Organize audio files from SOURCE into TARGET based on ID3 tags."""
    process_library(source, target, dry_run=dry_run, conflict=conflict)
