from __future__ import annotations

import json
from typing import Any

from app.approval import InvalidApprovalTransition
from app.schemas import DrillResult, FaultScenario
from app.trace import TraceStore


class FaultDrillError(RuntimeError):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        suggestion: str,
        status_code: int,
        trace_id: str,
        retryable: bool,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion
        self.status_code = status_code
        self.trace_id = trace_id
        self.retryable = retryable


class FaultDrillService:
    def __init__(self, approvals: Any, traces: TraceStore) -> None:
        self.approvals = approvals
        self.traces = traces

    def run(self, scenario: FaultScenario) -> DrillResult:
        trace_id = self.traces.start("fault-drill-v1", {"scenario": scenario})
        self.traces.emit(trace_id, "drill.injected", scenario=scenario)

        if scenario == "model_timeout":
            self._fail(
                trace_id,
                code="MODEL_TIMEOUT",
                message="模型响应超时，本次审查没有生成不完整结果。",
                suggestion="请稍后重试；连续失败时切换备用模型或缩小 Diff。",
                status_code=504,
                retryable=True,
            )
        if scenario == "tool_exception":
            self._fail(
                trace_id,
                code="TOOL_EXECUTION_FAILED",
                message="知识检索工具执行异常，Agent 已停止依赖该工具继续推断。",
                suggestion="检查工具 trace 和依赖状态，恢复后重新运行。",
                status_code=502,
                retryable=True,
            )
        if scenario == "empty_retrieval":
            return self._complete(
                trace_id,
                scenario,
                status="degraded",
                code="KNOWLEDGE_NOT_FOUND",
                message="知识库没有命中可引用规范，结果已降级且不会伪造引用。",
                suggestion="补充查询关键词、放宽过滤条件或完善知识库后重试。",
            )
        if scenario == "invalid_json":
            try:
                json.loads('{"summary": "broken"')
            except json.JSONDecodeError:
                self._fail(
                    trace_id,
                    code="MODEL_JSON_INVALID",
                    message="模型返回内容无法解析为约定 JSON，结果已被拒绝。",
                    suggestion="重试一次；仍失败时检查结构化输出 Schema 和 Prompt 版本。",
                    status_code=502,
                    retryable=True,
                )
        if scenario == "approval_rejected":
            approval = self.approvals.create(
                "deploy",
                {"target": "production"},
                "fault-drill",
                "演练高风险操作拒绝流程",
            )
            rejected = self.approvals.decide(
                approval.id,
                "rejected",
                "reviewer",
                "演练：风险条件未满足",
            )
            try:
                self.approvals.require_approved(rejected.id, "deploy")
            except InvalidApprovalTransition:
                return self._complete(
                    trace_id,
                    scenario,
                    status="blocked",
                    code="APPROVAL_REJECTED",
                    message="审批已拒绝，生产操作未执行。",
                    suggestion="修正风险项后创建新的审批申请，原审批决定不可覆盖。",
                    details={"approval_id": rejected.id, "approval_status": rejected.status},
                )
        raise ValueError(f"unsupported scenario: {scenario}")

    def _complete(
        self,
        trace_id: str,
        scenario: FaultScenario,
        *,
        status: str,
        code: str,
        message: str,
        suggestion: str,
        details: dict[str, Any] | None = None,
    ) -> DrillResult:
        self.traces.emit(trace_id, "drill.completed", status=status, code=code, details=details or {})
        return DrillResult(
            scenario=scenario,
            status=status,
            code=code,
            message=message,
            suggestion=suggestion,
            trace_id=trace_id,
            details=details or {},
        )

    def _fail(self, trace_id: str, **payload: Any) -> None:
        self.traces.emit(trace_id, "drill.failed", code=payload["code"], message=payload["message"])
        raise FaultDrillError(trace_id=trace_id, **payload)
