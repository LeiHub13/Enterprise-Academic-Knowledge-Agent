"""文档元数据存储（SQLite，标准库实现，零额外服务）。

向量本体在 Milvus；这里只存文档级元数据（文件名、切片数、上传时间），
并通过 doc_id 与 Milvus 中每个 chunk 的 metadata 关联。
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "metadata.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def add_document(doc_id: str, filename: str, chunk_count: int, status: str = "ready") -> None:
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO documents (id, filename, chunk_count, status, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                doc_id,
                filename,
                chunk_count,
                status,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )


def list_documents() -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM documents ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_document(doc_id: str) -> None:
    with _conn() as c:
        c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
