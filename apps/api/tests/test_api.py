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
    assert layers["network.routes"]["available"] is False
    assert layers["plan.assignments"]["available"] is False


def test_risk_summary_reports_what_was_computed(client: TestClient) -> None:
    payload = client.get("/risk/summary").json()
    assert set(payload["class_share_percent"]) == {"LOW", "WATCH", "ELEVATED", "CRITICAL"}
    assert sum(payload["class_share_percent"].values()) == pytest.approx(100.0, abs=0.2)
    assert payload["hazards_modelled"] == ["LANDSLIDE", "FLOOD", "CLOUDBURST"]
    assert payload["incidents_used"] > 0
    assert payload["grid_rows"] > 100 and payload["grid_cols"] > 100


def test_zones_carry_their_arithmetic_and_never_claim_authority(client: TestClient) -> None:
    payload = client.get("/risk/zones").json()
    assert payload["classification_label"] == "ASTRA analytical classification"
    assert "SDMA" in payload["decision_authority"]
    assert payload["features"], "the baseline scenario must produce zones"
    for feature in payload["features"]:
        properties = feature["properties"]
        assert properties["classification_label"] == "ASTRA analytical classification"
        assert properties["max_composite"] >= properties["mean_composite"]
        assert properties["area_km2"] > 0
        assert properties["cell_count"] > 0
        assert properties["rule_version"]
        assert properties["dominant_hazard"] in {"LANDSLIDE", "FLOOD", "CLOUDBURST"}


def test_zone_population_totals_agree_with_the_habitation_layer(client: TestClient) -> None:
    zones = client.get("/risk/zones").json()
    habitations = {h["id"]: h for h in client.get("/habitations").json()["habitations"]}
    for feature in zones["features"]:
        properties = feature["properties"]
        expected = sum(
            habitations[habitation_id]["population"]
            for habitation_id in properties["habitation_ids"]
        )
        assert properties["population_intersected"] == expected


def test_risk_cell_decomposes_the_score_into_its_factors(client: TestClient) -> None:
    payload = client.get("/risk/cell", params={"lon": 79.56, "lat": 30.55}).json()
    hazard = payload["hazard"]
    assert 0 <= hazard["composite"] <= 100
    assert hazard["classification_label"] == "ASTRA analytical classification"
    assert payload["formula"]["formula_id"] == "hazard.hsi"
    assert payload["composite_formula"]["formula_id"] == "hazard.composite"

    for score in hazard["per_hazard"]:
        weights = sum(factor["weight"] for factor in score["factors"])
        assert weights == pytest.approx(1.0, abs=1e-6), "factor weights must sum to 1"
        recomputed = 100.0 * sum(factor["contribution"] for factor in score["factors"])
        assert recomputed == pytest.approx(score["score"], abs=0.05), (
            "the published score must equal the sum of its published contributions"
        )
        for factor in score["factors"]:
            assert factor["contribution"] == pytest.approx(
                factor["weight"] * factor["normalised_value"], abs=1e-6
            )


def test_composite_equals_dominance_preserving_formula(client: TestClient) -> None:
    payload = client.get("/risk/cell", params={"lon": 79.5, "lat": 30.45}).json()
    config = client.get("/model/config").json()["config"]
    lam = config["hazard"]["composite_lambda"]["value"]
    scores = sorted((score["score"] for score in payload["hazard"]["per_hazard"]), reverse=True)
    expected = min(100.0, scores[0] + lam * scores[1])
    assert payload["hazard"]["composite"] == pytest.approx(expected, abs=0.05)


def test_confidence_is_reported_separately_from_the_score(client: TestClient) -> None:
    payload = client.get("/risk/cell", params={"lon": 79.5, "lat": 30.45}).json()
    confidence = payload["confidence"]
    assert 0.0 <= confidence["value"] <= 1.0
    assert confidence["band"] in {"HIGH", "MEDIUM", "LOW"}
    assert "never multiplied into it" in confidence["note"]


