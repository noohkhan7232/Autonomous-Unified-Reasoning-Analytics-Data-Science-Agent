"use client";

import { useEffect, useState } from "react";
import { ArrowRight, Download, Play, Printer, Copy, Trash2 } from "lucide-react";
import { ReactFlow, Background, type Node, type Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { api, date, modelName, percent, type Dataset, type Profile, type Run, type RunDetail, type RunEvent } from "./api";
import { Bars, Empty, ErrorNote, Loading, Panel, Status, Table, useResource } from "./ui";
import { Statistics } from "./datasets";

const candidates = ["Logistic Regression", "Random Forest", "Gradient Boosting"];
const stages = ["Planning","Exploratory data analysis","Modeling","Evaluation","Decision routing","Self-correction","Explanation","Final report"];

export function Experiment({ datasets, initial, onStart, onUpload }: { datasets: Dataset[]; initial?: string; onStart: (id: string) => void; onUpload: () => void }) {
  const [dataset, setDataset] = useState(initial ?? "");
  const [target, setTarget] = useState("");
  const [split, setSplit] = useState("20");
  const [seed, setSeed] = useState("42");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const detail = useResource<Dataset>(dataset ? "datasets/" + dataset : null);
  if (!datasets.length) return <Panel title="Dataset required"><Empty title="Upload a dataset to begin" action={<button className="button primary" onClick={onUpload}>Dataset registry</button>}/></Panel>;
  return <form className="setup-grid" onSubmit={async event => {
    event.preventDefault();
    if (pending) return;
    setPending(true); setError("");
    try {
      const run = await api<{ id: string }>("analyses", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: dataset, target, test_size: Number(split) / 100, random_state: Number(seed) }) });
      onStart(run.id);
    } catch (cause) { setError((cause as Error).message); }
    finally { setPending(false); }
  }}>
    <Panel title="Experiment configuration" caption="Choose the data and training parameters for this run.">
      <div className="form-fields">
        <label>Dataset<select required value={dataset} onChange={event => { setDataset(event.target.value); setTarget(""); }}><option value="">Choose a dataset</option>{datasets.map(item => <option value={item.id} key={item.id}>{item.name}</option>)}</select></label>
        <label>Target column<select required disabled={!detail?.data} value={target} onChange={event => setTarget(event.target.value)}><option value="">Choose a target</option>{detail?.data?.schema?.map(column => <option key={column.name}>{column.name}</option>)}</select></label>
        {detail?.error && <ErrorNote message={detail.error}/>}
        <div className="form-row"><label>Test split (%)<input type="number" min="10" max="50" step="1" required value={split} onChange={event => setSplit(event.target.value)}/></label>
        <label>Random state<input type="number" min="0" max="4294967295" step="1" required value={seed} onChange={event => setSeed(event.target.value)}/></label></div>
        {error && <ErrorNote message={error}/>}
      </div>
    </Panel>
    <Panel title="Execution summary" caption="Classification · evaluation threshold 0.70">
      <div className="form-fields"><dl className="facts"><dt>Dataset</dt><dd>{detail?.data?.name ?? "—"}</dd><dt>Target</dt><dd>{target || "—"}</dd><dt>Holdout</dt><dd>{split || "—"}%</dd><dt>Random state</dt><dd>{seed || "—"}</dd></dl>
      <div className="candidate-list">{candidates.map(name => <span key={name}>{name}</span>)}</div>
      <p className="muted">Plan → Explore → Benchmark → Evaluate → Explain → Report</p>
      <button className="button primary" disabled={pending || !target} type="submit"><Play size={15}/>{pending ? "Queuing…" : "Run analysis"}</button></div>
    </Panel>
  </form>;
}

