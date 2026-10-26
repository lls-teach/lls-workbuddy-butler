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
  const click = await send("Runtime.evaluate", { expression: `(() => {
    const els=[...document.querySelectorAll('*')].filter(e=>e.childElementCount===0&&e.textContent.trim()==='使用量');
    if(!els.length) return 'not found';
    els[els.length-1].click();
    return 'clicked';
  })()`, returnByValue: true });
  console.log("click:", click.result?.value);
  await new Promise(r => setTimeout(r, 4000));
  const check = await send("Runtime.evaluate", { expression: `(() => {
    const card=document.querySelector('.sm-card');
    if(!card) return 'no cards';
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){
        const s=cur.memoizedProps.services.marketBuiltinService.store.getState().collections['fixed:recommend'];
        return JSON.stringify({len:s.skills.length,total:s.total,sortBy:s.sortBy,page:s.page,first3:s.skills.slice(0,3).map(x=>x.display_name_zh+'|'+x.use_stat.use_count)});
      }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  console.log("state:", check.result?.value);
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 20000);
