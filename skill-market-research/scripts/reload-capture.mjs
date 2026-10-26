// Reload the page and capture ALL skillhub API requests+responses from boot.
import { writeFileSync } from "node:fs";
const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const page = list.find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
let seq = 0; const pending = new Map(); const reqs = new Map(); const bodies = [];
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
  if (m.method === "Network.requestWillBeSent") {
    const r = m.params.request;
    if (/skillhub\.cn/.test(r.url)) {
      reqs.set(m.params.requestId, r);
      console.log("REQ", r.method, r.url);
      if (r.postData) console.log("  body:", r.postData.slice(0, 500));
      console.log("  hdrs:", JSON.stringify(r.headers).slice(0, 900));
    }
  }
  if (m.method === "Network.responseReceived" && /skillhub\.cn/.test(m.params.response.url)) {
    const rid = m.params.requestId;
    try {
      const body = await send("Network.getResponseBody", { requestId: rid });
      const text = body.base64Encoded ? Buffer.from(body.body, "base64").toString("utf8") : body.body;
      bodies.push({ url: m.params.response.url, status: m.params.response.status, len: text.length });
      writeFileSync(`/tmp/wb-cdp/resp_${bodies.length}.json`, text);
      console.log("RESP", m.params.response.status, m.params.response.url.slice(0, 120), "len=" + text.length, "-> saved resp_" + bodies.length + ".json");
    } catch (e) { console.log("RESP-NOBODY", m.params.response.url.slice(0, 120)); }
  }
});
ws.addEventListener("open", async () => {
  await send("Network.enable", { maxTotalBufferSize: 500_000_000, maxResourceBufferSize: 100_000_000 });
  await send("Page.enable");
  await send("Page.reload", { ignoreCache: true });
  console.log("reloaded, waiting...");
  await new Promise(r => setTimeout(r, 18000));
  console.log("done, responses:", bodies.length);
  ws.close(); process.exit(0);
});
setTimeout(() => { console.error("hard timeout"); process.exit(1); }, 40000);
