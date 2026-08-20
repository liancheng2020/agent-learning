import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.tools import build_registry

client = TestClient(app)


def test_agent_calls_three_tools() -> None:
    response = client.post("/review", json={"diff_text": "+++ b/App.jsx\n@@ -1 +1 @@\n+await api.load()"})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()["tool_calls"]] == ["read_diff", "search_knowledge", "generate_patch_plan"]


def test_tool_arguments_are_validated() -> None:
    with pytest.raises(ValidationError):
        build_registry().call("search_knowledge", {"query": "", "top_k": 99})


def test_registry_exposes_function_schemas() -> None:
    schemas = build_registry().schemas()
    assert {item["function"]["name"] for item in schemas} == {"read_diff", "search_knowledge", "generate_patch_plan"}

