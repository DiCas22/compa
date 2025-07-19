# utils.py
"""
Small cross‑platform helpers that do **not** depend on external packages.
Currently only `open_with_default_app` is exposed; more utilities can be
added here without touching the CLI layer.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _cmd_exists(cmd: str) -> bool:
    """Return True if *cmd* is found on $PATH."""
    return shutil.which(cmd) is not None


def open_with_default_app(path: Path) -> None:
    """
    Open *path* with the OS‑default GUI application and return immediately.

    Parameters
    ----------
    path : pathlib.Path
        File to open.  Must exist.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    RuntimeError
        If the platform is unsupported or no suitable opener is available.
    """
    path = Path(path)  # ensure Path
    if not path.exists():
        raise FileNotFoundError(path)

    # ── Linux ─────────────────────────────────────────────────────────── #
    if sys.platform.startswith("linux"):
        opener = None
        for candidate in ("xdg-open", "gio"):
            if _cmd_exists(candidate):
                opener = candidate
                break

        if opener:
            subprocess.Popen([opener, str(path)], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return
        raise RuntimeError("No xdg-open/gio found on PATH; cannot open files.")

    # ── macOS ─────────────────────────────────────────────────────────── #
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        return

    # ── Windows ───────────────────────────────────────────────────────── #
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
        return

    # ── Other / unsupported ───────────────────────────────────────────── #
    raise RuntimeError(f"Unsupported OS for 'open' command: {sys.platform}")
