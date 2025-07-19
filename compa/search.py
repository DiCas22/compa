# compa/search.py
from __future__ import annotations

import io
import re
import tempfile
import subprocess
from pathlib import Path

import zstandard as zstd
import typer

from .compress import STORAGE_DIR, decompress_file

def find_with_context(text: str, query: str, ctx: int) -> list[str]:
    """
    Return all snippets containing `query`, with `ctx` characters of context
    on each side, lines collapsed to spaces.
    """
    results: list[str] = []
    pattern = re.escape(query)
    for m in re.finditer(pattern, text, flags=re.IGNORECASE):
        start = max(m.start() - ctx, 0)
        end = min(m.end() + ctx, len(text))
        snippet = text[start:end].replace("\n", " ")
        results.append(snippet.strip())
    return results

def streaming_search(archive: Path, query: str, ctx: int) -> list[str]:
    """
    Decompress `archive` on the fly and search for `query` in its text.
    Returns list of snippets.
    """
    snippets: list[str] = []
    dctx = zstd.ZstdDecompressor()
    with open(archive, "rb") as fin, dctx.stream_reader(fin) as reader:
        text_stream = io.TextIOWrapper(reader, encoding="utf-8", errors="ignore")
        for line in text_stream:
            if query.lower() in line.lower():
                snippets.extend(find_with_context(line, query, ctx))
    return snippets

def pdf_search(archive: Path, query: str, ctx: int) -> list[str]:
    """
    Decompress a `.pdf.zst` archive, extract text via pdftotext, then search.
    """
    snippets: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp_pdf = decompress_file(archive, Path(td))
        try:
            txt_bytes = subprocess.check_output(
                ["pdftotext", "-layout", str(tmp_pdf), "-"],
                stderr=subprocess.DEVNULL
            )
            text = txt_bytes.decode("utf-8", "ignore")
        except FileNotFoundError:
            typer.echo("Error: `pdftotext` not found; install poppler-utils.", err=True)
            return []
    return find_with_context(text, query, ctx)

def search_command(
    query: str = typer.Argument(..., help="Phrase to search for"),
    context: int = typer.Option(50, "--context", "-c", help="Chars of context"),
) -> None:
    """
    Search all `.zst` archives for QUERY and print filename: snippet.
    """
    for archive in Path(STORAGE_DIR).glob("*.zst"):
        if archive.name.lower().endswith(".pdf.zst"):
            matches = pdf_search(archive, query, context)
        else:
            matches = streaming_search(archive, query, context)

        for snip in matches:
            typer.echo(f"{archive.name}: \"{snip}\"")
