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
      const p=cur.memoizedProps;
      if(p&&Array.isArray(p.skills)&&p.skills[0]&&('skill_id' in p.skills[0])){
        const arr=p.skills;
        const ids=arr.map(s=>s.skill_id);
        const uniq=new Set(ids);
        // look for total in nearby hooks of the owner fiber
        let total=null;
        let hs=cur.memoizedState; let hi=0;
        while(hs&&hi<40){ const mv=hs.memoizedState; if(typeof mv==='number'&&mv>1000&&mv<10_000_000&&mv!==arr.length){ total=total||('hook'+hi+':'+mv); } hs=hs.next; hi++; }
        return JSON.stringify({len:arr.length, uniq:uniq.size, first:arr[0].display_name_zh, last:arr[arr.length-1].display_name_zh, lastId:arr[arr.length-1].skill_id, useRange:[arr[0].use_stat, arr[arr.length-1].use_stat], totalHint:total});
      }
      cur=cur.return;
    }
    return 'not found';
  })()`, returnByValue: true });
  console.log(r.result?.value ?? JSON.stringify(r).slice(0,400));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
