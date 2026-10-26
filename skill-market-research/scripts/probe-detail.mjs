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
        const ds=cur.memoizedProps.services.detailService;
        const out={};
        for(const k of ['services','deps','store']){
          const v=ds[k];
          if(v&&typeof v==='object') out[k]='{'+Object.keys(v).slice(0,25).join('|')+'}';
          else out[k]=typeof v;
        }
        return JSON.stringify(out);
      }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  console.log(r.result?.value);
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 12000);
