"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, ArrowRight, Bell, ChartColumnIncreasing, ChevronDown, ChevronRight, CircleCheck, Database, FileText, FlaskConical, GitBranch, History, LayoutGrid, Moon, PanelLeftClose, Play, Plus, Search, Settings, ShieldCheck, Sparkles, Sun, Workflow, X, type LucideIcon } from "lucide-react";
import { date, percent, type Dataset, type Run } from "./api";
import { Bars, Empty, ErrorNote, Loading, Panel, RunTable, Status, useResource } from "./ui";
import { DatasetDetail, Registry } from "./datasets";
import { Analysis, Experiment } from "./analysis";

const groups: { title: string; items: [string, LucideIcon][] }[] = [
  { title: "Workspace", items: [["Overview",LayoutGrid],["Dataset Registry",Database],["Experiments",FlaskConical]] },
  { title: "Intelligence", items: [["Agent Runs",Play],["Workflow Monitor",Workflow],["EDA Explorer",ChartColumnIncreasing],["Model Benchmarking",GitBranch],["Model Evaluation",ShieldCheck]] },
  { title: "Reporting", items: [["AI Insights",Sparkles],["Reports",FileText],["Analysis History",History]] },
  { title: "System", items: [["Settings",Settings],["System Health",Activity]] },
];
const descriptions: Record<string,string> = {
  Overview: "Monitor analytical workloads, model performance, and autonomous execution activity.",
  "Dataset Registry": "Upload, inspect, and profile datasets before running an analysis.",
  Experiments: "Configure a classification experiment and launch the agent workflow.",
  "Agent Runs": "Inspect the execution stages, logs, and outputs of an analysis.",
  "Workflow Monitor": "Follow agent activity and review recorded execution events.",
  "EDA Explorer": "Explore feature statistics, missing values, correlations, and target classes.",
  "Model Benchmarking": "Compare classifier performance on the held-out dataset.",
  "Model Evaluation": "Inspect quality scores, verdicts, and follow-up recommendations.",
  "AI Insights": "Read the analytical explanation and review its generation status.",
  Reports: "Review reports and download artifacts from completed analyses.",
  "Analysis History": "Search and reopen previous analysis runs.",
  Settings: "Manage workspace appearance and review supported analysis defaults.",
  "System Health": "Review connectivity and workspace service status.",
};

type Location = { page: string; id?: string; dataset?: string };
const slug = (page: string) => page.toLowerCase().replaceAll(" ", "-");
function fromUrl(): Location {
  const params = new URLSearchParams(window.location.search);
  const page = Object.keys(descriptions).find(name => slug(name) === params.get("view")) ?? "Overview";
  return { page, id: params.get("id") ?? undefined, dataset: params.get("dataset") ?? undefined };
}

