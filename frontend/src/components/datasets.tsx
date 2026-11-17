"use client";

import { useRef, useState } from "react";
import { ArrowDownUp, Database, UploadCloud } from "lucide-react";
import { date, type Dataset, type Preview, type Profile } from "./api";
import { Bars, Empty, ErrorNote, Loading, Pagination, Panel, RunTable, Table, useResource } from "./ui";
import type { Run } from "./api";

export function Registry({ datasets, open, refresh }: { datasets: Dataset[]; open: (id: string) => void; refresh: () => void }) {
  const input = useRef<HTMLInputElement>(null);
  const upload = useRef<XMLHttpRequest | null>(null);
  const [progress, setProgress] = useState<number>();
  const [message, setMessage] = useState("");
  const [query, setQuery] = useState("");
  const [drag, setDrag] = useState(false);
  function submit(file?: File) {
    if (!file || upload.current) return;
    setMessage("");
    if (!file.name.toLowerCase().endsWith(".csv") || file.size > 20 * 1024 * 1024) {
      setMessage("Select a CSV file up to 20 MB."); return;
    }
    const request = new XMLHttpRequest();
    upload.current = request;
    setProgress(0);
    request.open("POST", "/api/datasets/upload");
    request.setRequestHeader("X-Filename", encodeURIComponent(file.name));
    request.upload.onprogress = event => { if (event.lengthComputable) setProgress(Math.round(event.loaded / event.total * 100)); };
    request.onload = () => {
      let body;
      try { body = JSON.parse(request.responseText); } catch {}
      if (request.status === 201) { refresh(); open(body.id); }
      else setMessage(typeof body?.detail === "string" ? body.detail : "Upload failed.");
    };
    request.onerror = () => setMessage("The upload could not reach the API.");
    request.onabort = () => setMessage("Upload canceled.");
    request.onloadend = () => { upload.current = null; setProgress(undefined); };
    request.send(file);
  }
  const filtered = datasets.filter(data => data.name.toLowerCase().includes(query.toLowerCase()));
  return <>
    <section className={"dropzone " + (drag ? "drag" : "")} onDragOver={event => { event.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)} onDrop={event => { event.preventDefault(); setDrag(false); submit(event.dataTransfer.files[0]); }}>
      <div className="empty-icon"><UploadCloud size={20}/></div>
      <div><strong>Upload a dataset</strong><p>Drop a CSV file here or browse your device. Maximum 20 MB.</p></div>
      <input ref={input} type="file" accept=".csv" hidden onChange={event => { submit(event.target.files?.[0]); event.target.value = ""; }}/>
      {progress === undefined ? <button className="button primary" onClick={() => input.current?.click()}>Choose CSV</button> : <><progress value={progress} max={100} aria-label="Upload progress"/><button className="button" onClick={() => upload.current?.abort()}>Cancel</button></>}
    </section>
    {message && <ErrorNote message={message}/>}
    <Panel title="Registered datasets" caption={datasets.length + " datasets in this workspace"} action={<input aria-label="Filter datasets" placeholder="Filter datasets…" value={query} onChange={event => setQuery(event.target.value)}/>}>
      {filtered.length ? <Table headers={["Dataset","Type","Rows","Columns","Size","Uploaded","Last analyzed",""]} rows={filtered.map(data => [
        <span className="table-name" key="name"><Database size={15}/>{data.name}</span>, "CSV", data.rows.toLocaleString(), data.columns, (data.size / 1024).toFixed(1) + " KB", date(data.created), date(data.last_analyzed), <button className="text-button" key="open" onClick={() => open(data.id)}>Inspect</button>,
      ])}/> : <Empty title={datasets.length ? "No matching datasets" : "No datasets registered"}/>}
    </Panel>
  </>;
}

