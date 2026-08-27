from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_compose_contains_four_health_checked_services() -> None:
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]
    assert set(services) == {"frontend", "api", "postgres", "redis"}
    assert services["api"]["depends_on"]["postgres"]["condition"] == "service_healthy"
    assert services["api"]["depends_on"]["redis"]["condition"] == "service_healthy"
    assert "healthcheck" in services["api"]
    assert "healthcheck" in services["postgres"]
    assert "healthcheck" in services["redis"]


def test_env_example_documents_required_runtime_configuration() -> None:
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    for name in {
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DATABASE_URL",
        "VECTOR_STORE_BACKEND",
        "REDIS_URL",
        "REVIEW_CACHE_TTL_SECONDS",
        "TRACE_PATH",
    }:
        assert f"{name}=" in content
    assert "sk-" not in content


def test_frontend_uses_api_proxy_and_images_are_reproducible() -> None:
    script = (ROOT / "frontend/app.js").read_text(encoding="utf-8")
    nginx = (ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
    assert 'data-api-prefix="/api"' in (ROOT / "frontend/index.html").read_text(encoding="utf-8")
    assert "`${API_PREFIX}/review`" in script
    assert "`${API_PREFIX}/eval`" in script
    assert "proxy_pass http://api:8000/" in nginx
    assert (ROOT / "docker/api.Dockerfile").exists()
    assert (ROOT / "docker/frontend.Dockerfile").exists()
