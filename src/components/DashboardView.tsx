import type { HealthResponse, InvestigationPage } from "../api";
import { EmptyState, ErrorState, LoadingState, type RemoteState } from "./AsyncState";
import type { AppRoute } from "./AppLayout";

export function DashboardView({
  health,
  catalog,
  onRetryHealth,
  onRetryCatalog,
  onNavigate,
}: {
  health: RemoteState<HealthResponse>;
  catalog: RemoteState<InvestigationPage>;
  onRetryHealth: () => void;
  onRetryCatalog: () => void;
  onNavigate: (route: AppRoute) => void;
}) {
  return (
    <div className="dashboard-stack">
      <section className="welcome-panel">
        <div>
          <p className="eyebrow">SCIENCE INTELLIGENCE FOR SPACE HABITATS</p>
          <h2>Explore the evidence.<br /><span>Understand its limits.</span></h2>
          <p className="welcome-copy">
            Search NASA PSI combustion investigations and compare their indexed
            evidence with a hypothetical mission scenario.
          </p>
          <button className="button primary" onClick={() => onNavigate("explorer")}>
            Explore investigations <span aria-hidden="true">→</span>
          </button>
        </div>
        <div className="welcome-orbit" aria-hidden="true">
          <span className="orbit-ring orbit-ring-one" />
          <span className="orbit-ring orbit-ring-two" />
          <span className="orbit-core">F</span>
        </div>
      </section>

      <div className="dashboard-metrics">
        <section className="panel metric-card">
          <div className="metric-label">API STATUS</div>
          {health.status === "loading" && <LoadingState label="Checking backend…" />}
          {health.status === "error" && (
            <ErrorState message={health.message} onRetry={onRetryHealth} />
          )}
          {health.status === "ready" && (
            <>
              <strong className="metric-value">
                <span className="status-dot" /> Online
              </strong>
              <p>Connected to the FLARE AI API.</p>
            </>
          )}
        </section>
        <section className="panel metric-card">
          <div className="metric-label">INDEXED INVESTIGATIONS</div>
          {catalog.status === "loading" && <LoadingState label="Loading catalog…" />}
          {catalog.status === "error" && (
            <ErrorState message={catalog.message} onRetry={onRetryCatalog} />
          )}
          {catalog.status === "ready" && (
            <>
              <strong className="metric-value">{catalog.data.total}</strong>
              <p>Records returned by the connected catalog.</p>
            </>
          )}
        </section>
      </div>

      <div className="dashboard-columns">
        <section className="panel dashboard-panel">
          <div className="panel-title">
            <div>
              <h2>Recent investigations</h2>
              <p>Loaded from the API catalog. No sample NASA data is shown.</p>
            </div>
            <button className="text-button" onClick={() => onNavigate("explorer")}>
              Open explorer <span aria-hidden="true">→</span>
            </button>
          </div>
          {catalog.status === "loading" && <LoadingState label="Loading investigations…" />}
          {catalog.status === "error" && (
            <ErrorState message={catalog.message} onRetry={onRetryCatalog} />
          )}
          {catalog.status === "ready" &&
            (catalog.data.items.length === 0 ? (
              <EmptyState
                title="No indexed investigations yet"
                detail="The catalog is empty. Add verified NASA PSI records to make investigations available here."
              />
            ) : (
              <div className="dashboard-records">
                {catalog.data.items.slice(0, 4).map((record) => (
                  <button
                    className="dashboard-record"
                    key={record.investigation_id}
                    onClick={() => onNavigate("explorer")}
                  >
                    <span className="tag">{record.research_area}</span>
                    <span className="dashboard-record-title">{record.title}</span>
                    <span className="record-id">{record.investigation_id}</span>
                  </button>
                ))}
              </div>
            ))}
        </section>

        <section className="panel dashboard-panel focus-panel">
          <p className="eyebrow">EVIDENCE-FIRST WORKFLOW</p>
          <h2>From investigations to research gaps</h2>
          <ol className="workflow-list">
            <li><span>01</span> Browse source-backed investigations</li>
            <li><span>02</span> Configure a hypothetical scenario</li>
            <li><span>03</span> Compare evidence and its limitations</li>
            <li><span>04</span> Build a cited research brief</li>
          </ol>
          <button
            className="button secondary"
            onClick={() => onNavigate("scenario")}
          >
            Configure a mission scenario
          </button>
        </section>
      </div>

      <div className="safety-banner" role="note">
        <strong>Student-built research tool · Not an official NASA system</strong>
        <span>
          FLARE AI ranks research relevance only. It does not estimate fire risk
          or establish habitat safety.
        </span>
      </div>
    </div>
  );
}
