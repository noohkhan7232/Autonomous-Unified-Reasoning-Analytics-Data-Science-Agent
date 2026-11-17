import asyncio
import json
import logging
import math
import os
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote
from uuid import UUID, uuid4

import matplotlib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

matplotlib.use("Agg")
load_dotenv()
ROOT = Path(os.getenv("AURA_STORAGE", "output/workspace")).resolve()
LIMIT = 20 * 1024 * 1024
ARTIFACTS = {"target_distribution.png", "best_model.pkl"}
log = logging.getLogger(__name__)


@contextmanager
def database():
    db = sqlite3.connect(ROOT / "workspace.sqlite3", timeout=20)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()


def now():
    return datetime.now(timezone.utc).isoformat()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if hasattr(value, "item"):
        return clean(value.item())
    return value


def encode(value):
    return json.dumps(clean(value), allow_nan=False)


def lookup(table, key):
    with database() as db:
        row = db.execute(f"SELECT * FROM {table} WHERE id=?", (str(key),)).fetchone()
    if row is None:
        raise HTTPException(404, "Record not found.")
    result = dict(row)
    for field in ("config", "results", "schema"):
        if field in result:
            result[field] = json.loads(result[field])
    return result


def event(db, run, stage, status, detail=""):
    db.execute(
        "INSERT INTO events(run, stage, status, detail, time) VALUES (?,?,?,?,?)",
        (run, stage, status, detail, now()),
    )


