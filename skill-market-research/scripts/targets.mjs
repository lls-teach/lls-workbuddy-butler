// Connect to browser-level CDP and enumerate all targets (incl. webviews/iframes).
const ver = await (await fetch("http://127.0.0.1:9222/json/version")).json();
const ws = new WebSocket(ver.webSocketDebuggerUrl);
let seq = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params }));
});
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id); pending.delete(m.id);
    m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
  }
});
ws.addEventListener("open", async () => {
  const { targetInfos } = await send("Target.getTargets");
  for (const t of targetInfos) {
    console.log([t.type, t.targetId, (t.title || "").slice(0, 40), (t.url || "").slice(0, 110)].join(" | "));
  }
  ws.close(); process.exit(0);
});
setTimeout(() => { console.error("timeout"); process.exit(1); }, 8000);
