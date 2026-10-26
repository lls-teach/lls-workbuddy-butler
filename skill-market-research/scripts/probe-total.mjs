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
  // 1) current list state
  const r1 = await send("Runtime.evaluate", { expression: `(() => {
    const card=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='AI交付前全自动自检技能');
    if(!card) return 'card gone';
    let cur=card.closest('.sm-card')[Object.keys(card.closest('.sm-card')).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<60&&cur;h++){
      const p=cur.memoizedProps;
      if(p&&Array.isArray(p.skills)&&p.skills[0]&&('skill_id' in p.skills[0])) return JSON.stringify({len:p.skills.length,hasMore:p.hasMore});
      cur=cur.return;
    }
    return 'panel not found';
  })()`, returnByValue: true });
  console.log("panel:", r1.result?.value);
  // 2) services internals
  const r2 = await send("Runtime.evaluate", { expression: `(() => {
    const card=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='AI交付前全自动自检技能');
    let cur=card.closest('.sm-card')[Object.keys(card.closest('.sm-card')).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){
        const svcs=cur.memoizedProps.services||{};
        const out={svcKeys:Object.keys(svcs)};
        for(const k of Object.keys(svcs)){
          const s=svcs[k];
          if(s&&typeof s==='object'){
            const kk=Object.keys(s).slice(0,25);
            out[k]=kk.join('|');
          } else out[k]=typeof s;
        }
        return JSON.stringify(out);
      }
      cur=cur.return;
    }
    return 'svc not found';
  })()`, returnByValue: true });
  console.log("services:", r2.result?.value?.slice(0, 1500));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