export function DatasetDetail({ id, runs, openRun, create }: { id: string; runs: Run[]; openRun: (id: string) => void; create: () => void }) {
  const [tab, setTab] = useState("Overview");
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState("");
  const [hidden, setHidden] = useState<string[]>([]);
  const [sort, setSort] = useState("");
  const [descending, setDescending] = useState(false);
  const data = useResource<Dataset>("datasets/" + id);
  const profile = useResource<Profile>(["Overview","Profiling","Data quality"].includes(tab) ? "datasets/" + id + "/profile" : null);
  const params = new URLSearchParams({ offset: String(page * 20), search, sort, descending: String(descending) });
  const preview = useResource<Preview>(tab === "Data preview" ? "datasets/" + id + "/preview?" + params : null);
  if (data?.error) return <ErrorNote message={data.error}/>;
  if (!data?.data) return <Loading/>;
  const dataset = data.data;
  const schema = dataset.schema ?? [];
  const visible = schema.map((column, index) => ({ ...column, index })).filter(column => !hidden.includes(column.name));
  return <>
    <div className="detail-head"><div className="empty-icon"><Database size={20}/></div><div><h2>{dataset.name}</h2><p>{dataset.rows.toLocaleString()} rows · {dataset.columns} columns · CSV</p></div><button className="button primary" onClick={create}>Analyze dataset</button></div>
    <div className="tabs" aria-label="Dataset sections">{["Overview","Data preview","Schema","Profiling","Data quality","Analysis history"].map(name => <button key={name} aria-pressed={name === tab} onClick={() => setTab(name)}>{name}</button>)}</div>
    {tab === "Schema" && <Panel title="Schema"><Table headers={["Column","Type","Missing","Distinct","Examples"]} rows={schema.map(column => [column.name,column.dtype,column.missing,column.unique,column.examples.map(String).join(", ")])}/></Panel>}
    {tab === "Data preview" && <Panel title="Data preview"><div className="toolbar">
      <input value={search} placeholder="Search cells…" aria-label="Search cells" onChange={event => { setSearch(event.target.value); setPage(0); }}/>
      <details className="column-picker"><summary>Columns</summary><div>{schema.map(column => <label key={column.name}><input type="checkbox" checked={!hidden.includes(column.name)} onChange={() => setHidden(items => items.includes(column.name) ? items.filter(item => item !== column.name) : [...items, column.name])}/>{column.name}</label>)}</div></details>
    </div>{preview?.error ? <ErrorNote message={preview.error}/> : preview?.data ? <>
      <Table headers={visible.map(column => <button className="text-button" key={column.name} onClick={() => { setDescending(sort === column.name && !descending); setSort(column.name); setPage(0); }}>{column.name}<ArrowDownUp size={12}/></button>)} rows={preview.data.rows.map(row => visible.map(column => String(row[column.index] ?? "—")))}/>
      <Pagination page={page} total={preview.data.total} size={20} setPage={setPage}/>
    </> : <Loading/>}</Panel>}
    {tab === "Analysis history" && <Panel title="Dataset runs"><RunTable runs={runs.filter(run => run.dataset_id === id)} open={openRun} create={create}/></Panel>}
    {["Overview","Profiling","Data quality"].includes(tab) && (profile?.error ? <ErrorNote message={profile.error}/> : profile?.data ? <>
      {tab === "Overview" && <div className="metric-grid">{Object.entries({ Rows: dataset.rows, Features: dataset.columns, Missing: profile.data.missing, Duplicates: profile.data.duplicates, "Memory (KB)": Math.round(profile.data.memory / 1024) }).map(([label,value]) => <div className="metric" key={label}><span>{label}</span><strong>{value.toLocaleString()}</strong></div>)}</div>}
      {tab !== "Profiling" && <Panel title="Missing values by feature"><Bars label="Missing values" data={schema.slice(0, 24).map(column => ({ name: column.name, value: column.missing }))}/></Panel>}
      {tab === "Profiling" && <><Statistics values={profile.data.numeric}/><Panel title="Categorical frequency"><Table headers={["Feature","Most frequent values"]} rows={Object.entries(profile.data.categorical).map(([name, counts]) => [name,Object.entries(counts).map(([value,count]) => value + " (" + count + ")").join(" · ")])}/></Panel></>}
    </> : <Loading/>)}
  </>;
}

export function Statistics({ values }: { values: Profile["numeric"] }) {
  const fields = ["count","mean","std","min","25%","50%","75%","max"];
  return <Panel title="Numeric statistics">{Object.keys(values).length ? <Table headers={["Feature",...fields]} rows={Object.entries(values).map(([name, stats]) => [name,...fields.map(field => stats[field]?.toLocaleString(undefined, { maximumFractionDigits: 3 }) ?? "—")])}/> : <Empty title="No numeric features"/>}</Panel>;
}
