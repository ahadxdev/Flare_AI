import { useEffect, useState, type FormEvent } from "react";
import {
  api,
  APIRequestError,
  type ChatResponse,
  type ComparisonFieldName,
  type ComparisonResponse,
  type FieldComparison,
  type DataAvailability,
  type HealthResponse,
  type Investigation,
  type InvestigationConditions,
  type InvestigationPage,
  type InvestigationQuery,
  type InvestigationSource,
  type InvestigationEnvironment,
  type Measurement,
  type MeasurementList,
  type ResearchArea,
  type ReportResponse,
  type ScenarioAnalysisResponse,
  type ScenarioRequest,
  type SourceCitation,
} from "./api";
import {
  AppLayout,
  readInvestigationId,
  readRoute,
  type AppRoute,
} from "./components/AppLayout";
import { DashboardView } from "./components/DashboardView";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  type RemoteState,
} from "./components/AsyncState";

type ExplorerTab = "investigations" | "measurements";
type InvestigationDetailState =
  | RemoteState<Investigation>
  | { status: "not_found" };

interface ExplorerFilters {
  research_area: ResearchArea | "";
  environment: InvestigationEnvironment | "";
  data_availability: DataAvailability | "";
}

const emptyFilters: ExplorerFilters = {
  research_area: "",
  environment: "",
  data_availability: "",
};

const EXPLORER_PAGE_SIZE = 20;

const initialScenario: ScenarioRequest = {
  environment: "lunar_habitat",
  oxygen_pct: 30,
  pressure: { value: 10.2, unit: "psi" },
  material_or_fuel: null,
  objective: "general",
};