export default function Workspace() {
  const [location, setLocation] = useState<Location>({ page: "Overview" });
  const [revision, setRevision] = useState(0);
  const [theme, setTheme] = useState("light");
  const [collapsed, setCollapsed] = useState(false);
  const [menu, setMenu] = useState("");
  const [search, setSearch] = useState("");
  const refresh = useCallback(() => setRevision(value => value + 1), []);
  const runs = useResource<Run[]>("analyses", revision);
  const datasets = useResource<Dataset[]>("datasets", revision);
  const health = useResource<Record<string,string>>("health", revision);
  const { page, id, dataset } = location;
  useEffect(() => {
    const sync = () => setLocation(fromUrl());
    sync();
    window.addEventListener("popstate", sync);
    setTheme(localStorage.getItem("aura-theme") === "dark" ? "dark" : "light");
    setCollapsed(window.innerWidth < 850);
    return () => window.removeEventListener("popstate", sync);
  }, []);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  function chooseTheme(value: string) {
    setTheme(value); localStorage.setItem("aura-theme", value);
  }
  function go(next: string, run?: string, data?: string) {
    const params = new URLSearchParams({ view: slug(next) });
    if (run) params.set("id", run);
    if (data) params.set("dataset", data);
    window.history.pushState(null, "", "?" + params);
    setLocation({ page: next, id: run, dataset: data });
    setMenu(""); setSearch("");
  }
  const create = () => go("Experiments");
  const open = (run: string) => go("Agent Runs", run);
  const allRuns = runs?.data ?? [];
  const allDatasets = datasets?.data ?? [];
  const active = allRuns.filter(run => ["running","queued"].includes(run.status));
  const isRunView = ["Agent Runs","Workflow Monitor","EDA Explorer","Model Benchmarking","Model Evaluation","AI Insights","Reports"].includes(page);
  const filteredRuns = page === "Workflow Monitor" ? active : page === "Reports" ? allRuns.filter(run => run.status === "completed") : allRuns;
  const matching = search.trim().toLowerCase();
  return <div className={"shell" + (collapsed ? " collapsed" : "")}>
    <aside className="sidebar">
      <button className="brand" onClick={() => go("Overview")} aria-label="AURA-DS overview"><span className="mark"><Activity size={21}/></span><span><strong>AURA-DS</strong><small>Analytics workspace</small></span></button>
      <nav aria-label="Workspace navigation">{groups.map(group => <div className="nav-group" key={group.title}><h2>{group.title}</h2>{group.items.map(([name, Icon]) => <button key={name} className={page === name ? "current" : ""} aria-current={page === name ? "page" : undefined} aria-label={name} title={name} onClick={() => go(name, isRunView && ["EDA Explorer","Model Benchmarking","Model Evaluation","AI Insights","Reports","Agent Runs","Workflow Monitor"].includes(name) ? id : undefined)}><Icon size={16}/><span>{name}</span></button>)}</div>)}</nav>
      <button className="sidebar-foot" onClick={() => go("System Health")} aria-label="System health"><i className={health?.data ? "online" : ""}/><span>{health?.data ? "API connected" : health?.error ? "API unavailable" : "Connecting"}</span><ChevronRight size={14}/></button>
    </aside>
    <div className="frame">
      <header className="topbar">
        <button className="icon" onClick={() => setCollapsed(!collapsed)} aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}><PanelLeftClose size={17}/></button>
        <div className="breadcrumbs"><span>Workspace</span><ChevronRight size={13}/><strong>{page}</strong>{id && <><ChevronRight size={13}/><code>{id.slice(0,8)}</code></>}</div>
        <div className="header-actions">
          <button className="button quick-search" onClick={() => setMenu(menu === "search" ? "" : "search")}><Search size={15}/><span>Search workspace</span></button>
          <button className="icon" aria-label="Notifications" onClick={() => setMenu(menu === "notifications" ? "" : "notifications")}><Bell size={17}/></button>
          <button className="icon" aria-label="Toggle theme" onClick={() => chooseTheme(theme === "light" ? "dark" : "light")}>{theme === "light" ? <Moon size={17}/> : <Sun size={17}/>}</button>
          <button className="profile" aria-label="Workspace profile" onClick={() => setMenu(menu === "profile" ? "" : "profile")}><span>AD</span><ChevronDown size={13}/></button>
        </div>
      </header>
      {menu && <section className="popover" aria-label={menu}><div className="popup-head"><strong>{menu === "search" ? "Search workspace" : menu === "notifications" ? "Run activity" : "Local workspace"}</strong><button className="icon" aria-label="Close menu" onClick={() => setMenu("")}><X size={16}/></button></div>
        {menu === "search" && <><input autoFocus aria-label="Search pages, datasets, or runs" placeholder="Search pages, datasets, or runs…" value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => { if (e.key === "Escape") setMenu(""); }}/>
          {matching && <div className="popup-list">{Object.keys(descriptions).filter(name => name.toLowerCase().includes(matching)).map(name => <button key={name} onClick={() => go(name)}>{name}</button>)}{allDatasets.filter(item => item.name.toLowerCase().includes(matching)).slice(0, 6).map(item => <button key={item.id} onClick={() => go("Dataset Registry",undefined,item.id)}>{item.name}</button>)}{allRuns.filter(item => (item.dataset + item.id).toLowerCase().includes(matching)).slice(0,6).map(item => <button key={item.id} onClick={() => open(item.id)}>{item.dataset} · {item.id.slice(0,8)}</button>)}</div>}</>}
        {menu === "notifications" && <div className="popup-list">{allRuns.slice(0,5).map(run => <button key={run.id} onClick={() => open(run.id)}>{run.dataset}<Status value={run.status}/></button>)}{!allRuns.length && <p className="muted">No run activity yet.</p>}</div>}
        {menu === "profile" && <button className="button" onClick={() => go("Settings")}>Workspace settings</button>}
      </section>}
      <main>
        <div className="page-head"><div><h1>{page}</h1><p>{descriptions[page]}</p></div><button className="button primary" onClick={page === "Dataset Registry" && dataset ? () => go(page) : create}>{page === "Dataset Registry" && dataset ? "All datasets" : <><Plus size={17}/> New analysis</>}</button></div>
        {page === "Overview" && (runs?.error ? <ErrorNote message={runs.error}/> : !runs?.data || !datasets?.data ? datasets?.error ? <ErrorNote message={datasets.error}/> : <Loading/> : <Overview runs={allRuns} datasets={allDatasets} online={Boolean(health?.data)} open={open} create={create} go={go}/>)}
        {page === "Dataset Registry" && (dataset ? <DatasetDetail key={dataset} id={dataset} runs={allRuns} openRun={open} create={() => go("Experiments",undefined,dataset)}/> : datasets?.error ? <ErrorNote message={datasets.error}/> : datasets?.data ? <Registry datasets={allDatasets} open={key => go(page,undefined,key)} refresh={refresh}/> : <Loading/>)}
        {page === "Experiments" && (datasets?.error ? <ErrorNote message={datasets.error}/> : datasets?.data ? <Experiment key={dataset ?? "new"} initial={dataset} datasets={allDatasets} onStart={key => { refresh(); open(key); }} onUpload={() => go("Dataset Registry")}/> : <Loading/>)}
        {isRunView && id && <Analysis key={id} id={id} view={page} setView={name => go(name,id)} refresh={refresh} exit={() => go(page)}/>}
        {(page === "Analysis History" || (isRunView && !id)) && <Panel title={page === "Workflow Monitor" ? "Active runs" : "Analysis runs"} caption="Open a run to inspect its recorded results.">{runs?.error ? <ErrorNote message={runs.error}/> : runs?.data ? <RunTable runs={filteredRuns} open={key => go(page === "Analysis History" ? "Agent Runs" : page,key)} create={create}/> : <Loading/>}</Panel>}
        {page === "Settings" && <Panel title="Workspace preferences"><div className="form-fields"><label>Appearance<select value={theme} onChange={e => chooseTheme(e.target.value)}><option value="light">Light</option><option value="dark">Dark</option></select></label><dl className="facts"><dt>Default task</dt><dd>Classification</dd><dt>Default test split</dt><dd>20%</dd><dt>Random state</dt><dd>42</dd><dt>Evaluation threshold</dt><dd>0.70</dd></dl><button className="button" onClick={() => go("System Health")}>API configuration <ArrowRight size={15}/></button></div></Panel>}
        {page === "System Health" && <Panel title="Service status" action={<button className="button" onClick={refresh}>Refresh checks</button>}>{health?.error ? <ErrorNote message={health.error}/> : health?.data ? <dl className="facts padded">{Object.entries(health.data).map(([service,value]) => <div className="fact-row" key={service}><dt>{service}</dt><dd>{value}</dd></div>)}</dl> : <Loading/>}</Panel>}
      </main>
    </div>
  </div>;
}

