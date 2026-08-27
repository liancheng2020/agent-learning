from __future__ import annotations

from difflib import unified_diff

from app.schemas import PatchArtifact


def generate_patch(approval_id: str, file_path: str, original_text: str, proposed_text: str) -> PatchArtifact:
    diff = "".join(
        unified_diff(
            original_text.splitlines(keepends=True),
            proposed_text.splitlines(keepends=True),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        )
    )
    return PatchArtifact(
        approval_id=approval_id,
        file_path=file_path,
        summary="审批通过后生成候选 Patch；本接口不会直接写入代码仓库。",
        unified_diff=diff,
    )
