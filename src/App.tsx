import { useEffect, useState, type FormEvent } from "react";
import {
  api,
  type ChatResponse,
  type ComparisonResponse,
  type HealthResponse,
  type Investigation,
  type InvestigationPage,
  type InvestigationSource,
  type MeasurementList,
  type ReportResponse,
  type ScenarioAnalysisResponse,
  type ScenarioRequest,
  type SourceCitation,
} from "./api";
import { AppLayout, readRoute, type AppRoute } from "./components/AppLayout";
import { DashboardView } from "./components/DashboardView";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  type RemoteState,
} from "./components/AsyncState";

type ExplorerTab = "investigations" | "measurements";

const initialScenario: ScenarioRequest = {
  environment: "lunar_habitat",
  oxygen_pct: 30,
  pressure: { value: 10.2, unit: "psi" },
  material_or_fuel: null,
  objective: "general",
};

function App() {
  const [route, setRoute] = useState<AppRoute>(readRoute);
  const [health, setHealth] = useState<RemoteState<HealthResponse>>({
    status: "loading",
  });
  const [dashboardCatalog, setDashboardCatalog] =
    useState<RemoteState<InvestigationPage>>({ status: "loading" });
  const [explorerCatalog, setExplorerCatalog] =
    useState<RemoteState<InvestigationPage>>({ status: "loading" });
  const [measurements, setMeasurements] =
    useState<RemoteState<MeasurementList>>({ status: "loading" });
  const [explorerTab, setExplorerTab] =
    useState<ExplorerTab>("investigations");
  const [selected, setSelected] = useState<Investigation | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [scenario, setScenario] = useState(initialScenario);
  const [analysis, setAnalysis] = useState<ScenarioAnalysisResponse | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [question, setQuestion] = useState("");
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadHealth = async () => {
    setHealth({ status: "loading" });
    try {
      setHealth({ status: "ready", data: await api.health() });
    } catch (reason) {
      setHealth({
        status: "error",
        message:
          reason instanceof Error ? reason.message : "Unable to check API health.",
      });
    }
  };

  const loadCatalog = async (
    term = "",
    updateDashboard = false,
  ): Promise<void> => {
    setExplorerCatalog({ status: "loading" });
    if (updateDashboard) setDashboardCatalog({ status: "loading" });
    const params = new URLSearchParams({ page: "1", page_size: "100" });
    if (term.trim()) params.set("q", term.trim());
    try {
      const data = await api.investigations(params);
      setExplorerCatalog({ status: "ready", data });
      if (updateDashboard) setDashboardCatalog({ status: "ready", data });
    } catch (reason) {
      const message =
        reason instanceof Error
          ? reason.message
          : "Unable to load investigations.";
      setExplorerCatalog({ status: "error", message });
      if (updateDashboard) setDashboardCatalog({ status: "error", message });
    }
  };

  const loadMeasurements = async () => {
    setMeasurements({ status: "loading" });
    try {
      setMeasurements({ status: "ready", data: await api.measurements() });
    } catch (reason) {
      setMeasurements({
        status: "error",
        message:
          reason instanceof Error
            ? reason.message
            : "Unable to load verified measurements.",
      });
    }
  };

  useEffect(() => {
    void loadHealth();
    void loadCatalog("", true);
    void loadMeasurements();
    const updateRoute = () => setRoute(readRoute());
    window.addEventListener("hashchange", updateRoute);
    return () => window.removeEventListener("hashchange", updateRoute);
  }, []);

  const navigate = (nextRoute: AppRoute) => {
    setError("");
    if (window.location.hash !== `#${nextRoute}`) {
      window.location.hash = nextRoute;
    }
    setRoute(nextRoute);
  };

  const run = async <T,>(
    action: () => Promise<T>,
    onSuccess: (value: T) => void,
  ) => {
    setBusy(true);
    setError("");
    try {
      onSuccess(await action());
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "The request could not be completed.",
      );
    } finally {
      setBusy(false);
    }
  };

  const toggleSelected = (id: string) => {
    setSelectedIds((ids) =>
      ids.includes(id)
        ? ids.filter((item) => item !== id)
        : ids.length < 5
          ? [...ids, id]
          : ids,
    );
  };

  const catalogCount =
    dashboardCatalog.status === "ready"
      ? dashboardCatalog.data.total
      : undefined;
  const records =
    explorerCatalog.status === "ready"
      ? explorerCatalog.data.items
      : [];
  const retryDashboardCatalog = () => {
    setQuery("");
    setSearch("");
    void loadCatalog("", true);
  };

  return (
    <AppLayout
      activeRoute={route}
      health={health}
      catalogCount={catalogCount}
      onNavigate={navigate}
    >
      {error && (
        <div role="alert" className="error-banner">
          <span>Request issue</span>
          {error}
          <button onClick={() => setError("")} aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}

      {route === "dashboard" && (
        <DashboardView
          health={health}
          catalog={dashboardCatalog}
          onRetryHealth={() => void loadHealth()}
          onRetryCatalog={retryDashboardCatalog}
          onNavigate={navigate}
        />
      )}

      {route === "explorer" && (
        <ExplorerPage
          tab={explorerTab}
          onTabChange={setExplorerTab}
          catalog={explorerCatalog}
          records={records}
          measurements={measurements}
          selected={selected}
          selectedIds={selectedIds}
          query={query}
          total={
            explorerCatalog.status === "ready"
              ? explorerCatalog.data.total
              : undefined
          }
          onQueryChange={setQuery}
          onSearch={(event) => {
            event.preventDefault();
            setSearch(query);
            void loadCatalog(query);
          }}
          onRetry={() => void loadCatalog(search)}
          onRetryMeasurements={() => void loadMeasurements()}
          onSelect={setSelected}
          onToggleSelected={toggleSelected}
          onNavigate={navigate}
        />
      )}

      {route === "scenario" && (
        <ScenarioPage
          scenario={scenario}
          setScenario={setScenario}
          analysis={analysis}
          busy={busy}
          onAnalyze={() =>
            void run(() => api.analyze(scenario), setAnalysis)
          }
        />
      )}

      {route === "compare" && (
        <ComparePage
          selectedIds={selectedIds}
          comparison={comparison}
          busy={busy}
          onLoad={() =>
            void run(
              () => api.compare({ investigation_ids: selectedIds }),
              setComparison,
            )
          }
          onNavigate={navigate}
        />
      )}

      {route === "assistant" && (
        <AssistantPage
          question={question}
          selectedIds={selectedIds}
          response={chatResponse}
          setQuestion={setQuestion}
          busy={busy}
          onAsk={(event) => {
            event.preventDefault();
            void run(
              () => api.chat({ question, investigation_ids: selectedIds }),
              setChatResponse,
            );
          }}
        />
      )}

      {route === "brief" && (
        <BriefPage
          selectedIds={selectedIds}
          report={report}
          busy={busy}
          onGenerate={() =>
            void run(
              () => api.report({ investigation_ids: selectedIds }),
              setReport,
            )
          }
          onNavigate={navigate}
        />
      )}
    </AppLayout>
  );
}

