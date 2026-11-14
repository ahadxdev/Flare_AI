import pytest
from fastapi.testclient import TestClient

from app.models import (
    InvestigationConditions,
    Measurement,
    Pressure,
    ScenarioRequest,
)
from app.main import create_app
from app.services import (
    DEFAULT_RELEVANCE_WEIGHTS,
    RelevanceWeights,
    SQLiteResearchService,
    _score_investigation,
)
from app.store import SQLiteStore


def scenario(**updates) -> ScenarioRequest:
    values = {
        "environment": "spacecraft",
        "oxygen_pct": 30,
        "pressure": {"value": 10.2, "unit": "psi"},
        "material_or_fuel": "test cellulose",
        "objective": "combustion_fundamentals",
    }
    values.update(updates)
    return ScenarioRequest.model_validate(values)


def verified_observation(investigation) -> Measurement:
    source = investigation.sources[0]
    return Measurement(
        measurement_id="test-only-observation",
        investigation_id=investigation.investigation_id,
        variable="test burn time",
        value=1.2,
        unit="s",
        source_id=source.source_id,
    )


def test_default_weights_are_configurable_and_validated() -> None:
    assert DEFAULT_RELEVANCE_WEIGHTS == RelevanceWeights(
        objective_match=0.40,
        parameter_similarity=0.30,
        measurement_usefulness=0.20,
        context_hardware=0.10,
    )
    with pytest.raises(ValueError, match="sum to 1"):
        RelevanceWeights(0.5, 0.3, 0.2, 0.2)
    with pytest.raises(ValueError, match="finite and non-negative"):
        RelevanceWeights(-0.1, 0.5, 0.4, 0.2)
    with pytest.raises(ValueError, match="finite and non-negative"):
        RelevanceWeights(float("nan"), 0.3, 0.2, 0.5)
    with pytest.raises(ValueError, match="finite and non-negative"):
        RelevanceWeights(float("inf"), 0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="finite and non-negative"):
        RelevanceWeights(True, 0.0, 0.0, 0.0)


def test_service_accepts_custom_weights(tmp_path, test_investigation) -> None:
    store = SQLiteStore(tmp_path / "custom-weights.sqlite3")
    mismatched_objective = test_investigation.model_copy(
        update={"research_area": "prevention"}
    )
    store.import_records([mismatched_objective], [])
    store.import_records(
        [], [verified_observation(mismatched_objective)]
    )
    service = SQLiteResearchService(
        store,
        RelevanceWeights(
            objective_match=0.1,
            parameter_similarity=0.3,
            measurement_usefulness=0.2,
            context_hardware=0.4,
        ),
    )

    result = service.analyze_scenario(scenario()).matches[0]

    assert result.relevance_score == 90


def test_objective_match_and_all_evidence_score_full_relevance(
    test_investigation,
) -> None:
    result = _score_investigation(
        scenario(),
        test_investigation,
        verified_measurements=[verified_observation(test_investigation)],
    )

    assert result.relevance_score == 100
    assert result.evidence_completeness == 1
    assert result.score_breakdown.objective_match == 1
    assert "Research area matches the requested objective." in result.match_reasons
    assert result.citations[0].source_id == "test-only-source"


def test_mismatched_objective_uses_configured_weight(test_investigation) -> None:
    record = test_investigation.model_copy(update={"research_area": "prevention"})

    result = _score_investigation(
        scenario(), record, verified_measurements=[verified_observation(record)]
    )

    assert result.score_breakdown.objective_match == 0
    assert result.relevance_score == 60
    assert "Research area does not align with the requested objective." in result.match_reasons


def test_mismatched_parameters_lower_parameter_similarity(test_investigation) -> None:
    result = _score_investigation(
        scenario(oxygen_pct=60, pressure={"value": 5.1, "unit": "psi"}),
        test_investigation,
        verified_measurements=[verified_observation(test_investigation)],
    )

    assert result.score_breakdown.parameter_similarity == 0.6
    assert result.relevance_score == 88


def test_missing_oxygen_and_pressure_are_reported_not_called_mismatches(
    test_investigation,
) -> None:
    record = test_investigation.model_copy(
        update={"conditions": InvestigationConditions()}
    )

    result = _score_investigation(
        scenario(), record, verified_measurements=[verified_observation(record)]
    )

    assert result.score_breakdown.parameter_similarity is None
    assert any("Oxygen percentage is not reported" in item for item in result.limitations)
    assert any("Pressure is not reported" in item for item in result.limitations)
    assert any("Parameter similarity is unavailable" in item for item in result.match_reasons)
    assert result.evidence_completeness == 0.7
    assert result.relevance_score == 100