@asynccontextmanager
async def lifespan(app):
    ROOT.mkdir(parents=True, exist_ok=True)
    with database() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS datasets (
          id TEXT PRIMARY KEY, name TEXT, size INTEGER, rows INTEGER,
          columns INTEGER, created TEXT, schema TEXT
        );
        CREATE TABLE IF NOT EXISTS runs (
          id TEXT PRIMARY KEY, dataset_id TEXT, dataset TEXT, created TEXT,
          status TEXT, config TEXT, results TEXT, report TEXT
        );
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, run TEXT, stage TEXT,
          status TEXT, detail TEXT, time TEXT
        );
        CREATE INDEX IF NOT EXISTS run_events ON events(run, id);
        """)
        for row in db.execute("SELECT id FROM runs WHERE status IN ('queued','running')"):
            event(db, row["id"], "Execution", "failed", "Worker restarted.")
        db.execute("UPDATE runs SET status='failed' WHERE status IN ('queued','running')")
    app.state.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="aura-analysis")
    app.state.submission_lock = threading.Lock()
    yield
    app.state.worker.shutdown(wait=True)


app = FastAPI(title="AURA-DS", lifespan=lifespan)


def dataframe(key):
    return pd.read_csv(ROOT / f"{key}.csv")


@app.post("/api/datasets/upload", status_code=201)
async def upload(request: Request):
    name = unquote(request.headers.get("x-filename", "")).replace("\\", "/").split("/")[-1]
    if not name.lower().endswith(".csv") or len(name) > 255:
        raise HTTPException(422, "Select a CSV file with a valid filename.")
    key = str(uuid4())
    path = ROOT / f"{key}.csv"
    size = 0
    try:
        with path.open("xb") as target:
            async for chunk in request.stream():
                size += len(chunk)
                if size > LIMIT:
                    raise HTTPException(413, "CSV files must be 20 MB or smaller.")
                target.write(chunk)
        return await asyncio.to_thread(register, key, name, size)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def register(key, name, size):
    try:
        frame = dataframe(key)
    except (ValueError, UnicodeError) as exc:
        raise HTTPException(422, "The file is not a readable UTF-8 CSV.") from exc
    if frame.empty or len(frame.columns) < 2:
        raise HTTPException(422, "CSV must contain data and at least two columns.")
    schema = [
        dict(name=column, dtype=str(series.dtype), missing=int(series.isna().sum()),
             unique=int(series.nunique()), examples=json.loads(series.dropna().head(3).to_json(orient="values")))
        for column, series in frame.items()
    ]
    with database() as db:
        db.execute("INSERT INTO datasets VALUES (?,?,?,?,?,?,?)",
                   (key, name, size, len(frame), len(frame.columns), now(), encode(schema)))
    return lookup("datasets", key)


@app.get("/api/datasets")
def datasets():
    with database() as db:
        return [dict(row) for row in db.execute("""
          SELECT id,name,size,rows,columns,created,
          (SELECT MAX(created) FROM runs WHERE dataset_id=datasets.id) AS last_analyzed
          FROM datasets ORDER BY created DESC
        """)]


@app.get("/api/datasets/{key}")
def dataset(key: UUID):
    return lookup("datasets", key)


@app.get("/api/datasets/{key}/profile")
def profile(key: UUID):
    lookup("datasets", key)
    frame = dataframe(key)
    numeric = frame.select_dtypes(include="number")
    categorical = frame.select_dtypes(exclude="number")
    return clean(dict(
        memory=int(frame.memory_usage(deep=True).sum()), duplicates=int(frame.duplicated().sum()),
        missing=int(frame.isna().sum().sum()),
        numeric={name: series.describe().to_dict() for name, series in numeric.items()},
        histograms={
            name: {str(interval): int(count) for interval, count in
                   series.replace([math.inf, -math.inf], float("nan")).dropna()
                   .value_counts(bins=12, sort=False).items()}
            for name, series in numeric.iloc[:, :24].items()
            if series.replace([math.inf, -math.inf], float("nan")).notna().any()
        },
        categorical={name: series.value_counts().head(10).to_dict() for name, series in categorical.items()},
        correlations=numeric.iloc[:, :24].corr().to_dict(),
    ))


@app.get("/api/datasets/{key}/preview")
def preview(key: UUID, offset: int = 0, limit: int = 20, search: str = "", sort: str = "", descending: bool = False):
    lookup("datasets", key)
    frame = dataframe(key)
    if search:
        mask = frame.astype(str).apply(lambda column: column.str.contains(search, case=False, regex=False))
        frame = frame.loc[mask.any(axis=1)]
    if sort in frame.columns:
        frame = frame.sort_values(sort, ascending=not descending, kind="stable")
    start = max(offset, 0)
    return {"total": len(frame), "rows": json.loads(frame.iloc[start:start + min(max(limit, 1), 100)].to_json(orient="values"))}


class AnalysisConfig(BaseModel):
    dataset_id: UUID
    target: str = Field(min_length=1)
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    random_state: int = Field(default=42, ge=0, le=4294967295)


@app.post("/api/analyses", status_code=202)
def create_analysis(config: AnalysisConfig, request: Request):
    data = lookup("datasets", config.dataset_id)
    frame = dataframe(config.dataset_id)
    if config.target not in frame:
        raise HTTPException(422, "Select a target from this dataset.")
    counts = frame[config.target].value_counts()
    test_rows = math.ceil(len(frame) * config.test_size)
    if (frame[config.target].isna().any() or not 2 <= len(counts) <= 50
            or counts.min() < 2 or min(test_rows, len(frame) - test_rows) < len(counts)):
        raise HTTPException(422, "Classification needs 2–50 classes, no missing targets, and enough samples per class for the selected split.")
    run = str(uuid4())
    payload = config.model_dump(mode="json")
    with request.app.state.submission_lock:
        with database() as db:
            db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?)",
                       (run, data["id"], data["name"], now(), "queued", encode(payload), "{}", ""))
            event(db, run, "Execution", "queued", "Analysis created.")
            event(db, run, "Dataset validation", "completed", "Classification target and split validated.")
        request.app.state.worker.submit(execute, run, payload)
    return {"id": run}


def execute(run, config):
    results = {}
    folder = ROOT / run
    path = str(ROOT / f'{config["dataset_id"]}.csv')
    target = config["target"]
    report = ""

    def stage(name, action, result_key=None):
        with database() as db:
            event(db, run, name, "running")
        try:
            value = action()
            if result_key:
                results[result_key] = value
        except Exception:
            with database() as db:
                event(db, run, name, "failed", f"{name} failed. See server logs for details.")
            raise
        with database() as db:
            db.execute("UPDATE runs SET results=? WHERE id=?", (encode(results), run))
            event(db, run, name, "completed")
        return value

    try:
        from agents.evaluation_agent import EvaluationAgent
        from agents.exploratory_analysis_agent import EDAAgent
        from agents.modeling_agent import ModelingAgent
        from agents.planning_agent import PlannerAgent

        with database() as db:
            db.execute("UPDATE runs SET status='running' WHERE id=?", (run,))
        stage("Planning", lambda: PlannerAgent().run(path, target, "classification"), "plan")
        stage("Exploratory data analysis", lambda: EDAAgent().run(path, target, str(folder))["eda_summary"], "eda")

        def benchmark(impute=False):
            agent = ModelingAgent()
            agent.random_state = config["random_state"]
            result = agent.run(path, target, "classification", test_size=config["test_size"],
                               model_dir=str(folder), impute=impute)
            result.pop("model_artifact_path")
            return result

        has_missing = any(count for name, count in results["eda"]["missing_values"].items() if name != target)
        corrected = False
        try:
            stage("Modeling", benchmark, "modeling")
        except ValueError:
            if not has_missing:
                raise
            with database() as db:
                event(db, run, "Self-correction", "retrying", "Fit preprocessing with training-set imputation.")
            stage("Self-correction", lambda: benchmark(impute=True), "modeling")
            corrected = True

        def evaluate():
            return EvaluationAgent().run(dict(
                eda_summary=results["eda"], model_metrics=results["modeling"]["model_metrics"],
                task_type="classification", target_column=target,
            ))

        stage("Evaluation", evaluate, "evaluation")
        stage("Decision routing", lambda: results["evaluation"]["verdict"])
        if not corrected and results["evaluation"]["requires_retraining"] and has_missing:
            results["first_evaluation"] = results["evaluation"]
            with database() as db:
                event(db, run, "Self-correction", "retrying", "Fit preprocessing with training-set imputation.")
            stage("Self-correction", lambda: benchmark(impute=True), "modeling")
            stage("Evaluation", evaluate, "evaluation")
        elif not corrected:
            with database() as db:
                event(db, run, "Self-correction", "skipped", "No missing-data correction was triggered.")
        try:
            def explain():
                from agents.explanation_agent import ExplanationAgent
                agent = ExplanationAgent(model=os.getenv("AURA_GEMINI_MODEL", "gemini-2.5-flash"))
                explanation = agent.run(results["eda"], results["modeling"]["model_metrics"], "classification", target)
                results["sources"] = agent.sources
                return explanation

            explanation = stage("Explanation", explain)
            results["explanation_status"] = "generated"
        except Exception:
            log.exception("Explanation failed for run %s", run)
            explanation = "AI explanation unavailable. The measured results are recorded below."
            results["explanation_status"] = "unavailable"
        evaluation = results["evaluation"]
        metrics = results["modeling"]["model_metrics"]
        dataset = results["plan"]["dataset_summary"]
        findings = "\n".join(f"- {issue}" for issue in evaluation["issues"]) or "No issues flagged by the evaluator."
        recommendations = "\n".join(f"- {item}" for item in evaluation["recommendations"]) or "No automatic recommendations."
        report = stage("Final report", lambda: (
            f'# Executive summary\n\nClassification of {target}. Verdict: {evaluation["verdict"]}. '
            f'System score: {evaluation["system_score"]:.3f}.\n\n'
            f'## Dataset analysis\n\n{dataset["num_rows"]:,} rows and {dataset["num_columns"]:,} columns. '
            f'Held-out test split: {config["test_size"]:.0%}.\n\n'
            f'## Data quality findings\n\n{findings}\n\n'
            f'## Model performance\n\nBest model: {results["modeling"]["best_model"]}. '
            f'Accuracy: {metrics["accuracy"]:.1%}. Weighted F1: {metrics["f1"]:.1%}.\n\n'
            f'## Evaluation\n\nData quality: {evaluation["data_quality_score"]:.3f}. '
            f'Model quality: {evaluation["model_quality_score"]:.3f}. Pass threshold: 0.70.\n\n'
            f'## Knowledge-grounded explanation\n\n{explanation}\n\n'
            f'## Recommendations\n\n{recommendations}'
        ))
        status = "completed"
    except Exception:
        log.exception("Analysis failed for run %s", run)
        status = "failed"
    with database() as db:
        db.execute("UPDATE runs SET results=?,report=?,status=? WHERE id=?", (encode(results), report, status, run))
        event(db, run, "Execution", status)


@app.get("/api/analyses")
def analyses():
    with database() as db:
        return [dict(row) for row in db.execute("""
          SELECT id,dataset_id,dataset,created,status,
          json_extract(results,'$.modeling.best_model') AS model,
          json_extract(results,'$.evaluation.system_score') AS score,
          json_extract(results,'$.evaluation.verdict') AS verdict
          FROM runs ORDER BY created DESC
        """)]


@app.get("/api/analyses/{key}")
def analysis(key: UUID):
    return lookup("runs", key)


@app.get("/api/analyses/{key}/results")
def results(key: UUID):
    return lookup("runs", key)["results"]


@app.get("/api/analyses/{key}/report", response_class=PlainTextResponse)
def report(key: UUID):
    content = lookup("runs", key)["report"]
    if not content:
        raise HTTPException(404, "Report is unavailable.")
    return PlainTextResponse(content, headers={"Content-Disposition": f'attachment; filename="analysis-{key}.md"'})


@app.get("/api/analyses/{key}/artifacts")
def artifacts(key: UUID):
    lookup("runs", key)
    return sorted(name for name in ARTIFACTS if (ROOT / str(key) / name).is_file())


@app.get("/api/analyses/{key}/artifacts/{name}")
def artifact(key: UUID, name: str):
    lookup("runs", key)
    path = ROOT / str(key) / name
    if name not in ARTIFACTS or not path.is_file():
        raise HTTPException(404, "Artifact unavailable.")
    return FileResponse(path, filename=name)


@app.delete("/api/analyses/{key}", status_code=204)
def delete(key: UUID):
    row = lookup("runs", key)
    if row["status"] in ("running", "queued"):
        raise HTTPException(409, "An active run cannot be deleted.")
    with database() as db:
        db.execute("DELETE FROM events WHERE run=?", (str(key),))
        db.execute("DELETE FROM runs WHERE id=?", (str(key),))
    folder = ROOT / str(key)
    if folder.exists():
        for name in ARTIFACTS:
            (folder / name).unlink(missing_ok=True)
        folder.rmdir()


@app.get("/api/analyses/{key}/events")
async def events(key: UUID, request: Request):
    lookup("runs", key)
    try:
        cursor = max(0, int(request.headers.get("last-event-id", "0")))
    except ValueError:
        cursor = 0

    async def stream():
        last = cursor
        while not await request.is_disconnected():
            with database() as db:
                records = db.execute("SELECT * FROM events WHERE run=? AND id>? ORDER BY id", (str(key), last)).fetchall()
                run = db.execute("SELECT status FROM runs WHERE id=?", (str(key),)).fetchone()
            for row in records:
                last = row["id"]
                yield f"id: {last}\ndata: {encode(dict(row))}\n\n"
            if run is None or (run["status"] in ("completed", "failed") and not records):
                yield "event: end\ndata: {}\n\n"
                return
            await asyncio.sleep(0.5)
            yield ": heartbeat\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/health")
def health(request: Request):
    with database() as db:
        db.execute("SELECT 1").fetchone()
    return {
        "API": "Online", "SQLite": "Reachable", "Analysis worker": "Initialized",
        "Gemini": "Configured · connectivity unverified" if os.getenv("GOOGLE_API_KEY") else "Unconfigured",
        "Knowledge store": "Checked during explanation",
        "Artifact storage": "Writable" if os.access(ROOT, os.W_OK) else "Unavailable",
    }