def test_risk_cell_outside_the_grid_is_a_404(client: TestClient) -> None:
    assert client.get("/risk/cell", params={"lon": 77.2, "lat": 28.6}).status_code == 404


def test_habitation_hazard_rows_are_ranked_and_labelled(client: TestClient) -> None:
    payload = client.get("/risk/habitations").json()
    rows = payload["habitations"]
    assert len(rows) == 12
    composites = [row["hazard"]["composite"] for row in rows]
    assert composites == sorted(composites, reverse=True)
    assert "not a probability" in payload["note"]
    for row in rows:
        assert row["footprint_max_composite"] >= row["footprint_mean_composite"]
        assert row["confidence"]["band"] in {"HIGH", "MEDIUM", "LOW"}


def test_hazard_layers_are_now_available_in_the_catalogue(client: TestClient) -> None:
    layers = {layer["id"]: layer for layer in client.get("/layers").json()["layers"]}
    assert layers["hazard.composite"]["available"] is True
    assert layers["hazard.red_zones"]["available"] is True
    assert layers["hazard.confidence"]["available"] is True
    # Still not built: the catalogue must keep saying so.
    assert layers["network.routes"]["available"] is False
    assert layers["plan.assignments"]["available"] is False


def test_roads_geojson_is_served_for_the_map(client: TestClient) -> None:
    payload = client.get("/layers/roads.geojson").json()
    assert payload["properties"]["road_ways"] > 0
    assert payload["features"][0]["geometry"]["type"] == "LineString"


def test_priority_ranking_is_served_with_its_weights_and_thresholds(client: TestClient) -> None:
    payload = client.get("/priority/habitations").json()
    assert len(payload["habitations"]) == 12
    assert payload["weights"]["hazard"] + payload["weights"]["exposure"] + payload[
        "weights"
    ]["vulnerability"] + payload["weights"]["history"] == pytest.approx(1.0, abs=1e-9)
    assert set(payload["tier_thresholds"]) == {"IMMEDIATE", "SHORT_TERM", "MEDIUM_TERM"}
    assert "not a probability" in payload["priority_note"]
    assert "SDMA" in payload["decision_authority"]


def test_priority_rows_publish_the_arithmetic_behind_the_score(client: TestClient) -> None:
    for row in client.get("/priority/habitations").json()["habitations"]:
        recomputed = 100.0 * sum(f["contribution"] for f in row["priority_factors"])
        assert recomputed == pytest.approx(row["priority_score"], abs=0.02)
        for factor in row["priority_factors"]:
            assert factor["contribution"] == pytest.approx(
                factor["weight"] * factor["normalised_value"], abs=1e-6
            )
        for component in ("hazard_component", "exposure", "vulnerability", "history"):
            block = row[component]
            assert 0.0 <= block["value"] <= 1.0
            assert block["factors"]
            assert block["formula_id"]


def test_hazard_exposure_and_vulnerability_are_reported_separately(client: TestClient) -> None:
    """The three quantities must never arrive pre-collapsed into one number."""
    row = client.get("/priority/habitations").json()["habitations"][0]
    assert row["hazard_component"]["value"] != row["vulnerability"]["value"]
    assert "hazard" in row and "exposure" in row and "vulnerability" in row
    assert row["hazard"]["per_hazard"], "the per-hazard vector must survive"


def test_phase_totals_account_for_every_assessed_resident(client: TestClient) -> None:
    payload = client.get("/priority/habitations").json()
    assert sum(t["habitations"] for t in payload["totals_by_phase"].values()) == len(
        payload["habitations"]
    )
    assert sum(t["population"] for t in payload["totals_by_phase"].values()) == payload[
        "total_population_assessed"
    ]


