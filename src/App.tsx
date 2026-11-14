import { useEffect, useMemo, useState } from "react";
import { api, type Investigation, type Measurement, type Report, type ScenarioAnalysis, type ScenarioRequest } from "./api";

type Section = "investigations" | "scenario" | "compare" | "assistant" | "measurements" | "report";
const navigation: { id: Section; label: string; icon: string }[] = [
  { id: "investigations", label: "Investigations", icon: "◉" },
  { id: "scenario", label: "Mission scenario", icon: "⌁" },
  { id: "compare", label: "Compare records", icon: "⇄" },
  { id: "assistant", label: "Research assistant", icon: "✳" },
  { id: "measurements", label: "Measurements", icon: "▥" },
  { id: "report", label: "Research brief", icon: "↗" },
];

const initialScenario: ScenarioRequest = {
  environment: "lunar_habitat",
  oxygen_pct: 30,
  pressure: { value: 10.2, unit: "psi" },
  material_or_fuel: null,
  objective: "general",
};

function App() {
  const [section, setSection] = useState<Section>("investigations");
  const [records, setRecords] = useState<Investigation[]>([]);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState<Investigation | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [scenario, setScenario] = useState(initialScenario);
  const [analysis, setAnalysis] = useState<ScenarioAnalysis | null>(null);
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [comparison, setComparison] = useState<Investigation[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const reload = async (term = search) => {
    setError("");
    try {
      const params = new URLSearchParams({ page: "1", page_size: "100" });
      if (term.trim()) params.set("q", term.trim());
      const result = await api.investigations(params);
      setRecords(result.items);
      setTotal(result.total);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load investigations.");
    }
  };

  useEffect(() => {
    void reload("");
    api.measurements().then((result) => setMeasurements(result.items)).catch(() => {
      setError("Unable to load verified measurements.");
    });
  }, []);

  const pageTitle = useMemo(
    () => navigation.find((item) => item.id === section)?.label ?? "FLARE AI",
    [section],
  );

  const run = async <T,>(action: () => Promise<T>, onSuccess: (value: T) => void) => {
    setBusy(true);
    setError("");
    try {
      onSuccess(await action());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The request could not be completed.");
    } finally {
      setBusy(false);
    }
  };

  const toggleSelected = (id: string) => {
    setSelectedIds((ids) =>
      ids.includes(id) ? ids.filter((item) => item !== id) : ids.length < 5 ? [...ids, id] : ids,
    );
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#" onClick={() => setSection("investigations")}>
          <span className="brand-mark">F</span>
          <span><strong>FLARE</strong><small>SCIENCE INTELLIGENCE</small></span>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navigation.map((item) => (
            <button key={item.id} className={`nav-item ${section === item.id ? "active" : ""}`} onClick={() => { setSection(item.id); setError(""); }}>
              <span className="nav-icon">{item.icon}</span>{item.label}
              {item.id === "investigations" && <span className="nav-count">{total}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <span className="status-dot" /> Evidence-first mode
          <p>Research relevance only<br />Never a fire-risk prediction</p>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs">FLARE AI <span>/</span> {pageTitle}</div>
          <div className="top-status"><span className="status-dot" /> LOCAL RESEARCH CATALOG</div>
        </header>
        <div className="content">
          <div className="page-heading">
            <div><p className="eyebrow">NASA PHYSICAL SCIENCES INFORMATICS</p><h1>{pageTitle}</h1></div>
            <div className="catalog-pill"><span className="status-dot" /> {total} indexed {total === 1 ? "record" : "records"}</div>
          </div>
          {error && <div role="alert" className="error-banner"><span>Request issue</span>{error}<button onClick={() => setError("")} aria-label="Dismiss error">×</button></div>}

          {section === "investigations" && (
            <div className="layout-two">
              <section className="panel records-panel">
                <div className="panel-title"><div><h2>Investigation library</h2><p>Browse sourced microgravity combustion research.</p></div><span className="count-badge">{total} records</span></div>
                <form className="search-row" onSubmit={(event) => { event.preventDefault(); setSearch(query); void reload(query); }}>
                  <label className="search-box"><span>⌕</span><input aria-label="Search investigations" placeholder="Search investigations..." value={query} onChange={(event) => setQuery(event.target.value)} /></label>
                  <button className="button secondary" type="submit">Search</button>
                </form>
                {records.length === 0 ? <EmptyState title="No indexed investigations yet" detail="FLARE AI does not include sample or invented NASA records. Import canonical records from verified NASA sources to begin exploring." /> :
                  <div className="record-list">{records.map((item) => <article className={`record-card ${selected?.investigation_id === item.investigation_id ? "chosen" : ""}`} key={item.investigation_id}>
                    <button className="record-main" onClick={() => setSelected(item)}><div className="record-top"><span className="tag">{item.research_area}</span><span className="record-id">{item.investigation_id}</span></div><h3>{item.title}</h3><div className="record-meta">{item.environment.replace("_", " ")} <span>·</span> {item.data_availability.replace("_", " ")}</div></button>
                    <label className="compare-check"><input type="checkbox" checked={selectedIds.includes(item.investigation_id)} onChange={() => toggleSelected(item.investigation_id)} aria-label={`Select ${item.title} for comparison`} /></label>
                  </article>)}</div>}
                {selectedIds.length > 0 && <button className="button primary wide" onClick={() => setSection("compare")}>Compare selected ({selectedIds.length})</button>}
              </section>
              <section className="panel detail-panel">
                {selected ? <RecordDetail item={selected} /> : <div className="detail-placeholder"><span className="detail-icon">◉</span><h3>Select an investigation</h3><p>Open a record to review indexed conditions, measurements, findings and source provenance.</p><div className="mini-rule" /><small>Only verified source data is displayed.</small></div>}
              </section>
            </div>
          )}

          {section === "scenario" && <section className="panel form-panel">
            <div className="panel-title"><div><h2>Configure a hypothetical mission</h2><p>Find research with relevant evidence. Similarity does not establish safety.</p></div><span className="tag amber">HYPOTHETICAL SCENARIO</span></div>
            <div className="assumption-note"><strong>Example assumptions</strong><span>30% oxygen and 10.2 psi are user-entered Moon Base demo assumptions—not NASA measurements.</span></div>
            <div className="form-grid">
              <label>Mission environment<select value={scenario.environment} onChange={(e) => setScenario({ ...scenario, environment: e.target.value as ScenarioRequest["environment"] })}><option value="lunar_habitat">Lunar habitat</option><option value="mars_habitat">Mars habitat</option><option value="spacecraft">Spacecraft</option><option value="spacesuit">Spacesuit</option><option value="custom">Custom</option></select></label>
              <label>Research objective<select value={scenario.objective} onChange={(e) => setScenario({ ...scenario, objective: e.target.value as ScenarioRequest["objective"] })}><option value="general">General</option><option value="material_flammability">Material flammability</option><option value="fire_detection">Fire detection</option><option value="fire_suppression">Fire suppression</option><option value="combustion_fundamentals">Combustion fundamentals</option></select></label>
              <label>Oxygen (%)<input type="number" min="0" max="100" step="any" value={scenario.oxygen_pct ?? ""} onChange={(e) => setScenario({ ...scenario, oxygen_pct: e.target.value === "" ? null : Number(e.target.value) })} /></label>
              <label>Pressure (psi)<input type="number" min="0" step="any" value={scenario.pressure.value ?? ""} onChange={(e) => setScenario({ ...scenario, pressure: { value: e.target.value === "" ? null : Number(e.target.value), unit: "psi" } })} /></label>
              <label className="full">Material or fuel (optional)<input placeholder="Enter a material or fuel to contextualize your question" value={scenario.material_or_fuel ?? ""} onChange={(e) => setScenario({ ...scenario, material_or_fuel: e.target.value || null })} /></label>
            </div>
            <button className="button primary" disabled={busy} onClick={() => void run(() => api.analyze(scenario), setAnalysis)}>{busy ? "Analyzing…" : "Analyze research relevance"} <span>→</span></button>
            {analysis && <div className="results-block"><div className="result-banner"><strong>Research relevance—not fire risk</strong><span>Scores rank indexed research evidence; they are not probabilities.</span></div>
              {analysis.matches.length ? analysis.matches.map((match) => <article className="match-card" key={match.investigation_id}><div className="match-head"><div><span className="tag">RESEARCH MATCH</span><h3>{match.title}</h3></div><strong>{match.relevance_score}<small>/100</small></strong></div><p>{match.match_reasons.join(" ")}</p><small>Objective {match.score_breakdown.objective_match.toFixed(2)} · Parameters {match.score_breakdown.parameter_similarity.toFixed(2)} · Measurements {match.score_breakdown.measurement_usefulness.toFixed(2)} · Context/hardware {match.score_breakdown.context_hardware.toFixed(2)}</small><CitationList citations={match.citations} /></article>) : <EmptyState title="No research matches available" detail="There are no investigations in the local catalog to rank. Import verified source records to see transparent comparisons." />}
              <NoticeList title="Research gaps & limitations" items={[...analysis.research_gaps, ...analysis.limitations]} />
            </div>}
          </section>}

          {section === "compare" && <section className="panel form-panel"><div className="panel-title"><div><h2>Compare investigation records</h2><p>Compare indexed fields side by side. Missing data remains missing.</p></div></div>
            {selectedIds.length === 0 && <p className="muted">Select up to five records in the investigation library first.</p>}
            {selectedIds.length > 0 && <button className="button primary" disabled={busy} onClick={() => void run(() => api.compare(selectedIds), (result) => setComparison(result.investigations))}>Load comparison</button>}
            {comparison.length > 0 && <div className="comparison-grid">{comparison.map((item) => <div className="comparison-card" key={item.investigation_id}><h3>{item.title}</h3><Info label="Research area" value={item.research_area} /><Info label="Environment" value={item.environment} /><Info label="Materials/fuels" value={item.materials_or_fuels.join(", ")} /><Info label="Measured variables" value={item.variables_measured.join(", ")} /><Info label="Data availability" value={item.data_availability} /><div className="info-row"><span>Sources</span><CitationList citations={item.sources.map((s) => ({ ...s, quote_or_supported_excerpt: null }))} /></div></div>)}</div>}
          </section>}

          {section === "assistant" && <section className="panel assistant-panel"><div className="panel-title"><div><h2>Evidence-grounded research assistant</h2><p>Answers must be supported by indexed source excerpts.</p></div><span className="tag">PROVENANCE REQUIRED</span></div>
            <div className="chat-empty"><span className="assistant-symbol">✳</span><h3>Ask a research question</h3><p>FLARE AI only answers when verified source excerpts are indexed. It will tell you when evidence is unavailable.</p></div>
            {answer && <div className="chat-answer">{answer}</div>}
            <form className="chat-form" onSubmit={(event) => { event.preventDefault(); void run(() => api.chat(question), (result) => setAnswer(result.answer)); }}><textarea aria-label="Research question" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about an indexed investigation, result, or measurement…" required /><button className="button primary" disabled={busy || !question.trim()}>{busy ? "Checking…" : "Ask"} <span>↑</span></button></form>
            <div className="footnote">No invented sources, measurements, or conclusions. Missing evidence is labeled “not available in indexed sources.”</div>
          </section>}

          {section === "measurements" && <section className="panel records-panel"><div className="panel-title"><div><h2>Verified measurements</h2><p>Only source-linked numeric values are shown.</p></div><span className="count-badge">{measurements.length} measurements</span></div>
            {measurements.length === 0 ? <EmptyState title="No verified measurements indexed" detail="Measurements appear only when their original source, unit, investigation, and conditions are verified and imported." /> : <div className="table-scroll"><table><thead><tr><th>Investigation</th><th>Variable</th><th>Value</th><th>Unit</th><th>Source ID</th></tr></thead><tbody>{measurements.map((item) => <tr key={item.measurement_id}><td>{item.investigation_id}</td><td>{item.variable}</td><td>{item.value}</td><td>{item.unit}</td><td>{item.source_id}</td></tr>)}</tbody></table></div>}
          </section>}

          {section === "report" && <section className="panel form-panel"><div className="panel-title"><div><h2>Generate a research brief</h2><p>Creates an evidence summary with source references, limits and gaps.</p></div></div>
            <p className="muted">Selected investigations: {selectedIds.length ? selectedIds.length : "none"}</p>
            {selectedIds.length === 0 && <button className="button secondary" onClick={() => setSection("investigations")}>Select records in the library</button>}
            {selectedIds.length > 0 && <button className="button primary" disabled={busy} onClick={() => void run(() => api.report(selectedIds), setReport)}>Generate brief <span>→</span></button>}
            {report && <div className="report-card"><span className="tag">EVIDENCE BRIEF</span><h3>{report.title}</h3><pre>{report.brief}</pre><CitationList citations={report.citations} /><NoticeList title="Limitations" items={[...report.limitations, ...report.research_gaps]} /></div>}
          </section>}
          <footer className="page-footer"><span>FLARE AI · Research Intelligence Prototype</span><span>Source facts are distinct from interpretation</span></footer>
        </div>
      </main>
    </div>
  );
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <div className="empty-state"><span className="empty-orbit">⌕</span><h3>{title}</h3><p>{detail}</p></div>;
}

function RecordDetail({ item }: { item: Investigation }) {
  return <div className="detail-content"><p className="eyebrow">INVESTIGATION RECORD</p><h2>{item.title}</h2><div className="detail-tags"><span className="tag">{item.research_area}</span><span className="tag quiet">{item.data_availability.replace("_", " ")}</span></div>
    <p className="record-id">{item.investigation_id}</p><Info label="Environment" value={item.environment} /><Info label="Materials or fuels" value={item.materials_or_fuels.join(", ")} /><Info label="Oxygen" value={item.conditions.oxygen_pct == null ? "Not available in indexed sources" : `${item.conditions.oxygen_pct}%`} /><Info label="Pressure" value={item.conditions.pressure.value == null ? "Not available in indexed sources" : `${item.conditions.pressure.value} ${item.conditions.pressure.unit}`} /><Info label="Hardware" value={item.hardware.join(", ")} /><Info label="Sensors" value={item.sensors.join(", ")} /><Info label="Measured variables" value={item.variables_measured.join(", ")} />
    <div className="detail-section"><h3>Objectives</h3>{item.objectives.length ? <ul>{item.objectives.map((v) => <li key={v}>{v}</li>)}</ul> : <p className="muted">Not available in indexed sources.</p>}</div>
    <div className="detail-section"><h3>Findings</h3>{item.findings.length ? <ul>{item.findings.map((v) => <li key={v}>{v}</li>)}</ul> : <p className="muted">Not available in indexed sources.</p>}</div>
    <div className="detail-section"><h3>Sources <span>{item.sources.length}</span></h3><CitationList citations={item.sources.map((s) => ({ ...s, quote_or_supported_excerpt: null }))} /></div>
    {item.environment === "microgravity" && <div className="caution-note">Microgravity results do not prove partial-gravity performance.</div>}
  </div>;
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="info-row"><span>{label}</span><strong>{value || "Not available in indexed sources"}</strong></div>;
}

function CitationList({ citations }: { citations: { source_id: string; document_title: string; source_url: string; page_number: number | null; section: string | null }[] }) {
  if (!citations.length) return <p className="muted small">No source citations indexed.</p>;
  return <ul className="citation-list">{citations.map((citation) => <li key={citation.source_id}><a href={citation.source_url} target="_blank" rel="noreferrer">{citation.document_title}</a>{citation.page_number && <span> · p. {citation.page_number}</span>}{citation.section && <span> · {citation.section}</span>}</li>)}</ul>;
}

function NoticeList({ title, items }: { title: string; items: string[] }) {
  return items.length ? <div className="notice-list"><strong>{title}</strong><ul>{items.map((item) => <li key={item}>{item}</li>)}</ul></div> : null;
}

export default App;
