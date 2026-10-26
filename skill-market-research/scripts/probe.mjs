// Attach to WorkBuddy main window via CDP, enable Network, log candidate API responses.
import { writeFileSync, appendFileSync } from "node:fs";

const targetId = process.argv[2];
const listenMs = Number(process.argv[3] ?? 20000);
const outFile = "/tmp/wb-cdp/net-log.jsonl";

const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const page = list.find(t => t.type === "page" && (!targetId || t.id === targetId));
if (!page) { console.error("no page target"); process.exit(1); }

const ws = new WebSocket(page.webSocketDebuggerUrl);
let seq = 0;
const pending = new Map();

function send(method, params = {}, sessionId) {
  const id = ++seq;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
  });
}

const interesting = /skill|market|store|plugin|recommend|list|search|category|open|explore|hub/i;
const seen = new Set();

ws.addEventListener("open", async () => {
  await send("Network.enable", { maxTotalBufferSize: 100_000_000, maxResourceBufferSize: 20_000_000 });
  await send("Runtime.enable");
  console.log("attached:", page.url.slice(0, 80));
  // Poke the UI a bit: run a tiny probe of the page's runtime to see what's there.
  const r = await send("Runtime.evaluate", { expression: "location.href + ' | ' + document.title", returnByValue: true });
  console.log("page:", r?.result?.result?.value);
});

ws.addEventListener("message", async ev => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    return;
  }
  if (msg.method === "Network.responseReceived") {
    const { response } = msg.params;
    const url = response.url;
    if (url.startsWith("file:") || /\.(js|css|png|svg|woff2?|ico|jpg|webp)(\?|$)/.test(url)) return;
    const key = response.requestId;
    if (seen.has(key)) return;
    seen.add(key);
    const isJson = (response.mimeType ?? "").includes("json");
    if (!isJson && !interesting.test(url)) return;
    try {
      const body = await send("Network.getResponseBody", { requestId: key });
      const text = body.base64Encoded ? Buffer.from(body.body, "base64").toString("utf8") : body.body;
      appendFileSync(outFile, JSON.stringify({ url, status: response.status, mime: response.mimeType, len: text.length, text: text.slice(0, 200_000) }) + "\n");
      console.log("CAPTURED", response.status, url.slice(0, 140), "len=" + text.length);
    } catch (e) {
      appendFileSync(outFile, JSON.stringify({ url, status: response.status, mime: response.mimeType, error: String(e) }) + "\n");
      console.log("NO-BODY", response.status, url.slice(0, 140));
    }
  }
});

setTimeout(async () => {
  try { ws.close(); } catch {}
  process.exit(0);
}, listenMs);