def test_an_override_is_named_wherever_it_fires(client: TestClient) -> None:
    rows = client.get("/priority/habitations").json()["habitations"]
    overridden = [row for row in rows if row["phase"]["rules_applied"]]
    assert overridden, "the demonstration scenario should exercise at least one override"
    for row in overridden:
        assert row["phase"]["phase"] == "IMMEDIATE"
        assert row["zone_class"] == "CRITICAL"
        for rule in row["phase"]["rules_applied"]:
            assert rule.startswith("OVERRIDE ")


def test_unbuilt_constraint_checks_are_declared(client: TestClient) -> None:
    for row in client.get("/priority/habitations").json()["habitations"]:
        assert row["phase"]["pending_checks"], "pending engines must be stated, not implied"


def test_priority_ranking_is_ordered_and_dense(client: TestClient) -> None:
    rows = client.get("/priority/habitations").json()["habitations"]
    assert [row["rank"] for row in rows] == list(range(1, len(rows) + 1))
    scores = [row["priority_score"] for row in rows]
    assert scores == sorted(scores, reverse=True)


def test_habitation_detail_returns_the_full_reasoning(client: TestClient) -> None:
    payload = client.get("/priority/habitations/H-03").json()
    assert payload["row"]["habitation_id"] == "H-03"
    assert payload["priority_formula"]["formula_id"] == "priority.score"
    assert payload["explanation"]["value"] == payload["row"]["priority_score"]
    assert "not a probability" in (payload["explanation"]["notes"] or "")
    assert payload["habitation"]["provenance"] == "SYNTHETIC_CALIBRATED"


def test_unknown_habitation_detail_is_a_404(client: TestClient) -> None:
    assert client.get("/priority/habitations/H-99").status_code == 404


def test_capacity_sites_report_effective_capacity_and_the_binding_service(
    client: TestClient,
) -> None:
    payload = client.get("/capacity/sites").json()
    assert len(payload["sites"]) == 6
    assert payload["suitable_sites"] <= len(payload["sites"])
    assert "ownership" in payload["limitation"]
    for site in payload["sites"]:
        capacities = {s["service"]: s["capacity_persons"] for s in site["services"]}
        assert site["effective_capacity"] == pytest.approx(min(capacities.values()), abs=0.1)
        assert capacities[site["bottleneck"]] == pytest.approx(
            site["effective_capacity"], abs=0.1
        )
        assert site["effective_capacity"] <= site["theoretical_capacity"] + 1e-6


def test_capacity_totals_only_count_sites_that_pass_every_gate(client: TestClient) -> None:
    payload = client.get("/capacity/sites").json()
    expected = sum(
        site["effective_capacity"] for site in payload["sites"] if site["suitable"]
    )
    assert payload["total_effective_capacity"] == pytest.approx(expected, abs=0.2)
    assert payload["unmet_demand"] == pytest.approx(
        max(payload["population_needing_relocation"] - expected, 0.0), abs=0.2
    )


def test_every_gate_failure_names_the_gate_and_its_threshold(client: TestClient) -> None:
    for site in client.get("/capacity/sites").json()["sites"]:
        for gate in site["gates"]:
            assert gate["detail"]
            assert gate["threshold"] is not None
            assert gate["observed"] is not None
        if not site["suitable"]:
            assert site["failed_gates"]


def test_marginal_intervention_is_computed_not_narrated(client: TestClient) -> None:
    for site in client.get("/capacity/sites").json()["sites"]:
        interventions = site["interventions"]
        assert interventions
        gains = [i["capacity_gain"] for i in interventions]
        assert gains == sorted(gains, reverse=True)
        for intervention in interventions:
            assert intervention["capacity_after"] - intervention["capacity_before"] == (
                pytest.approx(intervention["capacity_gain"], abs=0.2)
            )
            assert intervention["capacity_before"] == pytest.approx(
                site["effective_capacity"], abs=0.2
            )
        best = interventions[0]
        if best["unlocks"]:
            assert site["marginal_headline"]
            # The headline rounds; the test must round the same way rather than
            # truncate, or it fails on the engine being correct.
            assert str(round(best["capacity_after"])) in site[
                "marginal_headline"
            ].replace(",", "")


