from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(ROOT, tmp_path / "approvals.db"))


def patch_request(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/patches/requests",
        json={
            "file_path": "src/auth.ts",
            "original_text": "const token = localStorage.getItem('token');\n",
            "proposed_text": "const token = secureTokenStore.get();\n",
            "requested_by": "review-agent",
            "reason": "避免长期凭据暴露给 XSS",
        },
    )
    assert response.status_code == 202
    return response.json()


def test_patch_is_pending_and_cannot_be_generated_before_approval(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    approval = patch_request(client)
    assert approval["status"] == "pending"
    assert approval["result"] is None
    assert "original_text" not in approval["payload_summary"]
    denied = client.post(f"/patches/{approval['id']}/generate")
    assert denied.status_code == 409


def test_approved_patch_is_generated_without_writing_source_file(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    approval = patch_request(client)
    decision = client.post(
        f"/approvals/{approval['id']}/decision",
        json={"decision": "approved", "decided_by": "tech-lead", "reason": "变更范围可控"},
    )
    assert decision.json()["status"] == "approved"
    generated = client.post(f"/patches/{approval['id']}/generate")
    assert generated.status_code == 200
    assert "--- a/src/auth.ts" in generated.json()["unified_diff"]
    assert "+const token = secureTokenStore.get();" in generated.json()["unified_diff"]
    assert not (tmp_path / "src/auth.ts").exists()


def test_rejected_patch_stays_blocked_and_decision_is_final(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    approval = patch_request(client)
    rejected = client.post(
        f"/approvals/{approval['id']}/decision",
        json={"decision": "rejected", "decided_by": "tech-lead", "reason": "缺少兼容方案"},
    )
    assert rejected.json()["status"] == "rejected"
    assert client.post(f"/patches/{approval['id']}/generate").status_code == 409
    second_decision = client.post(
        f"/approvals/{approval['id']}/decision",
        json={"decision": "approved", "decided_by": "other"},
    )
    assert second_decision.status_code == 409


def test_high_risk_operation_requires_approved_state(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    pending = client.post(
        "/operations/requests",
        json={"action": "deploy", "target": "production", "requested_by": "release-agent", "reason": "发布候选版本"},
    ).json()
    assert client.post(f"/operations/{pending['id']}/execute").status_code == 409
    client.post(
        f"/approvals/{pending['id']}/decision",
        json={"decision": "approved", "decided_by": "release-manager"},
    )
    executed = client.post(f"/operations/{pending['id']}/execute")
    assert executed.status_code == 200
    assert executed.json()["executed"] is True
    assert client.post(f"/operations/{pending['id']}/execute").status_code == 409


def test_review_and_health_remain_available(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    assert client.get("/health").json()["approval_store"] == "sqlite"
    review = client.post("/review", json={"diff_text": "+localStorage.setItem('accessToken', token);"})
    assert review.status_code == 200
    assert review.json()["findings"][0]["category"] == "security-token-storage"
