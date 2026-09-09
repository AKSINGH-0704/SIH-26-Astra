"""API contract tests. The frontend renders exactly these payloads."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from astra.main import app


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_health_reports_real_state(client: TestClient) -> None:
    payload = client.get("/health").json()
    assert payload["status"] == "ok"
    assert payload["fixtures_valid"] is True
    assert payload["model_config_version"]
    assert payload["engine_version"]


def test_health_reports_template_mode_when_no_llm_key_is_configured(
    client: TestClient,
) -> None:
    """The demo must run identically with the LLM disabled, and say so."""
    assert client.get("/health").json()["llm_mode"] == "template"


def test_model_config_exposes_every_constant_with_provenance(client: TestClient) -> None:
    payload = client.get("/model/config").json()
    assert payload["constants"], "the transparency panel needs the constants"
    for constant in payload["constants"]:
        assert constant["provenance"] in {
            "REAL_OPEN",
            "DERIVED",
            "SYNTHETIC_CALIBRATED",
            "DEMO_CONFIG",
        }
        assert constant["description"]
        if constant["provenance"] != "DEMO_CONFIG":
            assert constant["citation"]


def test_model_config_serves_the_formula_registry(client: TestClient) -> None:
    payload = client.get("/model/config").json()
    formula_ids = {spec["formula_id"] for spec in payload["formulas"]}
    assert {"hazard.composite", "priority.score", "capacity.effective"} <= formula_ids


def test_model_config_serves_the_standing_notices(client: TestClient) -> None:
    notices = client.get("/model/config").json()["notices"]
    assert "never to produce them" in notices["how_this_works"]
    assert "SDMA" in notices["decision_authority"]


def test_provenance_lists_datasets_and_unblended_counts(client: TestClient) -> None:
    payload = client.get("/provenance").json()
    assert payload["datasets"]
    assert sum(payload["counts_by_class"].values()) == len(payload["datasets"])
    for dataset in payload["datasets"]:
        assert dataset["processing"]
        assert dataset["licence"]
        if dataset["provenance"] == "REAL_OPEN":
            assert dataset["source_url"]


def test_layers_declare_availability_honestly(client: TestClient) -> None:
    payload = client.get("/layers").json()
    assert payload["declared_count"] == len(payload["layers"])
    assert payload["available_count"] == sum(1 for layer in payload["layers"] if layer["available"])


def test_available_layers_resolve_registered_datasets(client: TestClient) -> None:
    layers = client.get("/layers").json()["layers"]
    registered = {d["id"] for d in client.get("/provenance").json()["datasets"]}
    for layer in layers:
        if layer["available"]:
            assert set(layer["dataset_ids"]) <= registered


def test_fixture_validation_is_visible_through_the_api(client: TestClient) -> None:
    payload = client.get("/validation/fixtures").json()
    assert payload["ok"] is True
    assert payload["checks"]
    assert payload["errors"] == []


def test_baseline_scenario_carries_its_study_area_and_disclaimer(client: TestClient) -> None:
    payload = client.get("/scenarios/baseline").json()
    assert payload["scenario"]["is_baseline"] is True
    assert "synthetic" in payload["scenario"]["disclaimer"]
    bbox = payload["study_area"]["bbox"]
    assert bbox["min_lon"] < bbox["max_lon"] and bbox["min_lat"] < bbox["max_lat"]
    assert payload["study_area"]["district"] == "Chamoli"


def test_unknown_scenario_is_a_404_not_an_empty_object(client: TestClient) -> None:
    assert client.get("/scenarios/does-not-exist").status_code == 404


def test_openapi_schema_is_complete_enough_to_generate_types(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    components = schema["components"]["schemas"]
    for name in ("HealthStatus", "ModelConfigResponse", "ProvenanceResponse", "LayersResponse"):
        assert name in components
    for path in ("/health", "/model/config", "/provenance", "/layers", "/scenarios"):
        assert path in schema["paths"]


def test_habitations_are_served_with_their_totals_and_disclaimer(client: TestClient) -> None:
    payload = client.get("/habitations").json()
    assert len(payload["habitations"]) == 12
    assert payload["total_population"] == sum(
        h["population"] for h in payload["habitations"]
    )
    assert payload["total_households"] == sum(
        h["households"] for h in payload["habitations"]
    )
    assert "synthetic" in payload["disclaimer"]
    for habitation in payload["habitations"]:
        assert habitation["provenance"] == "SYNTHETIC_CALIBRATED"


def test_sites_are_served_with_the_tenure_limitation_stated(client: TestClient) -> None:
    payload = client.get("/sites").json()
    assert len(payload["sites"]) == 6
    assert "ownership" in payload["limitation"]
    assert payload["total_gross_area_m2"] > 0


def test_study_area_data_reports_what_was_actually_computed(client: TestClient) -> None:
    payload = client.get("/study-area/data").json()
    names = {layer["name"] for layer in payload["layers"]}
    assert {"slope_deg", "hand_m", "drainage", "road_distance_m"} <= names
    assert payload["grid"]["rows"] > 0 and payload["grid"]["cols"] > 0
    assert "Horn" in payload["methods"]["slope"]
    assert payload["generation"]["measured_from_real_data"]
    assert payload["generation"]["assumed_not_measured"]


def test_derived_layer_ranges_are_physically_plausible(client: TestClient) -> None:
    layers = {
        layer["name"]: layer for layer in client.get("/study-area/data").json()["layers"]
    }
    assert 0.0 <= layers["slope_deg"]["min"] and layers["slope_deg"]["max"] <= 90.0
    assert layers["hand_m"]["min"] >= 0.0
    assert layers["drainage"]["max"] == 1.0


def test_terrain_preview_is_a_real_image(client: TestClient) -> None:
    response = client.get("/study-area/terrain.jpg")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 50_000


def test_layers_flip_to_available_only_when_their_artifacts_exist(client: TestClient) -> None:
    layers = {layer["id"]: layer for layer in client.get("/layers").json()["layers"]}
    # Landed in slices 1 and 2.
    assert layers["terrain.slope"]["available"] is True
    assert layers["exposure.habitations"]["available"] is True
    assert layers["network.roads"]["available"] is True
    # Not built yet: the catalogue must not claim them.
    assert layers["hazard.composite"]["available"] is False
    assert layers["plan.assignments"]["available"] is False
