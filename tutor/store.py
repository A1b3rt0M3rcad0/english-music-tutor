"""Primitivas de I/O atômicas. JSON para estado; YAML legível para configuração."""
from __future__ import annotations
import json
import os
import re
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


def root() -> Path:
    return Path(os.environ.get("TUTOR_WORKSPACE", Path.cwd())).resolve()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def today() -> str:
    return date.today().isoformat()


def slug(text: str) -> str:
    import unicodedata
    ascii_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    clean = re.sub(r'[^a-z0-9]+', '-', ascii_text.lower()).strip('-')
    return clean[:75] or "item"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("Instale dependências: python -m pip install -e .") from e
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_yaml(path: Path, value: dict) -> None:
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("Instale dependências: python -m pip install -e .") from e
    write_text(path, yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=100))


def state_path(base: Path) -> Path:
    return base / "data" / "state.json"


def state(base: Path) -> dict:
    return read_json(state_path(base), {
        "onboarded": False, "diagnostic_done": False,
        "roadmap_ready": False, "active_song": None, "songs_completed": 0,
        "session_events": []
    })


def save_state(base: Path, value: dict) -> None:
    write_json(state_path(base), value)


def event(base: Path, kind: str, fields: dict) -> None:
    path = base / "data" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": now(), "kind": kind, **fields}, ensure_ascii=False) + "\n")


def require_workspace(base: Path) -> None:
    if not (base / "config.yaml").exists():
        raise ValueError(f"Não há config.yaml em {base}. Crie um workspace com bootstrap.py.")