def test_capacity_norms_are_served_with_their_citations(client: TestClient) -> None:
    for norm in client.get("/capacity/sites").json()["norms"]:
        assert norm["description"]
        if norm["provenance"] != "DEMO_CONFIG":
            assert norm["citation"]


def test_access_capacity_is_computed_now_that_the_route_engine_exists(
    client: TestClient,
) -> None:
    """Slice 5 declared access pending on Engine 5. Engine 5 exists, so it is not."""
    for site in client.get("/capacity/sites").json()["sites"]:
        assert not site["pending_constraints"], (
            f"{site['site_id']} still declares a pending constraint"
        )
        access = [s for s in site["services"] if s["service"] == "ACCESS"]
        assert len(access) == 1
        assert access[0]["capacity_persons"] > 0
        assert access[0]["norm_provenance"] == "DEMO_CONFIG"


def test_unknown_site_capacity_is_a_404(client: TestClient) -> None:
    assert client.get("/capacity/sites/S-99").status_code == 404


def test_landcover_refinement_reports_its_own_limits(client: TestClient) -> None:
    refinement = client.get("/study-area/data").json().get("landcover_refinement")
    assert refinement, "the scoped ML component should be built"
    assert refinement["model"] == "landcover-refinement-rf"
    assert "RandomForest" in refinement["algorithm"]
    assert 0.0 <= refinement["buildable_accuracy"] <= 1.0
    assert 0.0 <= refinement["agreement_with_worldcover"] <= 1.0
    assert refinement["labelling_rules"], "the labelling rules must be published"
    for rule in refinement["labelling_rules"]:
        assert rule["reasoning"]
    caveats = " ".join(refinement["caveats"]).lower()
    assert "never from the worldcover product" in caveats
    assert "scores no hazard" in caveats

# ---------------------------------------------------------------------------
# Engine 5 - routes
# ---------------------------------------------------------------------------


def test_routes_report_reliability_for_every_habitation_site_pair(
    client: TestClient,
) -> None:
    payload = client.get("/routes").json()
    assert payload["pairs_evaluated"] == 72
    assert len(payload["rows"]) == 72
    for row in payload["rows"]:
        assert 0.0 <= row["reliability"] <= 1.0
        assert row["travel_time_min"] > 0
        assert row["feasible"] == (
            row["reliability"] >= payload["reliability_threshold"]
        )


def test_routes_name_the_habitations_no_suitable_site_can_be_reached_from(
    client: TestClient,
) -> None:
    """A habitation with nowhere reachable and safe is intelligence, not a gap."""
    payload = client.get("/routes").json()
    blocked = set(payload["route_blocked_habitations"])
    usable = {
        row["habitation_id"]
        for row in payload["rows"]
        if row["feasible"] and row["site_suitable"]
    }
    assert blocked == {row["habitation_id"] for row in payload["rows"]} - usable
    assert payload["habitations_with_a_reachable_suitable_site"] == len(usable)


def test_the_network_reports_its_own_lack_of_redundancy(client: TestClient) -> None:
    network = client.get("/routes").json()["network"]
    assert network["segments"] > 400
    assert 0.0 <= network["share_without_alternative"] <= 1.0
    assert str(network["independent_loops"]) in network["redundancy_note"]
    assert network["unrouted_ways"] == 0


def test_a_route_pair_states_the_trade_between_fastest_and_safest(
    client: TestClient,
) -> None:
    pair = client.get("/routes/pair/H-01/S-03").json()
    assert pair["safest"]["reliability"] >= pair["fastest"]["reliability"] - 1e-9
    assert pair["tradeoff"]
    if not pair["profiles_differ"]:
        assert "no trade to make" in pair["tradeoff"]
    for profile in ("fastest", "safest"):
        route = pair[profile]
        assert route["geometry"], "a route must be drawable"
        assert len(route["legs"]) > 0
        assert route["risk"] == pytest.approx(1.0 - route["reliability"], abs=1e-6)


