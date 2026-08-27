from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.schemas import ApprovalAction, ApprovalRecord, ApprovalStatus


class ApprovalNotFound(LookupError):
    pass


class InvalidApprovalTransition(RuntimeError):
    pass


class ApprovalStore:
    backend = "sqlite"

    def __init__(self, database: Path) -> None:
        self.database = database
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    result_json TEXT,
                    created_at TEXT NOT NULL,
                    decided_at TEXT,
                    decided_by TEXT
                )
                """
            )

    def create(
        self,
        action: ApprovalAction,
        payload: dict[str, Any],
        requested_by: str,
        reason: str,
    ) -> ApprovalRecord:
        approval_id = f"apr_{uuid4().hex}"
        created_at = datetime.now(UTC)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO approvals VALUES (?, ?, 'pending', ?, ?, ?, NULL, ?, NULL, NULL)",
                (approval_id, action, requested_by, reason, json.dumps(payload, ensure_ascii=False), created_at.isoformat()),
            )
        return self.get(approval_id)

    def get(self, approval_id: str) -> ApprovalRecord:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        if row is None:
            raise ApprovalNotFound(approval_id)
        return self._to_record(row)

    def get_payload(self, approval_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT payload_json FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        if row is None:
            raise ApprovalNotFound(approval_id)
        return json.loads(row["payload_json"])

    def decide(self, approval_id: str, decision: ApprovalStatus, decided_by: str, reason: str) -> ApprovalRecord:
        if decision not in {"approved", "rejected"}:
            raise InvalidApprovalTransition(f"不支持的审批结果：{decision}")
        decided_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE approvals
                SET status = ?, decided_at = ?, decided_by = ?, reason = CASE WHEN ? = '' THEN reason ELSE ? END
                WHERE id = ? AND status = 'pending'
                """,
                (decision, decided_at, decided_by, reason, reason, approval_id),
            )
            if cursor.rowcount == 0:
                exists = connection.execute("SELECT status FROM approvals WHERE id = ?", (approval_id,)).fetchone()
                if exists is None:
                    raise ApprovalNotFound(approval_id)
                raise InvalidApprovalTransition(f"审批已是 {exists['status']}，不能再次决策")
        return self.get(approval_id)

    def require_approved(self, approval_id: str, action: ApprovalAction) -> ApprovalRecord:
        approval = self.get(approval_id)
        if approval.action != action:
            raise InvalidApprovalTransition(f"审批动作是 {approval.action}，不是 {action}")
        if approval.status != "approved":
            raise InvalidApprovalTransition(f"审批状态是 {approval.status}，禁止执行 {action}")
        return approval

    def save_result(self, approval_id: str, result: dict[str, Any]) -> ApprovalRecord:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE approvals SET result_json = ? WHERE id = ? AND status = 'approved' AND result_json IS NULL",
                (json.dumps(result, ensure_ascii=False), approval_id),
            )
            if cursor.rowcount == 0:
                raise InvalidApprovalTransition("只有未执行的 approved 审批可以保存执行结果")
        return self.get(approval_id)

    @staticmethod
    def _to_record(row: sqlite3.Row) -> ApprovalRecord:
        payload = json.loads(row["payload_json"])
        summary = {key: value for key, value in payload.items() if key not in {"original_text", "proposed_text"}}
        if "original_text" in payload or "proposed_text" in payload:
            summary["content_changed"] = payload.get("original_text") != payload.get("proposed_text")
        return ApprovalRecord(
            id=row["id"],
            action=row["action"],
            status=row["status"],
            requested_by=row["requested_by"],
            reason=row["reason"],
            payload_summary=summary,
            result=json.loads(row["result_json"]) if row["result_json"] else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            decided_at=datetime.fromisoformat(row["decided_at"]) if row["decided_at"] else None,
            decided_by=row["decided_by"],
        )


