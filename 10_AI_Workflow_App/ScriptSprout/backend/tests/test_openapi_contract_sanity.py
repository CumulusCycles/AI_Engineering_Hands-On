"""Sanity checks for critical OpenAPI response schema contracts."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _response_schema_ref(spec: dict, path: str, method: str, status_code: str) -> str | None:
    return (
        spec.get("paths", {})
        .get(path, {})
        .get(method, {})
        .get("responses", {})
        .get(status_code, {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
        .get("$ref")
    )


def test_openapi_response_contracts_for_critical_endpoints(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()

    expected = [
        ("/api/content/", "get", "200", "#/components/schemas/ContentListPage"),
        ("/api/content/", "post", "201", "#/components/schemas/ContentItemDetail"),
        (
            "/api/content/{content_id}/generate-story",
            "post",
            "200",
            "#/components/schemas/GenerateStoryResponse",
        ),
        ("/api/admin/metrics", "get", "200", "#/components/schemas/AdminMetricsResponse"),
        ("/api/admin/nlp-query", "post", "200", "#/components/schemas/AdminNlpQueryResponse"),
        ("/api/search/semantic", "post", "200", "#/components/schemas/SemanticSearchResponse"),
    ]
    for path, method, status_code, ref in expected:
        assert _response_schema_ref(spec, path, method, status_code) == ref
