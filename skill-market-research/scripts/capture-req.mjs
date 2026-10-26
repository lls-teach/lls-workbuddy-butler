// Capture live requests to api.skillhub.cn while clicking a category tab.
const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const page = list.find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
let seq = 0; const pending = new Map(); const reqs = [];
const send = (method, params = {}) => new Promise((res, rej) => {
  const id = ++seq; pending.set(id, { res, rej });
  ws.send(JSON.stringify({ id, method, params }));
});
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) {
    const { res, rej } = pending.get(m.id); pending.delete(m.id);
    m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
    return;
  }
  if (m.method === "Network.requestWillBeSent" && /skillhub|skill/i.test(m.params.request.url) && !m.params.request.url.startsWith("file:")) {
    const r = m.params.request;
    reqs.push(r);
    console.log("REQ", r.method, r.url);
    console.log("  headers:", JSON.stringify(r.headers).slice(0, 800));
    if (r.postData) console.log("  body:", r.postData.slice(0, 600));
  }
});
ws.addEventListener("open", async () => {
  await send("Network.enable");
  await send("Runtime.enable");
  // click the "开发工具" category tab to force a list refresh
  const clickExpr = `(() => { const els=[...document.querySelectorAll('*')].filter(e=>e.childElementCount===0&&e.textContent.trim()==='开发工具'); if(!els.length) return 'not found'; els[els.length-1].click(); return 'clicked'; })()`;
  await new Promise(r => setTimeout(r, 1500));
  const res = await send("Runtime.evaluate", { expression: clickExpr, returnByValue: true });
  console.log("click:", JSON.stringify(res.result?.result?.value));
  await new Promise(r => setTimeout(r, 6000));
  console.log("total matched requests:", reqs.length);
  ws.close(); process.exit(0);
});
setTimeout(() => { console.error("hard timeout"); process.exit(1); }, 25000);
