# index_ini.py
from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from tempfile import NamedTemporaryFile

IDX = Path.home() / ".compa" / "topics.ini"
IDX.parent.mkdir(parents=True, exist_ok=True)


class Index:
    def __init__(self) -> None:
        self.cfg = ConfigParser(allow_no_value=True)
        self.cfg.read(IDX)

    # ────────────────────────────────────────────────────────────────── #
    # Helpers
    # ────────────────────────────────────────────────────────────────── #
    def _atomic_save(self) -> None:
        """
        Write the INI file via a temporary file + rename so updates
        remain atomic even if the process is interrupted.
        """
        with NamedTemporaryFile("w", delete=False, dir=IDX.parent) as tmp:
            self.cfg.write(tmp)
            tmp_path = Path(tmp.name)
        tmp_path.replace(IDX)

    # ────────────────────────────────────────────────────────────────── #
    # Public API
    # ────────────────────────────────────────────────────────────────── #
    def add(self, stored_path: Path, topics: list[str]) -> None:
        for topic in topics:
            if topic not in self.cfg:
                self.cfg.add_section(topic)
            self.cfg[topic][str(stored_path)] = None
        self._atomic_save()

    def query_all_of(self, topics: list[str]) -> list[Path]:
        """
        Return the list of files that belong to *all* the requested topics.
        """
        if not topics:
            return []

        # Build a set of filenames for each topic; if a topic doesn't exist,
        # the intersection is guaranteed to be empty.
        sets = []
        for t in topics:
            if t in self.cfg:
                sets.append(set(self.cfg[t].keys()))
            else:
                return []  # topic not found -> no matches

        result = set.intersection(*sets) if sets else set()
        return sorted(map(Path, result))