def test_every_route_leg_carries_the_facts_behind_its_own_risk(
    client: TestClient,
) -> None:
    route = client.get("/routes/pair/H-06/S-01").json()["safest"]
    for leg in route["legs"]:
        assert leg["segment_id"]
        assert leg["length_m"] > 0
        assert 0.0 <= leg["p_fail"] <= 1.0
        assert 0.0 <= leg["hazard_max"] <= 1.0
    product = 1.0
    for leg in route["legs"]:
        product *= 1.0 - leg["p_fail"]
    assert route["reliability"] == pytest.approx(product, abs=1e-3)


def test_an_unknown_route_pair_is_a_404(client: TestClient) -> None:
    assert client.get("/routes/pair/H-99/S-01").status_code == 404


def test_the_network_geojson_carries_what_the_map_needs_to_colour_it(
    client: TestClient,
) -> None:
    payload = client.get("/routes/network.geojson").json()
    assert payload["type"] == "FeatureCollection"
    assert payload["features"]
    for feature in payload["features"][:20]:
        properties = feature["properties"]
        assert properties["segment_id"]
        assert 0.0 <= properties["p_fail"] <= 1.0
        assert isinstance(properties["no_alternative"], bool)
    assert "OpenStreetMap" in payload["properties"]["source"]


def test_closing_a_road_changes_real_routes_and_says_by_how_much(
    client: TestClient,
) -> None:
    row = max(client.get("/routes").json()["rows"], key=lambda r: r["bridges_crossed"])
    pair = client.get(f"/routes/pair/{row['habitation_id']}/{row['site_id']}").json()
    bridges = [leg for leg in pair["safest"]["legs"] if leg["is_bridge"]]
    assert bridges, "the corridor routes cross bridges"
    closed = bridges[0]["segment_id"]

    payload = client.post("/routes/evaluate", json={"closed_segments": [closed]}).json()
    assert payload["closed_segments"] == [closed]
    assert payload["closed_segment_detail"][0]["segment_id"] == closed
    assert payload["changed"], "closing a used bridge must change something"
    for changed in payload["changed"]:
        assert (
            changed["reliability_after"] != changed["reliability_before"]
            or changed["travel_time_after_min"] != changed["travel_time_before_min"]
            or changed["feasible_after"] != changed["feasible_before"]
        )
    assert str(payload["newly_infeasible"]) in payload["headline"]

    after = client.get(f"/routes/pair/{row['habitation_id']}/{row['site_id']}").json()
    assert after["safest"]["reliability"] == pair["safest"]["reliability"], (
        "evaluating a closure must not mutate the baseline assessment"
    )


def test_closing_nothing_changes_nothing(client: TestClient) -> None:
    payload = client.post("/routes/evaluate", json={"closed_segments": []}).json()
    assert payload["changed"] == []
    assert payload["newly_infeasible"] == 0
    assert "change no habitation-site route" in payload["headline"]


def test_closing_an_unknown_segment_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/routes/evaluate", json={"closed_segments": ["not-a-segment"]}
    )
    assert response.status_code == 422
    assert "unknown road segments" in response.json()["detail"]


def test_a_closure_request_cannot_dismantle_the_network(client: TestClient) -> None:
    segments = [
        feature["properties"]["segment_id"]
        for feature in client.get("/routes/network.geojson").json()["features"][:30]
    ]
    response = client.post("/routes/evaluate", json={"closed_segments": segments})
    assert response.status_code == 422


def test_route_constants_are_served_with_their_provenance(client: TestClient) -> None:
    constants = client.get("/routes").json()["constants"]
    keys = {constant["key"] for constant in constants}
    assert "route.p_fail.hazard_coefficient" in keys
    assert "route.min_reliability" in keys
    for constant in constants:
        assert constant["provenance"] == "DEMO_CONFIG"
        assert constant["description"]