export function Analysis({ id, view, setView, refresh, exit }: { id: string; view: string; setView: (view: string) => void; refresh: () => void; exit: () => void }) {
  const [revision, setRevision] = useState(0);
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [selected, setSelected] = useState("");
  const [streamError, setStreamError] = useState(false);
  const [action, setAction] = useState("");
  const [edaTab, setEdaTab] = useState("Overview");
  const [feature, setFeature] = useState("");
  const resource = useResource<RunDetail>("analyses/" + id, revision);
  const assets = useResource<string[]>(view === "Reports" ? "analyses/" + id + "/artifacts" : null, revision);
  const profile = useResource<Profile>(view === "EDA Explorer" && resource?.data ? "datasets/" + resource.data.dataset_id + "/profile" : null);
  useEffect(() => {
    const stream = new EventSource("/api/analyses/" + id + "/events");
    stream.onopen = () => setStreamError(false);
    stream.onmessage = message => {
      const event: RunEvent = JSON.parse(message.data);
      setEvents(items => items.some(item => item.id === event.id) ? items : [...items, event]);
      if (event.stage === "Execution" || event.status === "completed") setRevision(value => value + 1);
    };
    stream.onerror = () => setStreamError(true);
    stream.addEventListener("end", () => { stream.close(); setRevision(value => value + 1); refresh(); });
    return () => stream.close();
  }, [id, refresh]);

  if (resource?.error) return <ErrorNote message={resource.error}/>;
  if (!resource?.data) return <Loading/>;
  const run = resource.data;
  const result = run.results;
  const workflow = ["Agent Runs","Workflow Monitor"].includes(view);
  const latest = new Map(events.map(event => [event.stage, event]));
  const status = run.status === "queued" && events.some(event => event.status === "running") ? "running" : run.status;
  const nodes: Node[] = stages.map((stage, index) => ({
    id: stage, position: { x: (index % 2) * 260, y: Math.floor(index / 2) * 105 },
    data: { label: <div className="node-label"><strong>{stage}</strong><Status value={latest.get(stage)?.status ?? "pending"}/></div> },
    style: { width: 210, background: "var(--surface)", borderColor: "var(--line)", color: "var(--text)" },
  }));
  const edges: Edge[] = stages.slice(1).map((stage, index) => ({ id: stage, source: stages[index], target: stage, animated: latest.get(stage)?.status === "running" }));
  const chart = (values: Record<string, number>) => Object.entries(values).slice(0, 24).map(([name, value]) => ({ name, value }));
  return <>
    <div className="detail-head"><div><h2>{run.dataset}</h2><p><code>{id.slice(0, 8)}</code> · Target {run.config.target} · {date(run.created)}</p></div><Status value={status}/></div>
    <div className="tabs" aria-label="Analysis sections">{["Agent Runs","EDA Explorer","Model Benchmarking","Model Evaluation","AI Insights","Reports"].map(name => <button key={name} aria-pressed={name === view || (name === "Agent Runs" && workflow)} onClick={() => setView(name)}>{name}</button>)}</div>
    {streamError && <div className="notice">Live event connection interrupted. Reconnecting…</div>}
    {workflow && <>
      <div className="workflow-grid">
        <Panel title="Agent workflow" caption="Select a stage to inspect its execution."><div className="flow"><ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.2 }} onNodeClick={(_, node) => setSelected(node.id)} nodesDraggable={false} nodesConnectable={false}><Background gap={18}/></ReactFlow></div></Panel>
        <Panel title={selected || "Execution details"} caption={selected ? "Recorded stage events" : "Most recent events"}>
          <div className="log">{(selected ? events.filter(event => event.stage === selected) : events.slice(-6)).map(event => <div key={event.id}><Status value={event.status}/><strong>{event.stage}</strong><time>{date(event.time)}</time>{event.detail && <p>{event.detail}</p>}</div>)}
          {!events.some(event => !selected || event.stage === selected) && <p className="muted">Waiting for stage events.</p>}</div>
        </Panel>
      </div>
      <Panel title="Execution timeline"><Table headers={["Sequence","Timestamp","Stage","Status","Details"]} rows={events.map(event => [event.id,date(event.time),event.stage,<Status key="status" value={event.status}/>,event.detail || "—"])}/></Panel>
    </>}
    {view === "EDA Explorer" && (result.eda ? <>
      <div className="subtabs">{["Overview","Distributions","Statistics","Missing values","Target analysis","Correlations"].map(name => <button className="button" aria-pressed={edaTab === name} key={name} onClick={() => setEdaTab(name)}>{name}</button>)}</div>
      {edaTab === "Distributions" && (profile?.error ? <ErrorNote message={profile.error}/> : profile?.data ? (() => {
        const distributions = { ...profile.data.histograms, ...profile.data.categorical };
        const selectedFeature = feature || Object.keys(distributions)[0];
        return <Panel title="Feature distribution" action={<select aria-label="Feature" value={selectedFeature} onChange={e => setFeature(e.target.value)}>{Object.keys(distributions).map(name => <option key={name}>{name}</option>)}</select>}><Bars label="Records" data={chart(distributions[selectedFeature] ?? {})}/></Panel>;
      })() : <Loading/>)}
      {edaTab === "Overview" && <Panel title="Exploratory summary"><dl className="facts padded"><dt>Numeric features</dt><dd>{Object.keys(result.eda.numeric_summary).length}</dd><dt>Target classes</dt><dd>{Object.keys(result.eda.target_distribution).length}</dd><dt>Missing cells</dt><dd>{Object.values(result.eda.missing_values).reduce((a,b) => a+b,0)}</dd><dt>Duplicate records</dt><dd>{profile?.data?.duplicates ?? "—"}</dd></dl></Panel>}
      {edaTab === "Statistics" && <Statistics values={result.eda.numeric_summary}/>}
      {edaTab === "Missing values" && <Panel title="Missing values by feature"><Bars label="Missing cells" data={chart(result.eda.missing_values)}/></Panel>}
      {edaTab === "Target analysis" && <Panel title="Target distribution"><Bars label="Records" data={chart(result.eda.target_distribution)}/></Panel>}
      {edaTab === "Correlations" && (profile?.error ? <ErrorNote message={profile.error}/> : profile?.data ? <Panel title="Pearson correlation" caption="Up to 24 numeric columns"><Table headers={["Feature",...Object.keys(profile.data.correlations)]} rows={Object.entries(profile.data.correlations).map(([name, values]) => [name,...Object.entries(values).map(([column, value]) => <span className="heat" key={column} style={{ background: value == null ? undefined : "color-mix(in srgb, var(--accent) " + (Math.abs(value) * 25) + "%, transparent)" }}>{value?.toFixed(2) ?? "—"}</span>)])}/></Panel> : <Loading/>)}
    </> : <Empty title="EDA results unavailable"/>)}
    {view === "Model Benchmarking" && (result.modeling ? <Panel title="Candidate performance" caption={"Selected by the modeling agent · " + modelName(result.modeling.best_model)}>
      <Table headers={["Candidate","Accuracy","Precision","Recall","F1","Training time"]} rows={Object.entries(result.modeling.model_comparison).sort((a,b) => b[1].f1 - a[1].f1).map(([name, metrics]) => [modelName(name),percent(metrics.accuracy),percent(metrics.precision),percent(metrics.recall),percent(metrics.f1),metrics.training_time_seconds?.toFixed(2) + " s"])}/>
      <Bars label="F1 score" data={Object.entries(result.modeling.model_comparison).map(([name, metrics]) => ({ name: modelName(name), value: metrics.f1 }))}/>
    </Panel> : <Empty title="Benchmark results unavailable"/>)}
    {view === "Model Evaluation" && (result.evaluation ? <Panel title="Evaluation verdict" caption="System score = 40% data quality + 60% model quality · threshold 0.70" action={<Status value={result.evaluation.verdict}/>}>
      <div className="form-fields">{Object.entries({ "Data quality": result.evaluation.data_quality_score, "Model quality": result.evaluation.model_quality_score, "System score": result.evaluation.system_score }).map(([name, score]) => <label key={name}>{name} · {percent(score)}<progress value={score} max={1}/></label>)}
        <p>{result.evaluation.verdict === "PASS" ? "System score meets the acceptance threshold." : "System score is below the acceptance threshold."}</p>
        {[...result.evaluation.issues,...result.evaluation.recommendations].map((line,index) => <p key={index}>{line}</p>)}</div>
    </Panel> : <Empty title="Evaluation unavailable"/>)}
    {["AI Insights","Reports"].includes(view) && <>
      <Panel title="Analysis report" caption={"Explanation " + (result.explanation_status ?? "pending")} action={run.report && <div className="actions">
        <button className="icon" aria-label="Copy report" onClick={async () => { try { await navigator.clipboard.writeText(run.report); setAction("Report copied."); } catch { setAction("Clipboard unavailable."); } }}><Copy size={16}/></button>
        <a className="button" href={"/api/analyses/" + id + "/report"}><Download size={15}/> Download</a>
        <button className="icon" aria-label="Print report" onClick={() => window.print()}><Printer size={16}/></button>
      </div>}>{run.report ? <article className="report">{run.report.split("\n\n").map((part,index) => part.startsWith("#") ? <h3 key={index}>{part.replace(/^#+\s*/, "")}</h3> : <p key={index}>{part}</p>)}</article> : <Empty title="Report unavailable"/>}</Panel>
      {view === "AI Insights" && <Panel title="Retrieved knowledge">{result.sources?.length ? <div className="form-fields">{result.sources.map((source,index) => <details key={index}><summary>{source.document || "Retrieved document"}{source.page == null ? "" : " · Page " + (source.page + 1)}</summary><p>{source.excerpt}</p></details>)}</div> : <Empty title="No retrieved sources available"/>}</Panel>}
      {view === "Reports" && <Panel title="Run artifacts">{assets?.error ? <ErrorNote message={assets.error}/> : assets?.data?.length ? <div className="toolbar">{assets.data.map(name => <a key={name} className="button" href={"/api/analyses/" + id + "/artifacts/" + name}><Download size={15}/>{name}</a>)}</div> : <Empty title="No artifacts available"/>}</Panel>}
      {view === "Reports" && ["completed","failed"].includes(status) && <button className="button danger" onClick={async () => {
        if (!window.confirm("Delete this run, report, and its artifacts?")) return;
        try { await api("analyses/" + id, { method: "DELETE" }); refresh(); exit(); } catch (cause) { setAction((cause as Error).message); }
      }}><Trash2 size={15}/> Delete analysis</button>}
      {action && <div className="notice" role="status">{action}</div>}
    </>}
    {!workflow && <button className="text-button" onClick={() => setView("Agent Runs")}>View execution <ArrowRight size={15}/></button>}
  </>;
}
