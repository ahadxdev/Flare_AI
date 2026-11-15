import type { ReactNode } from "react";
import type { HealthResponse } from "../api";

export type AppRoute =
  | "dashboard"
  | "explorer"
  | "investigation-detail"
  | "scenario"
  | "compare"
  | "assistant"
  | "brief";

const navigation: { id: AppRoute; label: string; icon: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: "⌂" },
  { id: "explorer", label: "Investigation Explorer", icon: "◉" },
  { id: "scenario", label: "Mission Scenario", icon: "⌁" },
  { id: "compare", label: "Compare", icon: "⇄" },
  { id: "assistant", label: "AI Research Assistant", icon: "✳" },
  { id: "brief", label: "Research Brief", icon: "↗" },
];

const titles: Record<AppRoute, string> = {
  dashboard: "Dashboard",
  explorer: "Investigation Explorer",
  "investigation-detail": "Investigation Detail",
  scenario: "Mission Scenario",
  compare: "Compare",
  assistant: "AI Research Assistant",
  brief: "Research Brief",
};

function routeFromHash(hash: string): AppRoute {
  const [route] = hash.replace(/^#\/?/, "").split(/[/?]/);
  if (route === "investigation") return "investigation-detail";
  return navigation.find((item) => item.id === route)?.id ?? "dashboard";
}

export function readRoute(): AppRoute {
  return routeFromHash(window.location.hash);
}

export function readInvestigationId(): string | null {
  const [, encodedId] = window.location.hash
    .replace(/^#\/?/, "")
    .split(/[/?]/);
  if (!encodedId) return null;
  try {
    return decodeURIComponent(encodedId);
  } catch {
    return encodedId;
  }
}

export function AppLayout({
  activeRoute,
  health,
  catalogCount,
  onNavigate,
  children,
}: {
  activeRoute: AppRoute;
  health: { status: "loading" | "ready" | "error"; data?: HealthResponse };
  catalogCount?: number;
  onNavigate: (route: AppRoute) => void;
  children: ReactNode;
}) {
  const healthLabel =
    health.status === "loading"
      ? "Checking API"
      : health.status === "ready" && health.data?.status === "ok"
        ? "API online"
        : "API unavailable";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#dashboard"
          onClick={() => onNavigate("dashboard")}
        >
          <span className="brand-mark" aria-hidden="true">F</span>
          <span>
            <strong>FLARE</strong>
            <small>SCIENCE INTELLIGENCE</small>
          </span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="primary-nav" aria-label="Primary navigation">
          {navigation.map((item) => (
            <a
              key={item.id}
              className={`nav-item ${activeRoute === item.id ? "active" : ""}`}
              href={`#${item.id}`}
              aria-current={activeRoute === item.id ? "page" : undefined}
              onClick={() => onNavigate(item.id)}
            >
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>
              <span>{item.label}</span>
              {item.id === "explorer" && catalogCount !== undefined && (
                <span className="nav-count" aria-label={`${catalogCount} investigations`}>
                  {catalogCount}
                </span>
              )}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <span className={`status-dot ${health.status === "error" ? "offline" : ""}`} />
          {healthLabel}
          <p>Student-built research tool<br />Not an official NASA system</p>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs">
            FLARE AI <span>/</span> {titles[activeRoute]}
          </div>
          <div className="top-status">
            <span className={`status-dot ${health.status === "error" ? "offline" : ""}`} />
            <span>{healthLabel}</span>
            <span className="official-notice">STUDENT-BUILT · NOT OFFICIAL NASA</span>
          </div>
        </header>
        <div className="content">
          <div className="page-heading">
            <div>
              <p className="eyebrow">FLARE AI · STUDENT RESEARCH PROTOTYPE</p>
              <h1>{titles[activeRoute]}</h1>
            </div>
            {catalogCount !== undefined && (
              <div className="catalog-pill">
                <span className="status-dot" />
                {catalogCount} indexed {catalogCount === 1 ? "record" : "records"}
              </div>
            )}
          </div>
          {children}
          <footer className="page-footer">
            <span>FLARE AI · Student-built research tool</span>
            <span>Not an official NASA system · Research relevance is not fire risk</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
