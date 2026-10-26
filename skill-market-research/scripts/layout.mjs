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
  const r = await send("Runtime.evaluate", { expression: `(() => {
    const card=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='PDF 文档处理').closest('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<60&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('DiscoverSection')){
        let hs=cur.memoizedState, hi=0;
        while(hs){ const mv=hs.memoizedState;
          if(mv&&typeof mv==='object'&&!Array.isArray(mv)&&('tabs' in mv||'categories' in mv)){ return JSON.stringify(mv).slice(0,20000); }
          hs=hs.next; hi++; }
        return 'layout hook not found';
      }
      cur=cur.return;
    }
    return 'DiscoverSection not found';
  })()`, returnByValue: true });
  const v = r.result?.value;
  if (v && v !== 'not found') {
    await (await import("node:fs/promises")).writeFile("/tmp/wb-cdp/layout.json", v);
    console.log("saved layout.json bytes:", v.length);
    console.log(v.slice(0, 1200));
  } else console.log("RAW:", JSON.stringify(r).slice(0, 300));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
