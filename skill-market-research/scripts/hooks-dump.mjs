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
    const out=[];
    for(let h=0;h<60&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('CollectionPanel')||t.includes('DiscoverSection')||t.includes('Spotlight')){
        const p=cur.memoizedProps||{};
        const propsSummary={};
        for(const k of Object.keys(p)){
          const v=p[k];
          const tv=Array.isArray(v)?('array['+v.length+']'):typeof v;
          propsSummary[k]= tv==='function'? 'fn' : tv==='object'&&v? Object.keys(v).slice(0,12).join('|') : String(v).slice(0,60);
        }
        // walk memoizedState hooks
        const hooks=[]; let hs=cur.memoizedState, hi=0;
        while(hs&&hi<30){
          const mv=hs.memoizedState;
          let desc;
          if(Array.isArray(mv)) desc='array['+mv.length+']';
          else if(mv&&typeof mv==='object') desc='obj{'+Object.keys(mv).slice(0,15).join('|')+'}';
          else if(typeof mv==='function') desc='fn';
          else desc=String(mv).slice(0,60);
          hooks.push(hi+':'+desc);
          hs=hs.next; hi++;
        }
        out.push({h, t:t.slice(0,40), props:propsSummary, hooks});
      }
      cur=cur.return;
    }
    return JSON.stringify(out);
  })()`, returnByValue: true });
  console.log(JSON.stringify(r.result?.value ?? r, null, 1).slice(0, 6000));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
