import re

from app.schemas import Finding, ReviewResponse


def review_diff(diff_text: str) -> ReviewResponse:
    lines = diff_text.splitlines()
    file = _extract_file(lines)
    findings: list[Finding] = []
    current_line = 1

    for raw in lines:
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw)
        if hunk:
            current_line = int(hunk.group(1))
            continue
        if raw.startswith(("+++", "---", "-")):
            continue
        if raw.startswith("+"):
            code = raw[1:]
            if "await " in code:
                findings.append(Finding(
                    severity="high", category="error-handling", file=file,
                    line=current_line, message="异步调用需要确认失败处理。",
                    suggestion="增加 try/catch 和用户可见的错误状态。",
                ))
            if "<img" in code and "alt=" not in code:
                findings.append(Finding(
                    severity="medium", category="accessibility", file=file,
                    line=current_line, message="图片缺少 alt 属性。",
                    suggestion="补充有意义的 alt，装饰图片使用空 alt。",
                ))
            current_line += 1

    return ReviewResponse(summary=f"发现 {len(findings)} 个问题", findings=findings)


def _extract_file(lines: list[str]) -> str:
    for line in lines:
        if line.startswith("+++ b/"):
            return line.removeprefix("+++ b/")
    return "unknown"

