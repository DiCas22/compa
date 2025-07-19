# cli.py
from __future__ import annotations

import pathlib
import subprocess
import tempfile
import time
import shutil
import sys

import typer

from .compress import compress_file, decompress_file
from .index_ini import Index
from .utils import open_with_default_app
from .search import search_command  # import the search command

app = typer.Typer(no_args_is_help=True)
idx = Index()  # loads ~/.compa/topics.ini


# ────────────────────────────────────────────────────────────────────────── #
# Core commands
# ────────────────────────────────────────────────────────────────────────── #
@app.command()
def compress(
    file: pathlib.Path,
    topics: str = typer.Option(
        "", "--topics", "-t", help="Comma‑separated topic list"
    ),
    level: int = 19,
    threads: int = 0,
    pdf_opt: bool = True,
) -> None:
    """
    Compress *file* with Zstandard (level 19 by default) and tag it with *topics*.
    """
    stored = compress_file(file, level, threads, pdf_opt)
    idx.add(stored, [t.strip() for t in topics.split(",") if t])
    typer.echo(f"Saved → {stored}")


@app.command()
def decompress(
    file: pathlib.Path,
    out: pathlib.Path = typer.Option(
        pathlib.Path("."), "--out", "-o", help="Destination directory"
    ),
) -> None:
    """
    Decompress *file* (a .zst archive) into *out*.
    """
    restored = decompress_file(file, out)
    typer.echo(f"Restored → {restored}")


@app.command("list")
def list_files(
    topics: str = typer.Argument(..., help="Comma‑separated topics to filter by")
) -> None:
    """
    List compressed files that belong to *all* specified topics.
    """
    topic_list = [t.strip() for t in topics.split(",") if t]
    paths = idx.query_all_of(topic_list)
    if paths:
        for p in paths:
            typer.echo(p)
    else:
        typer.echo("(no matches)")


# ────────────────────────────────────────────────────────────────────────── #
# One‑shot “open” command
# ────────────────────────────────────────────────────────────────────────── #
@app.command()
def open(
    file: pathlib.Path,
    keep_temp: bool = typer.Option(
        False, "--keep-temp", help="Keep the temporary copy instead of deleting"
    ),
    wait: int = typer.Option(
        0,
        "--wait",
        "-w",
        help="Seconds to wait before deleting. 0 = wait for user to press ENTER.",
    ),
) -> None:
    """
    Decompress *file* to a temporary location, open it with the system’s
    default application, and delete the temporary copy afterwards.
    """
    with tempfile.TemporaryDirectory(prefix="compa_") as tmpdir:
        tmp_dir = pathlib.Path(tmpdir)
        tmp_file = decompress_file(file, tmp_dir)

        typer.echo(f"Opening {tmp_file} …")
        open_with_default_app(tmp_file)

        if wait > 0:
            time.sleep(wait)
        else:
            typer.echo("Press ENTER when done to delete the temporary copy.")
            input()

        if keep_temp:
            final_path = pathlib.Path.cwd() / tmp_file.name
            shutil.move(tmp_file, final_path)
            typer.echo(f"Kept temporary copy at {final_path}")
        # else: TemporaryDirectory context removes the file automatically


# ────────────────────────────────────────────────────────────────────────── #
# Search command
# ────────────────────────────────────────────────────────────────────────── #
app.command(name="search")(search_command)


if __name__ == "__main__":
    app()
