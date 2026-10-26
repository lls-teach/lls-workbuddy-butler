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
    const card=document.querySelector('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){
        const s=cur.memoizedProps.services.marketBuiltinService.store.getState().collections['fixed:recommend'];
        return JSON.stringify(s.categories);
      }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  const v = r.result?.value;
  if (v && v !== 'nf') {
    await (await import("node:fs/promises")).writeFile("/tmp/wb-cdp/skill-categories.json", v);
    console.log(v.slice(0, 1500));
  } else console.log("RAW:", JSON.stringify(r).slice(0, 200));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
