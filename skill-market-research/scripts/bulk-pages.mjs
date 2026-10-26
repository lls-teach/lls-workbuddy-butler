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
  // bind service to window
  await send("Runtime.evaluate", { expression: `(() => {
    const card=document.querySelector('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){ window.__svc=cur.memoizedProps.services.marketBuiltinService; return 'ok'; }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  for (let base = 80; base <= 320; base += 10) {
    const expr = `(async () => {
      const jobs=[];
      for(let p=${base}; p<${base + 10} && p<=320; p++){ jobs.push(window.__svc.fetchCollectionSkills('fixed:recommend', p).catch(e=>('E'+p+':'+e.message))); }
      await Promise.all(jobs);
      const c=window.__svc.store.getState().collections['fixed:recommend'];
      return JSON.stringify({len:c.skills.length,total:c.total,page:c.page,loading:c.loading});
    })()`;
    try {
      const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
      console.log(`pages ${base}-${base + 9}:`, r.result?.value ?? JSON.stringify(r).slice(0, 200));
    } catch (e) { console.log(`pages ${base}: ERR`, String(e).slice(0, 150)); }
  }
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 590000);
