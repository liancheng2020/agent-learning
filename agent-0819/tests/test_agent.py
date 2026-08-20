from pathlib import Path

from src.agent import ReviewAgent
from src.retrieval import KnowledgeRetriever
from src.service import build_index


def test_agent_automatically_calls_knowledge_for_each_finding(tmp_path: Path) -> None:
    corpus = Path(__file__).resolve().parents[2] / "agent-0816" / "knowledge"
    retriever = KnowledgeRetriever(build_index(corpus, tmp_path / "knowledge.db"))
    diff = """+++ b/src/Login.tsx
@@ -1 +1,4 @@
+const token: any = response.token;
+localStorage.setItem("authToken", token);
+return <div dangerouslySetInnerHTML={{ __html: bio }} />;
"""
    result = ReviewAgent(retriever).review(diff)
    categories = {item.category for item in result.findings}
    assert categories >= {"typescript-any", "security-token-storage", "security-xss"}
    assert len(result.tool_runs) == len(result.findings)
    assert all(run.status == "completed" for run in result.tool_runs)
    assert all(finding.citations and finding.citations[0].topic == finding.topic for finding in result.findings)
    assert result.model_validate_json(result.model_dump_json())
