from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_readme_contains_required_sections() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for section in ("## 架构", "## 技术选型", "## 快速运行", "## 评测结果", "## 失败处理"):
        assert section in readme
    assert "```mermaid" in readme
    assert "./docs/demo.png" in readme
    assert "./docs/demo.gif" in readme


def test_demo_assets_exist_and_are_not_empty() -> None:
    for name in ("demo.png", "demo.gif"):
        asset = ROOT / "docs" / name
        assert asset.exists()
        assert asset.stat().st_size > 1_000