@pytest.mark.parametrize(
    ("conditions", "missing_field"),
    [
        (InvestigationConditions(oxygen_pct=30), "Pressure is not reported"),
        (
            InvestigationConditions(
                pressure=Pressure(value=10.2, unit="psi")
            ),
            "Oxygen percentage is not reported",
        ),
    ],
)
def test_one_missing_parameter_does_not_invalidate_comparable_parameter(
    test_investigation, conditions, missing_field
) -> None:
    record = test_investigation.model_copy(update={"conditions": conditions})

    result = _score_investigation(
        scenario(), record, verified_measurements=[verified_observation(record)]
    )

    assert result.score_breakdown.parameter_similarity == 1
    assert result.relevance_score == 100
    assert result.evidence_completeness == 0.85
    assert any(missing_field in item for item in result.limitations)


def test_missing_material_information_is_unavailable_not_a_mismatch(
    test_investigation,
) -> None:
    record = test_investigation.model_copy(update={"materials_or_fuels": []})

    result = _score_investigation(
        scenario(),
        record,
        verified_measurements=[verified_observation(record)],
    )

    assert result.score_breakdown.context_hardware is None
    assert result.evidence_completeness == 0.9
    assert result.relevance_score == 100
    assert any("Materials or fuels are not reported" in item for item in result.limitations)


def test_declared_numeric_dataset_without_observations_is_not_awarded_usefulness(
    test_investigation,
) -> None:
    result = _score_investigation(scenario(), test_investigation)

    assert result.score_breakdown.measurement_usefulness is None
    assert result.evidence_completeness == 0.8
    assert any(
        "numeric dataset is declared, but no source-linked measurement observations"
        in item
        for item in result.limitations
    )


def test_actual_source_linked_observations_are_used_for_measurement_component(
    tmp_path, test_investigation
) -> None:
    store = SQLiteStore(tmp_path / "verified-observations.sqlite3")
    store.import_records(
        [test_investigation], [verified_observation(test_investigation)]
    )
    result = SQLiteResearchService(store).analyze_scenario(scenario()).matches[0]

    assert result.score_breakdown.measurement_usefulness == 1
    assert result.evidence_completeness == 1
    assert any(
        "Source-linked numeric measurement observations are indexed"
        in item
        for item in result.match_reasons
    )


def test_all_components_unavailable_returns_zero_with_zero_completeness(
    test_investigation,
) -> None:
    record = test_investigation.model_copy(
        update={
            "conditions": InvestigationConditions(),
            "materials_or_fuels": [],
            "data_availability": "metadata_only",
        }
    )
    result = _score_investigation(
        scenario(
            objective="general",
            oxygen_pct=None,
            pressure={"value": None, "unit": None},
            material_or_fuel=None,
        ),
        record,
    )

    assert result.score_breakdown.model_dump() == {
        "objective_match": None,
        "parameter_similarity": None,
        "measurement_usefulness": None,
        "context_hardware": None,
    }
    assert result.evidence_completeness == 0
    assert result.relevance_score == 0


@pytest.mark.parametrize(
    ("oxygen_pct", "pressure"),
    [
        (0, {"value": 0.01, "unit": "psi"}),
        (100, {"value": 100000, "unit": "psi"}),
        (None, {"value": None, "unit": None}),
    ],
)
def test_relevance_scores_stay_between_zero_and_one_hundred(
    test_investigation, oxygen_pct, pressure
) -> None:
    result = _score_investigation(
        scenario(oxygen_pct=oxygen_pct, pressure=pressure),
        test_investigation,
        verified_measurements=[verified_observation(test_investigation)],
    )

    assert 0 <= result.relevance_score <= 100


def test_scenario_with_no_candidates_returns_empty_matches(client) -> None:
    response = client.post(
        "/api/scenarios/analyze",
        json={
            "environment": "spacecraft",
            "objective": "combustion_fundamentals",
        },
    )

    assert response.status_code == 200
    assert response.json()["matches"] == []
    assert "No investigations are available in indexed sources." in response.json()[
        "research_gaps"
    ]


def test_equal_scores_are_ordered_by_stable_investigation_id(
    seeded_app, test_investigation
) -> None:
    second = test_investigation.model_copy(
        update={"investigation_id": "test-only-alpha"}
    )
    seeded_app.state.research_service.store.import_records([second], [])

    with TestClient(seeded_app) as test_client:
        response = test_client.post(
            "/api/scenarios/analyze",
            json={
                "environment": "spacecraft",
                "oxygen_pct": 30,
                "pressure": {"value": 10.2, "unit": "psi"},
                "material_or_fuel": "test cellulose",
                "objective": "combustion_fundamentals",
            },
        )

    assert response.status_code == 200
    assert [
        match["investigation_id"] for match in response.json()["matches"]
    ] == ["test-only-alpha", "test-only-combustion"]


def test_pressure_with_unconvertible_units_is_not_compared(test_investigation) -> None:
    result = _score_investigation(
        scenario(oxygen_pct=None, pressure={"value": 760, "unit": "mmHg"}),
        test_investigation,
        verified_measurements=[verified_observation(test_investigation)],
    )

    assert result.score_breakdown.parameter_similarity is None
    assert any("Pressure units are not comparable" in item for item in result.limitations)
    assert any("Parameter similarity is unavailable" in item for item in result.match_reasons)
