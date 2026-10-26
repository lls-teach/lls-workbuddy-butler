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
  const expr = `(() => {
    const el=[...document.querySelectorAll('*')].find(e=>e.childElementCount===0&&e.textContent.trim()==='PDF 文档处理');
    if(!el) return 'not found';
    const fk=Object.keys(el).find(k=>k.startsWith('__reactFiber'));
    let cur=el[fk]; const out=[];
    for(let h=0;h<40&&cur;h++){
      const p=cur.memoizedProps;
      if(p&&Object.keys(p).length){
        const vals={};
        for(const k of Object.keys(p)){
          if(k==='children') continue;
          let s; try{ s=JSON.stringify(p[k]); }catch{ s=String(p[k]); }
          vals[k]= s===undefined?'undef':s.slice(0,160);
        }
        out.push({h, type:String(cur.elementType??cur.tag).slice(0,30), vals});
      }
      cur=cur.return;
    }
    return out;
  })()`;
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
  console.log("RAW:", JSON.stringify(r).slice(0, 900));
  if (r.result?.exceptionDetails) console.log("EXC:", JSON.stringify(r.result.exceptionDetails).slice(0,600));
  const val = r.result?.value;
  ((await import("node:fs"))).writeFileSync("/tmp/wb-cdp/ancestor-props.json", JSON.stringify(val, null, 1));
  console.log("saved, hops:", Array.isArray(val) ? val.length : val);
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 10000);
