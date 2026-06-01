from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

_SESSION_ID_RE = re.compile(r'^[A-Za-z0-9_-]+$')


def _safe_path(session_id: str, directory: Path | None = None) -> Path:
    """Validate session_id and return a path guaranteed inside target_dir."""
    if not _SESSION_ID_RE.match(session_id):
        raise ValueError(f"Invalid session_id: {session_id!r}")
    target_dir = (directory or DEFAULT_SESSION_DIR).resolve()
    file_path = (target_dir / f'{session_id}.json').resolve()
    if target_dir not in file_path.parents and file_path.parent != target_dir:
        raise ValueError("Path escapes session directory")
    return file_path


@dataclass(frozen=True)
class StoredSession:
    session_id: str
    messages: tuple[str, ...]
    input_tokens: int
    output_tokens: int


DEFAULT_SESSION_DIR = Path('.port_sessions')


def save_session(session: StoredSession, directory: Path | None = None) -> Path:
    target_dir = directory or DEFAULT_SESSION_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    path = _safe_path(session.session_id, directory)
    path.write_text(json.dumps(asdict(session), indent=2))
    return path


def load_session(session_id: str, directory: Path | None = None) -> StoredSession:
    path = _safe_path(session_id, directory)
    data = json.loads(path.read_text())
    return StoredSession(
        session_id=data['session_id'],
        messages=tuple(data['messages']),
        input_tokens=data['input_tokens'],
        output_tokens=data['output_tokens'],
    )
