import sqlite3
from pathlib import Path

from app.schemas.analysis import AnalysisResult


class AnalysisStore:
    """Small immutable run snapshots; keep SQL isolated for later storage replacement."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def save(self, result: AnalysisResult) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO analyses VALUES (?, ?, ?)",
                (result.analysis_id, result.generated_at, result.model_dump_json()),
            )

    def get(self, analysis_id: str) -> AnalysisResult | None:
        with self.connect() as db:
            row = db.execute("SELECT payload FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        return AnalysisResult.model_validate_json(row[0]) if row else None
