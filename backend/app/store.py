import json
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.models import (
    EvidenceExcerpt,
    Investigation,
    Measurement,
    ScenarioAnalysisResponse,
    Source,
)


DEFAULT_DATABASE = Path(__file__).resolve().parents[1] / "flare_ai.sqlite3"
_SEARCH_STOPWORDS = {
    "about",
    "after",
    "again",
    "are",
    "did",
    "does",
    "for",
    "from",
    "how",
    "into",
    "is",
    "its",
    "not",
    "that",
    "the",
    "their",
    "this",
    "was",
    "what",
    "when",
    "where",
    "which",
    "with",
}


@dataclass(frozen=True)
class EvidenceHit:
    excerpt: EvidenceExcerpt
    investigation: Investigation
    source: Source


class SQLiteStore:
    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(
            database_path or os.environ.get("FLARE_DATABASE_PATH", DEFAULT_DATABASE)
        )
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS investigations "
                "(investigation_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS measurements "
                "(measurement_id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL, "
                "variable TEXT NOT NULL, payload TEXT NOT NULL, "
                "FOREIGN KEY(investigation_id) REFERENCES investigations(investigation_id))"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS evidence_excerpts "
                "(excerpt_id TEXT PRIMARY KEY, investigation_id TEXT NOT NULL, "
                "source_id TEXT NOT NULL, payload TEXT NOT NULL, "
                "FOREIGN KEY(investigation_id) REFERENCES investigations(investigation_id))"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS evidence_investigation_source "
                "ON evidence_excerpts(investigation_id, source_id)"
            )
            connection.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS evidence_search USING fts5("
                "excerpt_id UNINDEXED, investigation_id UNINDEXED, "
                "source_id UNINDEXED, excerpt, tokenize='unicode61')"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS evidence_excerpts_insert "
                "AFTER INSERT ON evidence_excerpts BEGIN "
                "INSERT INTO evidence_search"
                "(excerpt_id, investigation_id, source_id, excerpt) VALUES "
                "(new.excerpt_id, new.investigation_id, new.source_id, "
                "json_extract(new.payload, '$.excerpt')); END"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS evidence_excerpts_update "
                "AFTER UPDATE ON evidence_excerpts BEGIN "
                "DELETE FROM evidence_search WHERE excerpt_id = old.excerpt_id; "
                "INSERT INTO evidence_search"
                "(excerpt_id, investigation_id, source_id, excerpt) VALUES "
                "(new.excerpt_id, new.investigation_id, new.source_id, "
                "json_extract(new.payload, '$.excerpt')); END"
            )
            connection.execute(
                "CREATE TRIGGER IF NOT EXISTS evidence_excerpts_delete "
                "AFTER DELETE ON evidence_excerpts BEGIN "
                "DELETE FROM evidence_search WHERE excerpt_id = old.excerpt_id; END"
            )
            connection.execute(
                "INSERT INTO evidence_search"
                "(excerpt_id, investigation_id, source_id, excerpt) "
                "SELECT excerpt_id, investigation_id, source_id, "
                "json_extract(payload, '$.excerpt') FROM evidence_excerpts "
                "WHERE NOT EXISTS (SELECT 1 FROM evidence_search "
                "WHERE evidence_search.excerpt_id = evidence_excerpts.excerpt_id)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS scenario_analyses "
                "(scenario_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def list_investigations(
        self,
        q: str | None = None,
        research_area: str | None = None,
        environment: str | None = None,
        data_availability: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Investigation], int]:
        clauses: list[str] = []
        parameters: list[object] = []
        for field, value in (
            ("research_area", research_area),
            ("environment", environment),
            ("data_availability", data_availability),
        ):
            if value:
                clauses.append(f"json_extract(payload, '$.{field}') = ?")
                parameters.append(value)
        if q:
            clauses.append(
                "(lower(json_extract(payload, '$.title')) LIKE ? OR "
                "lower(json_extract(payload, '$.acronym')) LIKE ? OR "
                "lower(payload) LIKE ?)"
            )
            term = f"%{q.lower()}%"
            parameters.extend([term, term, term])
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) FROM investigations{where}", parameters
            ).fetchone()[0]
            rows = connection.execute(
                f"SELECT payload FROM investigations{where} "
                "ORDER BY json_extract(payload, '$.title') "
                "LIMIT ? OFFSET ?",
                [*parameters, page_size, (page - 1) * page_size],
            ).fetchall()
        return [Investigation.model_validate_json(row["payload"]) for row in rows], total

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM investigations WHERE investigation_id = ?",
                (investigation_id,),
            ).fetchone()
        return Investigation.model_validate_json(row["payload"]) if row else None

    def get_investigations(self, investigation_ids: list[str]) -> list[Investigation]:
        if not investigation_ids:
            return []
        placeholders = ",".join("?" for _ in investigation_ids)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload FROM investigations "
                f"WHERE investigation_id IN ({placeholders})",
                investigation_ids,
            ).fetchall()
        by_id = {
            investigation.investigation_id: investigation
            for investigation in (
                Investigation.model_validate_json(row["payload"]) for row in rows
            )
        }
        return [by_id[item_id] for item_id in investigation_ids if item_id in by_id]

    def measurements(
        self, investigation_id: str | None = None, variable: str | None = None
    ) -> list[Measurement]:
        clauses: list[str] = []
        parameters: list[str] = []
        if investigation_id:
            clauses.append("investigation_id = ?")
            parameters.append(investigation_id)
        if variable:
            clauses.append("lower(variable) = lower(?)")
            parameters.append(variable)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload FROM measurements{where} ORDER BY variable",
                parameters,
            ).fetchall()
        return [Measurement.model_validate_json(row["payload"]) for row in rows]

    def measurements_for_investigations(
        self, investigation_ids: list[str]
    ) -> list[Measurement]:
        if not investigation_ids:
            return []
        placeholders = ",".join("?" for _ in investigation_ids)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload FROM measurements "
                f"WHERE investigation_id IN ({placeholders})",
                investigation_ids,
            ).fetchall()
        return [Measurement.model_validate_json(row["payload"]) for row in rows]

    def search_evidence(
        self,
        query: str,
        investigation_ids: list[str] | None = None,
        limit: int = 8,
    ) -> list[EvidenceHit]:
        terms = [
            term
            for term in dict.fromkeys(re.findall(r"[a-z0-9]{2,}", query.casefold()))
            if term not in _SEARCH_STOPWORDS
        ][:12]
        if not terms or investigation_ids == []:
            return []
        match_query = " OR ".join(f'"{term}"' for term in terms)
        clauses = ["evidence_search MATCH ?"]
        parameters: list[object] = [match_query]
        if investigation_ids is not None:
            placeholders = ",".join("?" for _ in investigation_ids)
            clauses.append(f"evidence_excerpts.investigation_id IN ({placeholders})")
            parameters.extend(investigation_ids)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT evidence_excerpts.payload FROM evidence_search "
                "JOIN evidence_excerpts USING (excerpt_id) WHERE "
                + " AND ".join(clauses)
                + " ORDER BY bm25(evidence_search) LIMIT ?",
                [*parameters, limit],
            ).fetchall()
        excerpts = [
            EvidenceExcerpt.model_validate_json(row["payload"]) for row in rows
        ]
        investigations = self.get_investigations(
            list(dict.fromkeys(item.investigation_id for item in excerpts))
        )
        by_id = {item.investigation_id: item for item in investigations}
        hits: list[EvidenceHit] = []
        for excerpt in excerpts:
            investigation = by_id.get(excerpt.investigation_id)
            if investigation is None:
                continue
            source = next(
                (
                    source
                    for source in investigation.sources
                    if source.source_id == excerpt.source_id
                ),
                None,
            )
            if source is None:
                continue
            hits.append(EvidenceHit(excerpt, investigation, source))
        return hits

    def save_scenario_analysis(self, analysis: ScenarioAnalysisResponse) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO scenario_analyses(scenario_id, payload) VALUES (?, ?) "
                "ON CONFLICT(scenario_id) DO UPDATE SET payload = excluded.payload",
                (analysis.scenario_id, analysis.model_dump_json()),
            )

    def get_scenario_analysis(
        self, scenario_id: str
    ) -> ScenarioAnalysisResponse | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM scenario_analyses WHERE scenario_id = ?",
                (scenario_id,),
            ).fetchone()
        return ScenarioAnalysisResponse.model_validate_json(row["payload"]) if row else None

    def import_records(
        self,
        investigations: list[Investigation],
        measurements: list[Measurement],
        replace: bool = False,
        evidence_excerpts: list[EvidenceExcerpt] | None = None,
    ) -> None:
        evidence_excerpts = evidence_excerpts or []
        investigation_ids = {item.investigation_id for item in investigations}
        if len(investigation_ids) != len(investigations):
            raise ValueError("Investigation IDs in the import must be unique.")
        if any(not item.sources for item in investigations):
            raise ValueError("Every imported investigation must include at least one source.")
        measurement_ids = {item.measurement_id for item in measurements}
        if len(measurement_ids) != len(measurements):
            raise ValueError("Measurement IDs in the import must be unique.")
        excerpt_ids = {item.excerpt_id for item in evidence_excerpts}
        if len(excerpt_ids) != len(evidence_excerpts):
            raise ValueError("Evidence excerpt IDs in the import must be unique.")
        known_ids = investigation_ids
        if not replace:
            existing, _ = self.list_investigations(page_size=1_000_000)
            known_ids.update(item.investigation_id for item in existing)
        sources = {
            (item.investigation_id, source.source_id)
            for item in investigations
            for source in item.sources
        }
        if not replace:
            sources.update(
                (item.investigation_id, source.source_id)
                for item in existing
                for source in item.sources
            )
        if any(item.investigation_id not in known_ids for item in measurements):
            raise ValueError("Every measurement must reference an imported investigation.")
        if any(
            (item.investigation_id, item.source_id) not in sources
            for item in measurements
        ):
            raise ValueError("Every measurement must cite a source for its investigation.")
        if any(item.investigation_id not in known_ids for item in evidence_excerpts):
            raise ValueError("Every evidence excerpt must reference an indexed investigation.")
        if any(
            (item.investigation_id, item.source_id) not in sources
            for item in evidence_excerpts
        ):
            raise ValueError("Every evidence excerpt must cite a source for its investigation.")

        with self._connect() as connection:
            if replace:
                connection.execute("DELETE FROM scenario_analyses")
                connection.execute("DELETE FROM evidence_excerpts")
                connection.execute("DELETE FROM measurements")
                connection.execute("DELETE FROM investigations")
            connection.executemany(
                "INSERT INTO investigations(investigation_id, payload) VALUES (?, ?) "
                "ON CONFLICT(investigation_id) DO UPDATE SET payload = excluded.payload",
                [
                    (item.investigation_id, item.model_dump_json())
                    for item in investigations
                ],
            )
            connection.executemany(
                "INSERT INTO measurements"
                "(measurement_id, investigation_id, variable, payload) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(measurement_id) DO UPDATE SET "
                "investigation_id = excluded.investigation_id, "
                "variable = excluded.variable, payload = excluded.payload",
                [
                    (
                        item.measurement_id,
                        item.investigation_id,
                        item.variable,
                        item.model_dump_json(),
                    )
                    for item in measurements
                ],
            )
            connection.executemany(
                "INSERT INTO evidence_excerpts"
                "(excerpt_id, investigation_id, source_id, payload) "
                "VALUES (?, ?, ?, ?) ON CONFLICT(excerpt_id) DO UPDATE SET "
                "investigation_id = excluded.investigation_id, "
                "source_id = excluded.source_id, payload = excluded.payload",
                [
                    (
                        item.excerpt_id,
                        item.investigation_id,
                        item.source_id,
                        item.model_dump_json(),
                    )
                    for item in evidence_excerpts
                ],
            )


def load_import_file(
    path: str | Path,
) -> tuple[list[Investigation], list[Measurement], list[EvidenceExcerpt]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) - {
        "investigations",
        "measurements",
        "evidence_excerpts",
    }:
        raise ValueError(
            "Import file must contain only investigations, measurements, and evidence_excerpts."
        )
    if any(
        not isinstance(data.get(field, []), list)
        for field in ("investigations", "measurements", "evidence_excerpts")
    ):
        raise ValueError("Import fields must be JSON arrays.")
    investigations = [
        Investigation.model_validate(item) for item in data.get("investigations", [])
    ]
    measurements = [
        Measurement.model_validate(item) for item in data.get("measurements", [])
    ]
    evidence_excerpts = [
        EvidenceExcerpt.model_validate(item)
        for item in data.get("evidence_excerpts", [])
    ]
    return investigations, measurements, evidence_excerpts
