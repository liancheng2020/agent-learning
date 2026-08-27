from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_resume_has_three_target_role_versions() -> None:
    resume = (ROOT / "RESUME.md").read_text(encoding="utf-8")
    for role in ("AI 前端开发", "AI 应用全栈", "Agent 应用开发"):
        assert role in resume
    assert "12 条" in resume
    assert "22 条自动化测试" in resume


def test_interview_material_contains_ten_answers() -> None:
    interview = (ROOT / "INTERVIEW.md").read_text(encoding="utf-8")
    numbered = [line for line in interview.splitlines() if line.startswith("## ") and line[3:4].isdigit()]
    assert len(numbered) == 10


def test_application_tracker_is_actionable() -> None:
    tracker = (ROOT / "APPLICATION_TRACKER.md").read_text(encoding="utf-8")
    assert "每日动作" in tracker
    assert "投递记录" in tracker
    assert "精投 3 个" in tracker