function App() {
  const [route, setRoute] = useState<AppRoute>(readRoute);
  const [investigationId, setInvestigationId] =
    useState<string | null>(readInvestigationId);
  const [detailState, setDetailState] =
    useState<InvestigationDetailState>({ status: "loading" });
  const [detailRetry, setDetailRetry] = useState(0);
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
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<ExplorerFilters>(emptyFilters);
  const [page, setPage] = useState(1);
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
    query: InvestigationQuery,
    updateDashboard = false,
  ): Promise<void> => {
    setExplorerCatalog({ status: "loading" });
    if (updateDashboard) setDashboardCatalog({ status: "loading" });
    try {
      const data = await api.investigations(query);
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
    void loadCatalog({ page: 1, page_size: EXPLORER_PAGE_SIZE }, true);
    void loadMeasurements();
    const updateRoute = () => {
      setRoute(readRoute());
      setInvestigationId(readInvestigationId());
    };
    window.addEventListener("hashchange", updateRoute);
    return () => window.removeEventListener("hashchange", updateRoute);
  }, []);

  useEffect(() => {
    if (route !== "investigation-detail") return;
    let active = true;
    if (!investigationId) {
      setDetailState({ status: "not_found" });
      return;
    }

    setDetailState({ status: "loading" });
    void api
      .investigation(investigationId)
      .then((data) => {
        if (active) setDetailState({ status: "ready", data });
      })
      .catch((reason: unknown) => {
        if (!active) return;
        if (
          reason instanceof APIRequestError &&
          (reason.status === 404 || reason.code === "NOT_FOUND")
        ) {
          setDetailState({ status: "not_found" });
          return;
        }
        const message =
          reason instanceof APIRequestError && reason.status >= 500
            ? `Server error: ${reason.message}`
            : reason instanceof Error
              ? reason.message
              : "Unable to load this investigation.";
        setDetailState({ status: "error", message });
      });

    return () => {
      active = false;
    };
  }, [route, investigationId, detailRetry]);

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
    setFilters(emptyFilters);
    setPage(1);
    void loadCatalog({ page: 1, page_size: EXPLORER_PAGE_SIZE }, true);
  };
  const explorerQuery = (
    targetPage: number,
    term = search,
    activeFilters = filters,
  ): InvestigationQuery => ({
    q: term || undefined,
    research_area: activeFilters.research_area || undefined,
    environment: activeFilters.environment || undefined,
    data_availability: activeFilters.data_availability || undefined,
    page: targetPage,
    page_size: EXPLORER_PAGE_SIZE,
  });
  const applyExplorerQuery = (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();
    const nextSearch = query.trim();
    setSearch(nextSearch);
    setPage(1);
    void loadCatalog(explorerQuery(1, nextSearch));
  };
  const requestExplorerPage = (nextPage: number) => {
    setPage(nextPage);
    void loadCatalog(explorerQuery(nextPage));
  };
  const retryExplorer = () => {
    void loadCatalog(explorerQuery(page));
  };
  const navigateToInvestigation = (id: string) => {
    const hash = `#investigation/${encodeURIComponent(id)}`;
    if (window.location.hash !== hash) window.location.hash = hash;
    setRoute("investigation-detail");
    setInvestigationId(id);
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
          selectedIds={selectedIds}
          query={query}
          filters={filters}
          page={page}
          total={
            explorerCatalog.status === "ready"
              ? explorerCatalog.data.total
              : undefined
          }
          onQueryChange={setQuery}
          onFiltersChange={setFilters}
          onSearch={applyExplorerQuery}
          onPageChange={requestExplorerPage}
          onRetry={retryExplorer}
          onRetryMeasurements={() => void loadMeasurements()}
          onToggleSelected={toggleSelected}
          onNavigate={navigate}
          onOpenInvestigation={navigateToInvestigation}
        />
      )}

      {route === "investigation-detail" && (
        <InvestigationDetailPage
          state={detailState}
          selected={detailState.status === "ready" && selectedIds.includes(detailState.data.investigation_id)}
          canSelect={selectedIds.length < 5}
          onRetry={() => setDetailRetry((attempt) => attempt + 1)}
          onBack={() => navigate("explorer")}
          onToggleComparison={(id) => toggleSelected(id)}
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
              () =>
                api.chat({
                  question,
                  scenario_id: analysis?.scenario_id ?? null,
                  investigation_ids: selectedIds,
                }),
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
  selectedIds,
  query,
  filters,
  page,
  total,
  onQueryChange,
  onFiltersChange,
  onSearch,
  onPageChange,
  onRetry,
  onRetryMeasurements,
  onToggleSelected,
  onNavigate,
  onOpenInvestigation,
}: {
  tab: ExplorerTab;
  onTabChange: (tab: ExplorerTab) => void;
  catalog: RemoteState<InvestigationPage>;
  records: Investigation[];
  measurements: RemoteState<MeasurementList>;
  selectedIds: string[];
  query: string;
  filters: ExplorerFilters;
  page: number;
  total: number | undefined;
  onQueryChange: (query: string) => void;
  onFiltersChange: (filters: ExplorerFilters) => void;
  onSearch: (event: FormEvent<HTMLFormElement>) => void;
  onPageChange: (page: number) => void;
  onRetry: () => void;
  onRetryMeasurements: () => void;
  onToggleSelected: (id: string) => void;
  onNavigate: (route: AppRoute) => void;
  onOpenInvestigation: (id: string) => void;
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
          <form className="explorer-filters" onSubmit={onSearch}>
            <label className="search-box">
              <span aria-hidden="true">⌕</span>
              <input
                aria-label="Search investigations"
                placeholder="Search investigations…"
                value={query}
                onChange={(event) => onQueryChange(event.target.value)}
              />
            </label>
            <label>
              Research area
              <select
                value={filters.research_area}
                onChange={(event) =>
                  onFiltersChange({
                    ...filters,
                    research_area: event.target.value as ExplorerFilters["research_area"],
                  })
                }
              >
                <option value="">All research areas</option>
                <option value="prevention">Prevention</option>
                <option value="detection">Detection</option>
                <option value="suppression">Suppression</option>
                <option value="fundamentals">Fundamentals</option>
                <option value="related">Related</option>
                <option value="other">Other</option>
              </select>
            </label>
            <label>
              Environment
              <select
                value={filters.environment}
                onChange={(event) =>
                  onFiltersChange({
                    ...filters,
                    environment: event.target.value as ExplorerFilters["environment"],
                  })
                }
              >
                <option value="">All environments</option>
                <option value="microgravity">Microgravity</option>
                <option value="normal_gravity">Normal gravity</option>
                <option value="other">Other</option>
                <option value="unknown">Unknown</option>
              </select>
            </label>
            <label>
              Data availability
              <select
                value={filters.data_availability}
                onChange={(event) =>
                  onFiltersChange({
                    ...filters,
                    data_availability: event.target.value as ExplorerFilters["data_availability"],
                  })
                }
              >
                <option value="">All availability</option>
                <option value="metadata_only">Metadata only</option>
                <option value="documents">Documents</option>
                <option value="numeric_dataset">Numeric dataset</option>
                <option value="unknown">Unknown</option>
              </select>
            </label>
            <button className="button secondary" type="submit">
              Apply filters
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
              <>
                <div className="record-list">
                  {records.map((item) => (
                    <article
                      className="record-card"
                      key={item.investigation_id}
                    >
                      <button
                        className="record-main"
                        aria-label={`View investigation ${item.title} (${item.investigation_id})`}
                        onClick={() =>
                          onOpenInvestigation(item.investigation_id)
                        }
                      >
                        <div className="record-top">
                          <span className="tag">{item.research_area}</span>
                          {item.acronym && (
                            <span className="tag quiet">{item.acronym}</span>
                          )}
                          <span className="record-id">
                            {item.investigation_id}
                          </span>
                        </div>
                        <h3>{item.title}</h3>
                        <div className="record-meta">
                          <span>Environment: {displayEnum(item.environment)}</span>
                          <span aria-hidden="true">·</span>
                          <span>
                            Data availability: {displayEnum(item.data_availability)}
                          </span>
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
                {total !== undefined && (
                  <nav className="pagination" aria-label="Investigation pages">
                    <button
                      className="button secondary"
                      disabled={page <= 1}
                      onClick={() => onPageChange(page - 1)}
                    >
                      Previous
                    </button>
                    <span>
                      Page {page} of {Math.max(1, Math.ceil(total / EXPLORER_PAGE_SIZE))}
                    </span>
                    <button
                      className="button secondary"
                      disabled={page >= Math.ceil(total / EXPLORER_PAGE_SIZE)}
                      onClick={() => onPageChange(page + 1)}
                    >
                      Next
                    </button>
                  </nav>
                )}
                {selectedIds.length > 0 && (
                  <button
                    className="button primary wide"
                    onClick={() => onNavigate("compare")}
                  >
                    Compare selected ({selectedIds.length})
                  </button>
                )}
              </>
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
            (measurements.data.data.length === 0 ? (
              <EmptyState
                title={`No verified measurements indexed (${displayEnum(measurements.data.data_availability)})`}
                detail={measurements.data.message}
              />
            ) : (
              <MeasurementsView measurements={measurements.data} />
            ))}
        </div>
      )}
    </section>
  );
}