function ExplorerPage({
  tab,
  onTabChange,
  catalog,
  records,
  measurements,
  selected,
  selectedIds,
  query,
  total,
  onQueryChange,
  onSearch,
  onRetry,
  onRetryMeasurements,
  onSelect,
  onToggleSelected,
  onNavigate,
}: {
  tab: ExplorerTab;
  onTabChange: (tab: ExplorerTab) => void;
  catalog: RemoteState<InvestigationPage>;
  records: Investigation[];
  measurements: RemoteState<MeasurementList>;
  selected: Investigation | null;
  selectedIds: string[];
  query: string;
  total: number | undefined;
  onQueryChange: (query: string) => void;
  onSearch: (event: FormEvent<HTMLFormElement>) => void;
  onRetry: () => void;
  onRetryMeasurements: () => void;
  onSelect: (record: Investigation) => void;
  onToggleSelected: (id: string) => void;
  onNavigate: (route: AppRoute) => void;
}) {
  return (
    <section className="panel records-panel">
      <div className="panel-title">
        <div>
          <h2>Explore the investigation catalog</h2>
          <p>Records and counts are loaded from the connected FLARE AI API.</p>
        </div>
        {total !== undefined && (
          <span className="count-badge">{total} records</span>
        )}
      </div>

      <div className="explorer-tabs" role="tablist" aria-label="Explorer content">
        <button
          id="records-tab"
          role="tab"
          aria-selected={tab === "investigations"}
          aria-controls="records-panel"
          className={tab === "investigations" ? "selected" : ""}
          onClick={() => onTabChange("investigations")}
        >
          Investigations
        </button>
        <button
          id="measurements-tab"
          role="tab"
          aria-selected={tab === "measurements"}
          aria-controls="measurements-panel"
          className={tab === "measurements" ? "selected" : ""}
          onClick={() => onTabChange("measurements")}
        >
          Verified measurements
        </button>
      </div>

      {tab === "investigations" ? (
        <div id="records-panel" role="tabpanel" aria-labelledby="records-tab">
          <form className="search-row" onSubmit={onSearch}>
            <label className="search-box">
              <span aria-hidden="true">⌕</span>
              <input
                aria-label="Search investigations"
                placeholder="Search investigations…"
                value={query}
                onChange={(event) => onQueryChange(event.target.value)}
              />
            </label>
            <button className="button secondary" type="submit">
              Search
            </button>
          </form>

          {catalog.status === "loading" && (
            <LoadingState label="Loading investigations…" />
          )}
          {catalog.status === "error" && (
            <ErrorState message={catalog.message} onRetry={onRetry} />
          )}
          {catalog.status === "ready" &&
            (records.length === 0 ? (
              <EmptyState
                title="No indexed investigations"
                detail="The connected catalog has no matching records. FLARE AI does not add sample or invented NASA data."
              />
            ) : (
              <div className="layout-two explorer-layout">
                <div>
                  <div className="record-list">
                    {records.map((item) => (
                      <article
                        className={`record-card ${selected?.investigation_id === item.investigation_id ? "chosen" : ""}`}
                        key={item.investigation_id}
                      >
                        <button
                          className="record-main"
                          onClick={() => onSelect(item)}
                        >
                          <div className="record-top">
                            <span className="tag">{item.research_area}</span>
                            <span className="record-id">
                              {item.investigation_id}
                            </span>
                          </div>
                          <h3>{item.title}</h3>
                          <div className="record-meta">
                            {item.environment.replace("_", " ")}
                            <span aria-hidden="true">·</span>
                            {item.data_availability.replace("_", " ")}
                          </div>
                        </button>
                        <label className="compare-check">
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(item.investigation_id)}
                            onChange={() =>
                              onToggleSelected(item.investigation_id)
                            }
                            aria-label={`Select ${item.title} for comparison`}
                          />
                        </label>
                      </article>
                    ))}
                  </div>
                  {selectedIds.length > 0 && (
                    <button
                      className="button primary wide"
                      onClick={() => onNavigate("compare")}
                    >
                      Compare selected ({selectedIds.length})
                    </button>
                  )}
                </div>
                <section className="panel detail-panel" aria-live="polite">
                  {selected ? (
                    <RecordDetail item={selected} />
                  ) : (
                    <div className="detail-placeholder">
                      <span className="detail-icon" aria-hidden="true">◉</span>
                      <h3>Select an investigation</h3>
                      <p>
                        Review indexed conditions, measurements, findings and
                        source provenance.
                      </p>
                      <div className="mini-rule" />
                      <small>Only verified source data is displayed.</small>
                    </div>
                  )}
                </section>
              </div>
            ))}
        </div>
      ) : (
        <div
          id="measurements-panel"
          role="tabpanel"
          aria-labelledby="measurements-tab"
        >
          {measurements.status === "loading" && (
            <LoadingState label="Loading verified measurements…" />
          )}
          {measurements.status === "error" && (
            <ErrorState
              message={measurements.message}
              onRetry={onRetryMeasurements}
            />
          )}
          {measurements.status === "ready" &&
            (measurements.data.items.length === 0 ? (
              <EmptyState
                title="No verified measurements indexed"
                detail="Numeric values appear only when their original source, unit and investigation are verified and indexed."
              />
            ) : (
              <MeasurementsTable measurements={measurements.data} />
            ))}
        </div>
      )}
    </section>
  );
}

