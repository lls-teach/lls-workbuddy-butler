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
    if(!card) return 'NO CARD';
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){
        const cols=cur.memoizedProps.services.marketBuiltinService.store.getState().collections;
        const rec=cols['fixed:recommend'];
        return JSON.stringify({collKeys:Object.keys(cols), rec:{len:rec?.skills?.length, hasMore:rec?.hasMore, sortBy:rec?.sortBy, categoryId:rec?.categoryId, loading:rec?.loading, page:rec?.page, total:rec?.total}});
      }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  console.log(r.result?.value ?? JSON.stringify(r).slice(0,300));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 12000);