function InvestigationDetailPage({
  state,
  selected,
  canSelect,
  onRetry,
  onBack,
  onToggleComparison,
}: {
  state: InvestigationDetailState;
  selected: boolean;
  canSelect: boolean;
  onRetry: () => void;
  onBack: () => void;
  onToggleComparison: (id: string) => void;
}) {
  return (
    <section className="panel detail-page">
      <button className="button secondary detail-back" onClick={onBack}>
        Back to Investigation Explorer
      </button>
      {state.status === "loading" && (
        <LoadingState label="Loading investigation details…" />
      )}
      {state.status === "not_found" && (
        <EmptyState
          title="Investigation not found"
          detail="This investigation ID is not available in the indexed catalog."
        >
          <button className="button secondary" onClick={onBack}>
            Return to Investigation Explorer
          </button>
        </EmptyState>
      )}
      {state.status === "error" && (
        <ErrorState message={state.message} onRetry={onRetry} />
      )}
      {state.status === "ready" && (
        <RecordDetail
          item={state.data}
          selected={selected}
          canSelect={canSelect}
          onToggleComparison={onToggleComparison}
        />
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
          detail="Select at least two records by investigation ID in the Investigation Explorer."
        >
          <button
            className="button secondary"
            onClick={() => onNavigate("explorer")}
          >
            Open Investigation Explorer
          </button>
        </EmptyState>
      ) : selectedIds.length < 2 ? (
        <EmptyState
          title="Select one more investigation"
          detail="A field-by-field comparison requires at least two distinct investigation IDs."
        >
          <button
            className="button secondary"
            onClick={() => onNavigate("explorer")}
          >
            Select another investigation
          </button>
        </EmptyState>
      ) : (
        <>
          <button className="button primary" disabled={busy} onClick={onLoad}>
            {busy ? "Loading comparison…" : `Compare ${selectedIds.length} selected`}
          </button>
          {comparison && (
            <>
              <NoticeList
                title="Differences summary"
                items={comparison.differences_summary}
              />
              <div className="table-scroll comparison-table-wrap">
                <table className="comparison-table">
                  <thead>
                    <tr>
                      <th scope="col">Field</th>
                      <th scope="col">Comparison</th>
                      {comparison.investigations.map((item) => (
                        <th scope="col" key={item.investigation_id}>
                          <span>{item.title}</span>
                          <small>{item.investigation_id}</small>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {comparison.field_comparisons.map((field) => (
                      <tr key={field.field}>
                        <th scope="row">{comparisonFieldLabel(field.field)}</th>
                        <td>
                          <span className={`comparison-status ${field.status}`}>
                            {comparisonStatusLabel(field.status)}
                          </span>
                          {field.explanation && (
                            <small className="comparison-explanation">
                              {field.explanation}
                            </small>
                          )}
                        </td>
                        {comparison.investigations.map((item) => {
                          const fieldValue = field.values.find(
                            (value) => value.investigation_id === item.investigation_id,
                          );
                          return (
                            <td key={item.investigation_id}>
                              {formatComparisonValue(
                                field.field,
                                fieldValue?.value ?? null,
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="comparison-sources">
                {comparison.investigations.map((item) => (
                  <section
                    className="comparison-source-card"
                    key={item.investigation_id}
                    aria-label={`Sources for ${item.title}`}
                  >
                    <h3>{item.title}</h3>
                    <p className="record-id">{item.investigation_id}</p>
                    <CitationList citations={item.citations} />
                  </section>
                ))}
              </div>
              <NoticeList
                title="Comparison limitations"
                items={comparison.limitations}
              />
            </>
          )}
        </>
      )}
    </section>
  );
}

function comparisonFieldLabel(field: ComparisonFieldName): string {
  return field.replace(/_/g, " ");
}

function comparisonStatusLabel(status: FieldComparison["status"]): string {
  if (status === "same") return "Same (reported values)";
  if (status === "different") return "Different";
  return "Not comparable / missing";
}

function formatComparisonValue(
  field: ComparisonFieldName,
  value: string | string[] | InvestigationConditions | null,
): string {
  if (value === null) return "Not reported";
  if (Array.isArray(value)) {
    return value.length ? value.join("; ") : "Not reported";
  }
  if (typeof value === "string") {
    return value === "unknown" ? "Not reported" : value;
  }
  if (field === "conditions" && isInvestigationConditions(value)) {
    const pressure =
      value.pressure.value == null || value.pressure.unit == null
        ? "Not reported"
        : `${value.pressure.value} ${value.pressure.unit}`;
    return [
      `Oxygen: ${value.oxygen_pct == null ? "Not reported" : `${value.oxygen_pct}%`}`,
      `Pressure: ${pressure}`,
      `Other: ${value.other.length ? value.other.join("; ") : "Not reported"}`,
    ].join(" · ");
  }
  return "Not reported";
}

function isInvestigationConditions(
  value: InvestigationConditions,
): value is InvestigationConditions {
  return (
    typeof value === "object" &&
    value !== null &&
    "oxygen_pct" in value &&
    "pressure" in value &&
    "other" in value
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

function RecordDetail({
  item,
  selected,
  canSelect,
  onToggleComparison,
}: {
  item: Investigation;
  selected: boolean;
  canSelect: boolean;
  onToggleComparison: (id: string) => void;
}) {
  return (
    <div className="detail-content">
      <p className="eyebrow">INVESTIGATION RECORD</p>
      <h2>{item.title}</h2>
      <p className="record-id">{item.investigation_id}</p>
      <div className="detail-tags">
        <span className="tag">{item.research_area}</span>
        <span className="tag quiet">
          {displayEnum(item.data_availability)}
        </span>
      </div>
      <div className="detail-actions">
        <button
          className="button secondary"
          aria-pressed={selected}
          disabled={!selected && !canSelect}
          onClick={() => onToggleComparison(item.investigation_id)}
        >
          {selected
            ? "Remove from comparison"
            : canSelect
              ? "Select for comparison"
              : "Comparison selection limit reached"}
        </button>
      </div>
      <Info label="Acronym" value={item.acronym} />
      <Info label="Environment" value={displayEnum(item.environment)} />
      <Info
        label="Data availability"
        value={displayEnum(item.data_availability)}
      />
      <DetailList title="Objectives" items={item.objectives} />
      <Info
        label="Materials or fuels"
        value={joinedOrMissing(item.materials_or_fuels)}
      />
      <Info
        label="Oxygen"
        value={item.conditions.oxygen_pct == null
          ? null
          : `${item.conditions.oxygen_pct}%`}
      />
      <Info
        label="Pressure"
        value={formatPressure(item.conditions.pressure)}
      />
      <Info
        label="Additional conditions"
        value={joinedOrMissing(item.conditions.other)}
      />
      <Info
        label="Last verified"
        value={item.last_verified_at}
      />
      <Info
        label="Hardware"
        value={joinedOrMissing(item.hardware)}
      />
      <Info
        label="Sensors"
        value={joinedOrMissing(item.sensors)}
      />
      <Info
        label="Measured variables"
        value={joinedOrMissing(item.variables_measured)}
      />
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

function displayEnum(value: string): string {
  return value.replace(/_/g, " ");
}

function joinedOrMissing(values: string[]): string | null {
  return values.length ? values.join(", ") : null;
}

function formatPressure(pressure: Investigation["conditions"]["pressure"]): string | null {
  if (pressure.value == null || !pressure.unit) return null;
  return `${pressure.value} ${pressure.unit}`;
}

function MeasurementsView({ measurements }: { measurements: MeasurementList }) {
  const groups = new Map<string, Measurement[]>();
  for (const point of measurements.data) {
    const key = `${point.variable}\u0000${point.unit}`;
    groups.set(key, [...(groups.get(key) ?? []), point]);
  }

  return (
    <div className="measurements-view">
      <p className="measurement-observation-note" role="note">
        Plotted data are reported observations, not predictions.
      </p>
      {[...groups.values()].map((points) => (
        <MeasurementChart
          key={`${points[0].variable}\u0000${points[0].unit}`}
          points={points}
        />
      ))}
      <MeasurementsTable measurements={measurements} />
    </div>
  );
}

function MeasurementChart({ points }: { points: Measurement[] }) {
  const width = 720;
  const height = 260;
  const margin = { top: 20, right: 20, bottom: 58, left: 76 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const values = points.map((point) => point.value);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const span = maximum - minimum || Math.max(Math.abs(minimum) * 0.1, 1);
  const lower = minimum - span * 0.08;
  const upper = maximum + span * 0.08;
  const range = upper - lower;
  const y = (value: number) =>
    margin.top + ((upper - value) / range) * plotHeight;
  const ticks = Array.from({ length: 5 }, (_, index) => {
    const value = lower + (range * index) / 4;
    return { value, y: y(value) };
  });

  return (
    <figure className="measurement-chart">
      <figcaption>
        <strong>{points[0].variable}</strong>
        <span>
          Reported observations · {points[0].unit} · Sources:{" "}
          {[...new Set(points.map((point) => point.source_id))].join(", ")}
        </span>
      </figcaption>
      <div className="measurement-chart-scroll">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label={`${points[0].variable} reported observations, vertical axis in ${points[0].unit}, horizontal axis by investigation. Sources: ${[...new Set(points.map((point) => point.source_id))].join(", ")}`}
        >
          {ticks.map((tick) => (
            <g key={tick.value}>
              <line
                x1={margin.left}
                x2={width - margin.right}
                y1={tick.y}
                y2={tick.y}
                className="measurement-gridline"
              />
              <text
                x={margin.left - 10}
                y={tick.y + 4}
                textAnchor="end"
                className="measurement-tick"
              >
                {Number(tick.value.toPrecision(3))}
              </text>
            </g>
          ))}
          <line
            x1={margin.left}
            x2={margin.left}
            y1={margin.top}
            y2={height - margin.bottom}
            className="measurement-axis"
          />
          <line
            x1={margin.left}
            x2={width - margin.right}
            y1={height - margin.bottom}
            y2={height - margin.bottom}
            className="measurement-axis"
          />
          <text
            transform={`translate(18 ${margin.top + plotHeight / 2}) rotate(-90)`}
            textAnchor="middle"
            className="measurement-axis-label"
          >
            Value ({points[0].unit})
          </text>
          <text
            x={margin.left + plotWidth / 2}
            y={height - 8}
            textAnchor="middle"
            className="measurement-axis-label"
          >
            Investigation
          </text>
          {points.map((point, index) => {
            const x =
              margin.left + ((index + 1) / (points.length + 1)) * plotWidth;
            return (
              <g key={point.measurement_id}>
                <circle
                  cx={x}
                  cy={y(point.value)}
                  r={5}
                  className="measurement-point"
                >
                  <title>
                    {`${point.investigation_id}: ${point.reported_value ?? point.value} ${point.unit}; ${point.document_title} (${point.source_id})`}
                  </title>
                </circle>
                <text
                  x={x}
                  y={height - margin.bottom + 18}
                  textAnchor="middle"
                  className="measurement-tick"
                >
                  {point.investigation_id}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </figure>
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
            <th>Observation context</th>
            <th>Source</th>
            <th>Location and evidence</th>
          </tr>
        </thead>
        <tbody>
          {measurements.data.map((item) => (
            <tr key={item.measurement_id}>
              <td>{item.investigation_id}</td>
              <td>{item.variable}</td>
              <td>{item.reported_value ?? item.value}</td>
              <td>{item.unit}</td>
              <td>
                {Object.keys(item.observation_context).length
                  ? Object.entries(item.observation_context)
                      .map(([key, value]) => `${key}: ${value ?? "Not reported"}`)
                      .join("; ")
                  : "Not reported"}
              </td>
              <td>
                <a href={item.source_url} target="_blank" rel="noreferrer">
                  {item.document_title}
                </a>
                <small className="measurement-source-id">{item.source_id}</small>
              </td>
              <td>
                {[
                  item.page_number && `PDF p. ${item.page_number}`,
                  item.section,
                  item.table_reference,
                ]
                  .filter(Boolean)
                  .join(" · ") || "Not reported"}
                {item.supporting_excerpt && (
                  <details className="measurement-evidence">
                    <summary>Supporting excerpt</summary>
                    <blockquote>{item.supporting_excerpt}</blockquote>
                  </details>
                )}
                {item.reviewed_by ? (
                  <small className="measurement-reviewer">
                    Reviewed by {item.reviewed_by}
                  </small>
                ) : (
                  <small className="measurement-reviewer">
                    Reviewer attribution not reported
                  </small>
                )}
                {item.review_notes && (
                  <details className="measurement-evidence">
                    <summary>Review audit note</summary>
                    <blockquote>{item.review_notes}</blockquote>
                  </details>
                )}
              </td>
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
        <p className="muted">Not reported</p>
      )}
    </div>
  );
}

function Info({
  label,
  value,
}: {
  label: string;
  value: string | null | undefined;
}) {
  return (
    <div className="info-row">
      <span>{label}</span>
      <strong>{value || "Not reported"}</strong>
    </div>
  );
}

function CitationList({
  citations,
}: {
  citations: (InvestigationSource | SourceCitation)[];
}) {
  if (!citations.length) {
    return <p className="muted small">Not reported</p>;
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
          <span> · {citation.verification_status}</span>
          {citation.local_file_path && (
            <span> · original file preserved</span>
          )}
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