function ScenarioPage({
  scenario,
  setScenario,
  analysis,
  busy,
  onAnalyze,
}: {
  scenario: ScenarioRequest;
  setScenario: (scenario: ScenarioRequest) => void;
  analysis: ScenarioAnalysisResponse | null;
  busy: boolean;
  onAnalyze: () => void;
}) {
  return (
    <section className="panel form-panel">
      <div className="panel-title">
        <div>
          <h2>Configure a hypothetical mission</h2>
          <p>
            Find research with relevant evidence. Similarity does not establish
            safety.
          </p>
        </div>
        <span className="tag amber">HYPOTHETICAL SCENARIO</span>
      </div>
      <div className="assumption-note">
        <strong>Example assumptions</strong>
        <span>
          30% oxygen and 10.2 psi are user-entered Moon Base demo assumptions—not
          NASA measurements.
        </span>
      </div>
      <div className="form-grid">
        <label>
          Mission environment
          <select
            value={scenario.environment}
            onChange={(event) =>
              setScenario({
                ...scenario,
                environment: event.target.value as ScenarioRequest["environment"],
              })
            }
          >
            <option value="lunar_habitat">Lunar habitat</option>
            <option value="mars_habitat">Mars habitat</option>
            <option value="spacecraft">Spacecraft</option>
            <option value="spacesuit">Spacesuit</option>
            <option value="custom">Custom</option>
          </select>
        </label>
        <label>
          Research objective
          <select
            value={scenario.objective}
            onChange={(event) =>
              setScenario({
                ...scenario,
                objective: event.target.value as ScenarioRequest["objective"],
              })
            }
          >
            <option value="general">General</option>
            <option value="material_flammability">Material flammability</option>
            <option value="fire_detection">Fire detection</option>
            <option value="fire_suppression">Fire suppression</option>
            <option value="combustion_fundamentals">
              Combustion fundamentals
            </option>
          </select>
        </label>
        <label>
          Oxygen (%)
          <input
            type="number"
            min="0"
            max="100"
            step="any"
            value={scenario.oxygen_pct ?? ""}
            onChange={(event) =>
              setScenario({
                ...scenario,
                oxygen_pct:
                  event.target.value === "" ? null : Number(event.target.value),
              })
            }
          />
        </label>
        <label>
          Pressure (psi)
          <input
            type="number"
            min="0"
            step="any"
            value={scenario.pressure.value ?? ""}
            onChange={(event) =>
              setScenario({
                ...scenario,
                pressure: {
                  value:
                    event.target.value === "" ? null : Number(event.target.value),
                  unit: "psi",
                },
              })
            }
          />
        </label>
        <label className="full">
          Material or fuel (optional)
          <input
            placeholder="Enter a material or fuel"
            value={scenario.material_or_fuel ?? ""}
            onChange={(event) =>
              setScenario({
                ...scenario,
                material_or_fuel: event.target.value || null,
              })
            }
          />
        </label>
      </div>
      <button className="button primary" disabled={busy} onClick={onAnalyze}>
        {busy ? "Analyzing…" : "Analyze research relevance"}
        <span aria-hidden="true">→</span>
      </button>
      {analysis && <ScenarioResults analysis={analysis} />}
    </section>
  );
}