function Overview({ runs, datasets, online, open, create, go }: { runs: Run[]; datasets: Dataset[]; online: boolean; open: (id: string) => void; create: () => void; go: (page: string) => void }) {
  const results = runs.filter(run => run.score != null);
  const active = runs.filter(run => ["running","queued"].includes(run.status));
  const passed = runs.filter(run => run.verdict === "PASS").length;
  const failed = runs.filter(run => run.status === "failed").length;
  const byDay = new Map<string, number>();
  for (const run of [...runs].reverse()) {
    const day = run.created.slice(0, 10);
    byDay.set(day, (byDay.get(day) ?? 0) + 1);
  }
  const metrics: [string, string | number, LucideIcon][] = [
    ["Analysis runs",runs.length,Activity],["Datasets processed",new Set(results.map(run => run.dataset_id)).size,Database],
    ["Passed evaluations",passed,CircleCheck],["Failed executions",failed,ShieldCheck],
    ["Mean system score",percent(results.length ? results.reduce((sum,run) => sum + (run.score ?? 0),0) / results.length : undefined),ChartColumnIncreasing],
    ["Active runs",active.length,Workflow],
  ];
  return <>
    <div className="metric-grid">{metrics.map(([label,value,Icon]) => <div className="metric" key={label}><span><Icon size={15}/>{label}</span><strong>{value}</strong></div>)}</div>
    <div className="overview-grid">
      <Panel title="Analysis activity" caption="Run submissions by day"><Bars label="Analysis runs" data={Array.from(byDay).slice(-14).map(([name,value]) => ({ name: name.slice(5),value }))}/></Panel>
      <Panel title="Evaluation verdicts" caption="Distribution across scored analyses"><Bars label="Evaluations" data={results.length ? [{ name: "PASS",value: passed },{ name: "FAIL",value: results.length - passed }] : []}/></Panel>
    </div>
    <Panel title="Recent analysis executions" caption="Search, filter, or reopen an analysis" action={<button className="button" onClick={() => go("Analysis History")}>View history <ArrowRight size={14}/></button>}><RunTable runs={runs} open={open} create={create}/></Panel>
    <div className="overview-grid">
      <Panel title="Model performance trend" caption="System scores from recent evaluated runs"><Bars label="System score" data={results.slice(0,10).reverse().map(run => ({ name: run.id.slice(0,6),value: run.score ?? 0 }))}/></Panel>
      <Panel title="Dataset activity" action={<button className="text-button" onClick={() => go("Dataset Registry")}>Registry <ArrowRight size={14}/></button>}>{datasets.length ? <div className="activity-list">{datasets.slice(0,5).map(item => <div key={item.id}><Database size={16}/><strong>{item.name}</strong><span>{date(item.created)}</span></div>)}</div> : <Empty title="No datasets uploaded" action={<button className="button" onClick={() => go("Dataset Registry")}>Upload CSV</button>}/>}</Panel>
    </div>
    <Panel title="System execution health" action={<button className="text-button" onClick={() => go("System Health")}>Service checks <ArrowRight size={14}/></button>}><div className="toolbar"><Status value={online ? "online" : "unverified"}/><span className="muted">{active.length} active · {failed} failed</span></div></Panel>
  </>;
}
