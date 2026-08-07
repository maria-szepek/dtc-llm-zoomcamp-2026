"""Load local Codex JSON/JSONL logs into DuckDB with dlt.

The pipeline stores each JSON record as raw text plus file metadata. That keeps
the first load resilient to heterogeneous Codex event schemas.
"""

from __future__ import annotations

import argparse
import fcntl
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import dlt

CODEX_HOME = Path.home() / ".codex"
DEFAULT_LOG_PATTERNS = (
    "sessions/**/*.jsonl",
    "history.jsonl",
    "session_index.jsonl",
)
PIPELINE_NAME = "codex_logs_to_duckdb"


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _json_metadata(raw_json: str) -> dict[str, Any]:
    try:
        value = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {
            "is_json_valid": False,
            "json_type": None,
            "parse_error": str(exc),
            "event_type": None,
            "event_timestamp": None,
            "session_id": None,
            "role": None,
            "top_level_keys": None,
        }

    metadata: dict[str, Any] = {
        "is_json_valid": True,
        "json_type": type(value).__name__,
        "parse_error": None,
        "event_type": None,
        "event_timestamp": None,
        "session_id": None,
        "role": None,
        "top_level_keys": None,
    }
    if isinstance(value, dict):
        metadata.update(
            {
                "event_type": value.get("type") or value.get("event_type"),
                "event_timestamp": value.get("timestamp") or value.get("ts"),
                "session_id": value.get("session_id") or value.get("conversation_id"),
                "role": value.get("role"),
                "top_level_keys": ",".join(sorted(str(key) for key in value)),
            }
        )
        metadata["event_type"] = _text_or_none(metadata["event_type"])
        metadata["event_timestamp"] = _text_or_none(metadata["event_timestamp"])
        metadata["session_id"] = _text_or_none(metadata["session_id"])
        metadata["role"] = _text_or_none(metadata["role"])
    return metadata


def _iter_log_files(codex_home: Path, patterns: tuple[str, ...]) -> Iterator[Path]:
    seen: set[Path] = set()
    for pattern in patterns:
        for path in sorted(codex_home.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            yield path


def _discover_log_files(codex_home: Path, patterns: tuple[str, ...]) -> list[Path]:
    """Return matching log files or raise a clear pipeline setup error."""

    if not codex_home.exists():
        raise FileNotFoundError(f"Codex log directory does not exist: {codex_home}")

    files = list(_iter_log_files(codex_home, patterns))
    if not files:
        pattern_list = ", ".join(patterns)
        raise FileNotFoundError(f"No Codex log files matched under {codex_home}: {pattern_list}")

    return files


def _format_bytes(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024 or unit == "GiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size_bytes} B"


@contextmanager
def _pipeline_run_lock(pipeline_name: str) -> Iterator[None]:
    lock_dir = Path(".dlt")
    lock_dir.mkdir(exist_ok=True)
    lock_path = lock_dir / f"{pipeline_name}.lock"

    with lock_path.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(
                f"Pipeline {pipeline_name!r} is already running. Wait for it to finish before starting another run."
            ) from exc

        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


@dlt.resource(
    name="codex_log_events",
    write_disposition="replace",
    columns={
        "source_file": {"data_type": "text"},
        "relative_path": {"data_type": "text"},
        "file_name": {"data_type": "text"},
        "file_size_bytes": {"data_type": "bigint"},
        "file_mtime": {"data_type": "text"},
        "record_number": {"data_type": "bigint"},
        "raw_json": {"data_type": "text"},
        "ingested_at": {"data_type": "text"},
        "is_json_valid": {"data_type": "bool"},
        "json_type": {"data_type": "text"},
        "parse_error": {"data_type": "text"},
        "event_type": {"data_type": "text"},
        "event_timestamp": {"data_type": "text"},
        "session_id": {"data_type": "text"},
        "role": {"data_type": "text"},
        "top_level_keys": {"data_type": "text"},
    },
)
def codex_log_events(
    codex_home: str = str(CODEX_HOME),
    patterns: tuple[str, ...] = DEFAULT_LOG_PATTERNS,
    limit_files: int | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield raw JSON records from local Codex log files."""

    root = Path(codex_home).expanduser()
    ingested_at = datetime.now(timezone.utc).isoformat()
    files = iter(_discover_log_files(root, patterns))
    if limit_files is not None:
        files = (path for index, path in enumerate(files) if index < limit_files)

    for path in files:
        stat = path.stat()
        relative_path = path.relative_to(root).as_posix()
        file_mtime = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()

        with path.open("r", encoding="utf-8") as file_obj:
            if path.suffix == ".jsonl":
                records = ((line_number, line.strip()) for line_number, line in enumerate(file_obj, 1))
            else:
                records = ((1, file_obj.read().strip()),)

            for record_number, raw_json in records:
                if not raw_json:
                    continue

                yield {
                    "source_file": str(path),
                    "relative_path": relative_path,
                    "file_name": path.name,
                    "file_size_bytes": stat.st_size,
                    "file_mtime": file_mtime,
                    "record_number": record_number,
                    "raw_json": raw_json,
                    "ingested_at": ingested_at,
                    **_json_metadata(raw_json),
                }


def load_codex_logs(sample: bool = False) -> None:
    """Load local Codex logs into DuckDB."""

    log_files = _discover_log_files(CODEX_HOME, DEFAULT_LOG_PATTERNS)
    selected_files = log_files[:1] if sample else log_files
    total_size = sum(path.stat().st_size for path in selected_files)
    print(
        "Discovered "
        f"{len(log_files)} matching log file(s); loading {len(selected_files)} "
        f"file(s), {_format_bytes(total_size)} total."
    )

    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination="duckdb",
        dataset_name="codex_raw",
    )

    resource = codex_log_events(limit_files=1 if sample else None)
    with _pipeline_run_lock(PIPELINE_NAME):
        load_info = pipeline.run(resource)
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Load only the first matching log file.",
    )
    args = parser.parse_args()
    load_codex_logs(sample=args.sample)


if __name__ == "__main__":
    main()
