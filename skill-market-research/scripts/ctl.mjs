// Generic CDP controller: attach, run JS snippets passed as argv, with Network capture running.
// usage: node ctl.mjs "<js expression>" [--capture-ms=5000]
import { appendFileSync } from "node:fs";

const args = process.argv.slice(2);
const expr = args[0];
const captureMs = Number((args.find(a => a.startsWith("--capture-ms=")) ?? "--capture-ms=4000").split("=")[1]);
const outFile = "/tmp/wb-cdp/net-log.jsonl";

const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const page = list.find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
let seq = 0; const pending = new Map(); const captured = [];
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params }));
});
ws.addEventListener("message", async ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id); pending.delete(m.id);
    m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
    return;
  }
  if (m.method === "Network.responseReceived") {
    const r = m.params.response;
    if (r.url.startsWith("file:") || /\.(js|css|png|svg|woff2?|ico|jpg|webp|gif)(\?|$)/.test(r.url)) return;
    const isJson = (r.mimeType ?? "").includes("json");
    if (!isJson && !/skill|market|store|hub|recommend|category|search|list|explore/i.test(r.url)) return;
    try {
      const body = await send("Network.getResponseBody", { requestId: r.requestId });
      const text = body.base64Encoded ? Buffer.from(body.body, "base64").toString("utf8") : body.body;
      appendFileSync(outFile, JSON.stringify({ url: r.url, status: r.status, mime: r.mimeType, len: text.length, text: text.slice(0, 500_000) }) + "\n");
      captured.push(`${r.status} ${r.url.slice(0, 150)} len=${text.length}`);
    } catch (e) {
      captured.push(`NOBODY ${r.status} ${r.url.slice(0, 150)}`);
    }
  }
});
ws.addEventListener("open", async () => {
  await send("Network.enable", { maxTotalBufferSize: 200_000_000, maxResourceBufferSize: 50_000_000 });
  await send("Runtime.enable");
  await send("Page.enable");
  if (expr) {
    try {
      const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
      const v = r.result?.result;
      console.log("RESULT:", v?.value !== undefined ? JSON.stringify(v.value) : JSON.stringify(r).slice(0, 500));
      if (r.exceptionDetails) console.log("EXC:", JSON.stringify(r.exceptionDetails).slice(0, 500));
    } catch (e) { console.log("ERR:", String(e).slice(0, 300)); }
  }
  await new Promise(r => setTimeout(r, captureMs));
  console.log("--- captured", captured.length, "responses");
  for (const c of captured) console.log("  ", c);
  ws.close(); process.exit(0);
});
setTimeout(() => { console.error("hard timeout"); process.exit(1); }, captureMs + 15000);
