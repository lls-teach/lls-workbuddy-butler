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
  // capture onLoadMore into window var
  const cap = await send("Runtime.evaluate", { expression: `(() => {
    const card=document.querySelector('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){
        window.__mb = cur.memoizedProps.services.marketBuiltinService;
        return 'ok';
      }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  console.log("cap:", cap.result?.value);
  let prev = 0;
  for (let round = 0; round < 80; round++) {
    const r = await send("Runtime.evaluate", {
      expression: `(async () => {
        const coll = () => window.__mb.store.getState().collections['fixed:recommend'];
        if (coll().hasMore === false) return 'DONE';
        // grab onLoadMore from fiber (panel may remount)
        const card=document.querySelector('.sm-card');
        let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
        let lm=null;
        outer: for(let h=0;h<80&&cur;h++){
          const t=String(cur.elementType??'');
          if(t.includes('SkillsMarketContent')){
            // walk DOWN is complex; use CollectionPanel via DOM: find any .sm-card fiber chain
          }
          cur=cur.return;
        }
        const c2=document.querySelector('.sm-grid');
        if(c2){
          let f=c2[Object.keys(c2).find(k=>k.startsWith('__reactFiber'))];
          let cf=f; for(let h=0;h<15&&cf;h++){ const p=cf.memoizedProps; if(p&&p.onLoadMore&&Array.isArray(p.skills)){ lm=p.onLoadMore; break; } cf=cf.return; }
        }
        if(!lm) return 'NO_LM';
        for(let i=0;i<25;i++){
          const before=coll().skills.length;
          try{ lm(); }catch(e){}
          await new Promise(r=>setTimeout(r,500));
          const now=coll().skills.length;
          if(coll().hasMore===false) return 'DONE';
          if(now===before&&i>6) return 'STALLED';
        }
        return 'ok len='+coll().skills.length;
      })()`,
      returnByValue: true, awaitPromise: true });
    const v = r.result?.value ?? JSON.stringify(r).slice(0, 200);
    const st = await send("Runtime.evaluate", { expression: `JSON.stringify({len:window.__mb.store.getState().collections['fixed:recommend'].skills.length, hasMore:window.__mb.store.getState().collections['fixed:recommend'].hasMore})`, returnByValue: true });
    const s = JSON.parse(st.result?.value ?? "{}");
    console.log(`round ${round}: ${v} | len=${s.len} hasMore=${s.hasMore}`);
    if (v === 'DONE') break;
    if (v === 'STALLED' && s.len === prev) { console.log("stalled twice, stopping"); break; }
    prev = s.len;
  }
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 590000);