class PostgresApprovalStore:
    backend = "postgres"

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._initialize()

    def _connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    payload_json JSONB NOT NULL,
                    result_json JSONB,
                    created_at TIMESTAMPTZ NOT NULL,
                    decided_at TIMESTAMPTZ,
                    decided_by TEXT
                )
                """
            )

    def create(
        self,
        action: ApprovalAction,
        payload: dict[str, Any],
        requested_by: str,
        reason: str,
    ) -> ApprovalRecord:
        approval_id = f"apr_{uuid4().hex}"
        created_at = datetime.now(UTC)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO approvals
                (id, action, status, requested_by, reason, payload_json, created_at)
                VALUES (%s, %s, 'pending', %s, %s, %s::jsonb, %s)""",
                (approval_id, action, requested_by, reason, json.dumps(payload, ensure_ascii=False), created_at),
            )
        return self.get(approval_id)

    def get(self, approval_id: str) -> ApprovalRecord:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM approvals WHERE id = %s", (approval_id,)).fetchone()
        if row is None:
            raise ApprovalNotFound(approval_id)
        return self._to_record(row)

    def get_payload(self, approval_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT payload_json FROM approvals WHERE id = %s", (approval_id,)).fetchone()
        if row is None:
            raise ApprovalNotFound(approval_id)
        return row["payload_json"]

    def decide(self, approval_id: str, decision: ApprovalStatus, decided_by: str, reason: str) -> ApprovalRecord:
        if decision not in {"approved", "rejected"}:
            raise InvalidApprovalTransition(f"不支持的审批结果：{decision}")
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE approvals
                SET status = %s, decided_at = %s, decided_by = %s,
                    reason = CASE WHEN %s = '' THEN reason ELSE %s END
                WHERE id = %s AND status = 'pending'
                """,
                (decision, datetime.now(UTC), decided_by, reason, reason, approval_id),
            )
            if cursor.rowcount == 0:
                exists = connection.execute("SELECT status FROM approvals WHERE id = %s", (approval_id,)).fetchone()
                if exists is None:
                    raise ApprovalNotFound(approval_id)
                raise InvalidApprovalTransition(f"审批已是 {exists['status']}，不能再次决策")
        return self.get(approval_id)

    def require_approved(self, approval_id: str, action: ApprovalAction) -> ApprovalRecord:
        approval = self.get(approval_id)
        if approval.action != action:
            raise InvalidApprovalTransition(f"审批动作是 {approval.action}，不是 {action}")
        if approval.status != "approved":
            raise InvalidApprovalTransition(f"审批状态是 {approval.status}，禁止执行 {action}")
        return approval

    def save_result(self, approval_id: str, result: dict[str, Any]) -> ApprovalRecord:
        with self._connect() as connection:
            cursor = connection.execute(
                """UPDATE approvals SET result_json = %s::jsonb
                WHERE id = %s AND status = 'approved' AND result_json IS NULL""",
                (json.dumps(result, ensure_ascii=False), approval_id),
            )
            if cursor.rowcount == 0:
                raise InvalidApprovalTransition("只有未执行的 approved 审批可以保存执行结果")
        return self.get(approval_id)

    @staticmethod
    def _to_record(row: dict[str, Any]) -> ApprovalRecord:
        payload = row["payload_json"]
        summary = {key: value for key, value in payload.items() if key not in {"original_text", "proposed_text"}}
        if "original_text" in payload or "proposed_text" in payload:
            summary["content_changed"] = payload.get("original_text") != payload.get("proposed_text")
        return ApprovalRecord(
            id=row["id"],
            action=row["action"],
            status=row["status"],
            requested_by=row["requested_by"],
            reason=row["reason"],
            payload_summary=summary,
            result=row["result_json"],
            created_at=row["created_at"],
            decided_at=row["decided_at"],
            decided_by=row["decided_by"],
        )


def create_approval_store(database: Path | None = None):
    if database is not None:
        return ApprovalStore(database)
    if os.getenv("APP_DATABASE_BACKEND", "sqlite").lower() == "postgres":
        return PostgresApprovalStore(
            os.getenv("DATABASE_URL", "postgresql://agent:agent@127.0.0.1:5432/agent")
        )
    return ApprovalStore(Path(os.getenv("APPROVAL_DATABASE_PATH", "data/approvals.db")))