function ScenarioResults({
  analysis,
}: {
  analysis: ScenarioAnalysisResponse;
}) {
  return (
    <div className="results-block">
      <div className="result-banner">
        <strong>Research relevance—not fire risk</strong>
        <span>Scores rank indexed research evidence; they are not probabilities.</span>
      </div>
      {analysis.matches.length ? (
        analysis.matches.map((match) => (
          <article className="match-card" key={match.investigation_id}>
            <div className="match-head">
              <div>
                <span className="tag">RESEARCH MATCH</span>
                <h3>{match.title}</h3>
              </div>
              <strong>{match.relevance_score}<small>/100</small></strong>
            </div>
            <p>{match.match_reasons.join(" ")}</p>
            <small>
              Objective (40%) {formatScore(match.score_breakdown.objective_match)} ·
              Parameters (30%) {formatScore(match.score_breakdown.parameter_similarity)} ·
              Measurements (20%) {formatScore(match.score_breakdown.measurement_usefulness)} ·
              Context/hardware (10%) {formatScore(match.score_breakdown.context_hardware)}
            </small>
            <p className="muted small">
              Evidence completeness: {Math.round(match.evidence_completeness * 100)}%
            </p>
            <CitationList citations={match.citations} />
            <NoticeList title="Record limitations" items={match.limitations} />
          </article>
        ))
      ) : (
        <EmptyState
          title="No research matches available"
          detail="There are no investigations in the local catalog to rank."
        />
      )}
      <NoticeList
        title="Research gaps & limitations"
        items={[...analysis.research_gaps, ...analysis.limitations]}
      />
    </div>
  );
}

