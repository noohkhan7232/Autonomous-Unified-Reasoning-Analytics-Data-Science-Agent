"use client";

import { useEffect, useState } from "react";
import { ArrowDownUp, ChevronLeft, ChevronRight, Inbox, Search } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, date, modelName, percent, type Run } from "./api";

export function useResource<T>(path: string | null, revision = 0) {
  const [state, setState] = useState<{ path: string; data?: T; error?: string }>();
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    api<T>(path, { signal: controller.signal })
      .then(data => setState({ path, data }))
      .catch(error => { if (!controller.signal.aborted) setState({ path, error: error.message }); });
    return () => controller.abort();
  }, [path, revision]);
  return state?.path === path ? state : undefined;
}

export function Status({ value }: { value: string }) {
  return <span className={"status " + value.toLowerCase()}><i />{value}</span>;
}

export function Empty({ title, detail, action }: { title: string; detail?: string; action?: React.ReactNode }) {
  return <div className="empty"><div className="empty-icon"><Inbox size={20} /></div><strong>{title}</strong>{detail && <p>{detail}</p>}{action}</div>;
}

export function Loading() {
  return <div className="skeleton" role="status" aria-label="Loading"><i /><i /><i /></div>;
}

export function ErrorNote({ message }: { message: string }) {
  return <div className="error" role="alert">{message}</div>;
}

export function Panel({ title, caption, action, children }: { title: string; caption?: string; action?: React.ReactNode; children: React.ReactNode }) {
  return <section className="panel"><div className="panel-head"><div><h2>{title}</h2>{caption && <p>{caption}</p>}</div>{action}</div>{children}</section>;
}

export function Table({ headers, rows }: { headers: React.ReactNode[]; rows: React.ReactNode[][] }) {
  return <div className="table-scroll" tabIndex={0} aria-label="Scrollable data table"><table><thead><tr>{headers.map((header, index) => <th key={index} scope="col">{header}</th>)}</tr></thead><tbody>{rows.map((cells, index) => <tr key={index}>{cells.map((cell, column) => <td key={column}>{cell}</td>)}</tr>)}</tbody></table></div>;
}

export function Pagination({ page, total, size, setPage }: { page: number; total: number; size: number; setPage: (value: number) => void }) {
  return <div className="pagination"><span>{total ? page * size + 1 : 0}–{Math.min((page + 1) * size, total)} of {total}</span><div>
    <button className="icon" aria-label="Previous page" disabled={page === 0} onClick={() => setPage(page - 1)}><ChevronLeft size={16}/></button>
    <button className="icon" aria-label="Next page" disabled={(page + 1) * size >= total} onClick={() => setPage(page + 1)}><ChevronRight size={16}/></button>
  </div></div>;
}

export function RunTable({ runs, open, create }: { runs: Run[]; open: (id: string) => void; create: () => void }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("");
  const [since, setSince] = useState("");
  const [order, setOrder] = useState(false);
  const [page, setPage] = useState(0);
  const filtered = runs.filter(run => (!status || run.status === status || run.verdict === status)
    && (!since || run.created.slice(0, 10) >= since) && (run.dataset + run.id).toLowerCase().includes(query.toLowerCase()));
  if (order) filtered.reverse();
  const current = Math.min(page, Math.max(0, Math.ceil(filtered.length / 7) - 1));
  if (!runs.length) return <Empty title="No analysis runs yet" detail="Start an analysis to see the workflow and results here." action={<button className="button" onClick={create}>New analysis</button>} />;
  return <><div className="toolbar"><label className="search"><Search size={15}/><input aria-label="Filter runs" placeholder="Search runs…" value={query} onChange={e => { setPage(0); setQuery(e.target.value); }}/></label>
    <select aria-label="Run status" value={status} onChange={e => { setPage(0); setStatus(e.target.value); }}><option value="">All statuses</option>{["completed","failed","running","queued","PASS","FAIL"].map(s => <option key={s}>{s}</option>)}</select>
    <input aria-label="Created on or after" type="date" value={since} onChange={e => { setPage(0); setSince(e.target.value); }}/>
  </div>{filtered.length ? <Table headers={["Run ID","Dataset","Task","Best model","System score","Status",<button className="text-button" key="time" onClick={() => setOrder(!order)}>Created <ArrowDownUp size={12}/></button>,""]} rows={filtered.slice(current * 7, current * 7 + 7).map(run => [
    <code key="id">{run.id.slice(0, 8)}</code>, run.dataset, "Classification", run.model ? modelName(run.model) : "—", percent(run.score), <Status key="status" value={run.verdict ?? run.status}/>, date(run.created), <button className="text-button" key="open" onClick={() => open(run.id)}>Open</button>,
  ])}/> : <Empty title="No matching runs"/>}<Pagination page={current} total={filtered.length} size={7} setPage={setPage}/></>;
}

export function Bars({ data, label }: { data: { name: string; value: number }[]; label: string }) {
  if (!data.length) return <Empty title="No data to chart"/>;
  return <div className="chart" role="img" aria-label={label}><ResponsiveContainer width="100%" height="100%">
    <BarChart data={data} margin={{ left: 0, right: 18, top: 10, bottom: 0 }}>
      <CartesianGrid vertical={false} stroke="var(--line)" strokeDasharray="3 4"/>
      <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "var(--muted)", fontSize: 11 }} />
      <YAxis width={37} tickLine={false} axisLine={false} tick={{ fill: "var(--muted)", fontSize: 11 }} />
      <Tooltip cursor={{ fill: "var(--subtle)" }} contentStyle={{ background: "var(--surface)", borderColor: "var(--line)", borderRadius: 6, color: "var(--text)" }}/>
      <Bar dataKey="value" name={label} fill="var(--accent)" radius={[4,4,0,0]} maxBarSize={36}/>
    </BarChart>
  </ResponsiveContainer></div>;
}

