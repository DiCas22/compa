# compa/compress.py
from __future__ import annotations

import pathlib
import subprocess
import tempfile
from pathlib import Path

import zstandard as zstd


# ────────────────────────────────────────────────────────────────────────── #
# Project‑wide storage directory
#   All new .zst archives are written here to keep the repo tidy.
#   ~/compa/
#       ├── compa/
#       └── files/          ← this folder (created on first run)
# ────────────────────────────────────────────────────────────────────────── #
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR: Path = PACKAGE_ROOT / "files"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


# ────────────────────────────────────────────────────────────────────────── #
# Helpers
# ────────────────────────────────────────────────────────────────────────── #
def _optimize_pdf(path: Path) -> Path:
    """
    Run Ghostscript in “/ebook” mode to shrink a PDF before compression.
    Returns the path to the temporary optimised PDF.
    """
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    subprocess.run(
        [
            "gs",
            "-q",
            "-dNOPAUSE",
            "-dBATCH",
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/ebook",
            f"-sOutputFile={out}",
            str(path),
        ],
        check=True,
    )
    return Path(out)


# ────────────────────────────────────────────────────────────────────────── #
# Public API
# ────────────────────────────────────────────────────────────────────────── #
def compress_file(
    path: Path,
    level: int = 19,
    threads: int = 0,
    pdf_opt: bool = True,
) -> Path:
    """
    Compress *path* with Zstandard and store the archive in ``files/``.
    If it's a PDF and *pdf_opt* is True, the file is first optimised via
    Ghostscript.

    Returns
    -------
    pathlib.Path
        Full path to the created ``.zst`` archive inside STORAGE_DIR.
    """
    src = _optimize_pdf(path) if pdf_opt and path.suffix.lower() == ".pdf" else path
    dst = STORAGE_DIR / (path.name + ".zst")

    cctx = zstd.ZstdCompressor(
        level=level,
        threads=threads or 0,  # 0 = auto‑detect CPU cores
        write_checksum=True,   # add xxhash64 frame checksum
    )

    with open(src, "rb") as fi, open(dst, "wb") as fo:
        cctx.copy_stream(fi, fo)

    if src is not path:  # remove temp optimised PDF
        src.unlink(missing_ok=True)

    return dst


def decompress_file(
    zst_path: Path,
    out_dir: Path | None = None,
) -> Path:
    """
    Decompress *zst_path* into *out_dir* (defaults to current directory) and
    return the path to the restored file.
    """
    zst_path = Path(zst_path)
    out_dir = Path.cwd() if out_dir is None else out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / zst_path.with_suffix("").name  # strip ".zst"
    dctx = zstd.ZstdDecompressor()

    with open(zst_path, "rb") as fin, open(out_path, "wb") as fout:
        dctx.copy_stream(fin, fout)

    return out_path
