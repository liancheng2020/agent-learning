import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas import ReviewPayload

client = TestClient(app)


def test_mock_provider_is_default() -> None:
    response = client.post("/review", json={"diff_text": "+++ b/App.jsx\n@@ -1 +1 @@\n+<img src=\"a.png\" />"})
    assert response.status_code == 200
    assert response.json()["provider"] == "mock"
    assert response.json()["findings"][0]["category"] == "accessibility"


def test_pydantic_rejects_unstable_model_json() -> None:
    with pytest.raises(ValidationError):
        ReviewPayload.model_validate_json('{"summary":"ok","findings":[{"severity":"urgent"}]}')