function formatScore(value: number | null): string {
  return value === null ? "Unavailable" : value.toFixed(2);
}

function ComparePage({
  selectedIds,
  comparison,
  busy,
  onLoad,
  onNavigate,
}: {
  selectedIds: string[];
  comparison: ComparisonResponse | null;
  busy: boolean;
  onLoad: () => void;
  onNavigate: (route: AppRoute) => void;
}) {
  return (
    <section className="panel form-panel">
      <div className="panel-title">
        <div>
          <h2>Compare investigation records</h2>
          <p>Compare indexed fields side by side. Missing data remains missing.</p>
        </div>
      </div>
      {selectedIds.length === 0 ? (
        <EmptyState
          title="Choose records to compare"
          detail="Select up to five records from the Investigation Explorer."
        >
          <button
            className="button secondary"
            onClick={() => onNavigate("explorer")}
          >
            Open Investigation Explorer
          </button>
        </EmptyState>
      ) : (
        <>
          <button className="button primary" disabled={busy} onClick={onLoad}>
            {busy ? "Loading comparison…" : `Compare ${selectedIds.length} selected`}
          </button>
          {comparison && (
            <>
              <div className="comparison-grid">
                {comparison.investigations.map((item) => (
                  <div className="comparison-card" key={item.investigation_id}>
                    <h3>{item.title}</h3>
                    <Info label="Research area" value={item.research_area} />
                    <Info label="Environment" value={item.environment} />
                    <Info
                      label="Materials/fuels"
                      value={item.materials_or_fuels.join(", ")}
                    />
                    <Info
                      label="Measured variables"
                      value={item.variables_measured.join(", ")}
                    />
                    <Info label="Data availability" value={item.data_availability} />
                    <div className="info-row">
                      <span>Sources</span>
                      <CitationList citations={item.sources} />
                    </div>
                  </div>
                ))}
              </div>
              <NoticeList title="Comparison limitations" items={comparison.limitations} />
            </>
          )}
        </>
      )}
    </section>
  );
}

