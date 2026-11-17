import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";

const root = fileURLToPath(new URL("../../", import.meta.url));
const frontend = fileURLToPath(new URL("../", import.meta.url));
const storage = await mkdtemp(join(tmpdir(), "aura-test-"));
const url = "http://127.0.0.1:3031";
const backendUrl = "http://127.0.0.1:8031";
const env = { ...process.env, AURA_STORAGE: storage, AURA_API_URL: backendUrl, GOOGLE_API_KEY: "", NEXT_TELEMETRY_DISABLED: "1" };
const servers = [
  spawn("python", ["-m", "uvicorn", "backend.api:app", "--port", "8031"], { cwd: root, env, stdio: "inherit" }),
  spawn(process.execPath, ["node_modules/next/dist/bin/next", "dev", "--hostname", "127.0.0.1", "--port", "3031"], { cwd: frontend, env, stdio: "inherit" }),
];
let browser;
try {
  for (let attempt = 0; ; attempt++) {
    const ready = await fetch(url + "/api/health").then(response => response.ok, () => false);
    if (ready) break;
    assert.ok(attempt < 60, "Workspace did not start");
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  browser = await chromium.launch({ channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.setDefaultTimeout(30000);
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(url);
  await page.getByRole("heading", { name: "Overview", exact: true }).waitFor();
  await page.getByRole("navigation").getByRole("button", { name: "Dataset Registry", exact: true }).click();
  const sample = "amount,group,label\n" + Array.from({ length: 60 }, (_, i) => `${i},${i < 30 ? "a" : "b"},${i < 30 ? 0 : 1}`).join("\n");
  await page.locator("input[type=file]").setInputFiles({ name: "browser-sample.csv", mimeType: "text/csv", buffer: Buffer.from(sample) });
  await page.getByRole("heading", { name: "browser-sample.csv" }).waitFor();
  await page.getByRole("button", { name: "Schema", exact: true }).click();
  await page.getByRole("cell", { name: "amount", exact: true }).waitFor();
  await page.getByRole("button", { name: "Data preview", exact: true }).click();
  await page.getByRole("cell", { name: "a", exact: true }).first().waitFor();
  await page.getByRole("button", { name: "Analyze dataset" }).click();
  await page.getByLabel("Target column").selectOption("label");
  await page.getByRole("button", { name: "Run analysis", exact: true }).click();
  await page.getByRole("heading", { name: "Execution timeline" }).waitFor();
  await page.getByRole("cell", { name: "Final report", exact: true }).first().waitFor();
  await page.locator(".detail-head .status").getByText("completed", { exact: true }).waitFor();
  await page.locator(".tabs").getByRole("button", { name: "EDA Explorer" }).click();
  await page.getByRole("heading", { name: "Exploratory summary" }).waitFor();
  await page.locator(".tabs").getByRole("button", { name: "Model Benchmarking" }).click();
  await page.getByRole("cell", { name: "Gradient Boosting", exact: true }).waitFor();
  await page.locator(".tabs").getByRole("button", { name: "Model Evaluation" }).click();
  await page.getByRole("heading", { name: "Evaluation verdict" }).waitFor();
  await page.locator(".tabs").getByRole("button", { name: "AI Insights" }).click();
  await page.getByRole("heading", { name: "Executive summary" }).waitFor();
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download", exact: true }).click();
  assert.match((await download).suggestedFilename(), /^analysis-.*\.md$/);
  await page.getByRole("navigation").getByRole("button", { name: "Analysis History" }).click();
  await page.getByRole("button", { name: "Open", exact: true }).click();
  await page.getByRole("heading", { name: "Execution timeline" }).waitFor();
  await page.setViewportSize({ width: 375, height: 812 });
  await page.reload();
  await page.getByRole("heading", { name: "Execution timeline" }).waitFor();
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), "Mobile page overflows");
  assert.deepEqual(errors, []);
  console.log("Browser workflow passed at 1440 px and 375 px.");
} finally {
  await browser?.close();
  for (const server of servers) server.kill();
  await Promise.all(servers.map(server => server.exitCode === null && server.signalCode === null
    ? new Promise(resolve => server.once("exit", resolve)) : Promise.resolve()));
  await rm(storage, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
}
