// Deep probe of the main page: frames, body size, marketplace presence.
const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const page = list.find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
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
  await send("Runtime.enable");
  const ev = async expr => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    return r.result?.result?.value ?? JSON.stringify(r.result ?? r).slice(0, 300);
  };
  console.log("href:", await ev("location.href"));
  console.log("frames:", await ev("document.querySelectorAll('iframe,webview').length"));
  console.log("bodyLen:", await ev("document.body ? document.body.innerHTML.length : -1"));
  console.log("title:", await ev("document.title"));
  console.log("markers:", await ev("Array.from(document.querySelectorAll('[class]')).slice(0,5).map(e=>e.className.toString().slice(0,60))"));
  const tree = await send("Page.getFrameTree");
  console.log("frameTree:", JSON.stringify(tree.frameTree, null, 1).slice(0, 1500));
  ws.close(); process.exit(0);
});
setTimeout(() => { console.error("timeout"); process.exit(1); }, 10000);