function AssistantPage({
  question,
  selectedIds,
  response,
  setQuestion,
  busy,
  onAsk,
}: {
  question: string;
  selectedIds: string[];
  response: ChatResponse | null;
  setQuestion: (value: string) => void;
  busy: boolean;
  onAsk: (event: React.FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="panel assistant-panel">
      <div className="panel-title">
        <div>
          <h2>Evidence-grounded research assistant</h2>
          <p>Answers must be supported by indexed source excerpts.</p>
        </div>
        <span className="tag">PROVENANCE REQUIRED</span>
      </div>
      <div className="chat-empty">
        <span className="assistant-symbol" aria-hidden="true">✳</span>
        <h3>Ask a research question</h3>
        <p>
          FLARE AI only answers when verified source excerpts are indexed. It
          will identify unavailable evidence rather than inventing an answer.
        </p>
        <p>
          {selectedIds.length
            ? `Using ${selectedIds.length} selected investigation${selectedIds.length === 1 ? "" : "s"} as context.`
            : "No investigations selected; questions use the indexed catalog."}
        </p>
      </div>
      {response && (
        <div className="chat-answer">
          <p>{response.answer}</p>
          <CitationList citations={response.citations} />
          <NoticeList title="Limitations" items={response.limitations} />
        </div>
      )}
      <form className="chat-form" onSubmit={onAsk}>
        <label className="sr-only" htmlFor="research-question">
          Research question
        </label>
        <textarea
          id="research-question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about an indexed investigation, result, or measurement…"
          required
        />
        <button
          className="button primary"
          disabled={busy || !question.trim()}
          type="submit"
        >
          {busy ? "Checking…" : "Ask"} <span aria-hidden="true">↑</span>
        </button>
      </form>
      <div className="footnote">
        Student-built research prototype. Not an official NASA system.
      </div>
    </section>
  );
}

function BriefPage({
  selectedIds,
  report,
  busy,
  onGenerate,
  onNavigate,
}: {
  selectedIds: string[];
  report: ReportResponse | null;
  busy: boolean;
  onGenerate: () => void;
  onNavigate: (route: AppRoute) => void;
}) {
  return (
    <section className="panel form-panel">
      <div className="panel-title">
        <div>
          <h2>Generate a research brief</h2>
          <p>Evidence summary with source references, limitations and research gaps.</p>
        </div>
      </div>
      <p className="muted">
        Selected investigations: {selectedIds.length || "none"}
      </p>
      {selectedIds.length === 0 ? (
        <button
          className="button secondary"
          onClick={() => onNavigate("explorer")}
        >
          Select records in the Investigation Explorer
        </button>
      ) : (
        <button
          className="button primary"
          disabled={busy}
          onClick={onGenerate}
        >
          {busy ? "Generating…" : "Generate brief"}
          <span aria-hidden="true">→</span>
        </button>
      )}
      {report && (
        <div className="report-card">
          <span className="tag">EVIDENCE BRIEF</span>
          <h3>{report.title}</h3>
          <pre>{report.brief}</pre>
          <CitationList citations={report.citations} />
          <NoticeList
            title="Limitations and research gaps"
            items={[...report.limitations, ...report.research_gaps]}
          />
        </div>
      )}
    </section>
  );
}

function RecordDetail({ item }: { item: Investigation }) {
  return (
    <div className="detail-content">
      <p className="eyebrow">INVESTIGATION RECORD</p>
      <h2>{item.title}</h2>
      <div className="detail-tags">
        <span className="tag">{item.research_area}</span>
        <span className="tag quiet">
          {item.data_availability.replace("_", " ")}
        </span>
      </div>
      <p className="record-id">{item.investigation_id}</p>
      <Info label="Environment" value={item.environment} />
      <Info
        label="Materials or fuels"
        value={item.materials_or_fuels.join(", ")}
      />
      <Info
        label="Oxygen"
        value={
          item.conditions.oxygen_pct == null
            ? ""
            : `${item.conditions.oxygen_pct}%`
        }
      />
      <Info
        label="Pressure"
        value={
          item.conditions.pressure.value == null
            ? ""
            : `${item.conditions.pressure.value} ${item.conditions.pressure.unit}`
        }
      />
      <Info label="Hardware" value={item.hardware.join(", ")} />
      <Info label="Sensors" value={item.sensors.join(", ")} />
      <Info
        label="Measured variables"
        value={item.variables_measured.join(", ")}
      />
      <DetailList title="Objectives" items={item.objectives} />
      <DetailList title="Findings" items={item.findings} />
      <div className="detail-section">
        <h3>Sources <span>{item.sources.length}</span></h3>
        <CitationList citations={item.sources} />
      </div>
      {item.environment === "microgravity" && (
        <div className="caution-note">
          Microgravity results do not prove partial-gravity performance.
        </div>
      )}
    </div>
  );
}

function MeasurementsTable({ measurements }: { measurements: MeasurementList }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Investigation</th>
            <th>Variable</th>
            <th>Value</th>
            <th>Unit</th>
            <th>Source ID</th>
          </tr>
        </thead>
        <tbody>
          {measurements.items.map((item) => (
            <tr key={item.measurement_id}>
              <td>{item.investigation_id}</td>
              <td>{item.variable}</td>
              <td>{item.value}</td>
              <td>{item.unit}</td>
              <td>{item.source_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DetailList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="detail-section">
      <h3>{title}</h3>
      {items.length > 0 ? (
        <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
      ) : (
        <p className="muted">Not available in indexed sources.</p>
      )}
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="info-row">
      <span>{label}</span>
      <strong>{value || "Not available in indexed sources"}</strong>
    </div>
  );
}

function CitationList({
  citations,
}: {
  citations: (InvestigationSource | SourceCitation)[];
}) {
  if (!citations.length) {
    return <p className="muted small">No source citations indexed.</p>;
  }
  return (
    <ul className="citation-list">
      {citations.map((citation) => (
        <li key={citation.source_id}>
          <a href={citation.source_url} target="_blank" rel="noreferrer">
            {citation.document_title}
          </a>
          {citation.page_number && <span> · p. {citation.page_number}</span>}
          {citation.section && <span> · {citation.section}</span>}
        </li>
      ))}
    </ul>
  );
}

function NoticeList({ title, items }: { title: string; items: string[] }) {
  return items.length > 0 ? (
    <div className="notice-list">
      <strong>{title}</strong>
      <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
    </div>
  ) : null;
}

export default App;
