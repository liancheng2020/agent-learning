import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app

SAMPLE = """diff --git a/src/LoginButton.jsx b/src/LoginButton.jsx
--- a/src/LoginButton.jsx
+++ b/src/LoginButton.jsx
@@ -1,1 +1,3 @@
+const result = await api.login();
+localStorage.setItem("token", result.token);
+return <img src=\"/avatar.png\" />;
"""


def main() -> None:
    response = TestClient(app).post("/review/stream", json={"diff_text": SAMPLE})
    for block in response.text.strip().split("\n\n"):
        event = re.search(r"^event: (.+)$", block, re.MULTILINE).group(1)
        data = json.loads(re.search(r"^data: (.+)$", block, re.MULTILINE).group(1))
        if event == "phase":
            print(f"[phase] {data['label']}")
        elif event == "tool":
            print(f"[tool]  {data['tool']}: {data['status']}")
        elif event == "final":
            result = data["result"]
            print(f"[final] {result['summary']} / risk={result['patch_plan']['risk']} / trace={result['trace_id']}")


if __name__ == "__main__":
    main()
