import { writeFileSync } from "node:fs";
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
    const panels=[];
    const walk=(el)=>{
      const fk=Object.keys(el).find(k=>k.startsWith('__reactFiber'));
      if(fk){
        let cur=el[fk];
        for(let h=0;h<50&&cur;h++){
          const t=String(cur.elementType??'');
          if(t.includes('CollectionPanel')){
            const p=cur.memoizedProps||{};
            panels.push({collectionId:p.collectionId, skillsLen:Array.isArray(p.skills)?p.skills.length:null, skills:p.skills});
            break;
          }
          cur=cur.return;
        }
      }
      for(const c of el.children) walk(c);
    };
    walk(document.body);
    return panels.map(p=>({collectionId:p.collectionId, skillsLen:p.skillsLen, skills:p.skills}));
  })()`;
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true });
  const val = r.result?.value;
  if (!val) { console.log("RAW:", JSON.stringify(r).slice(0, 600)); process.exit(1); }
  for (const p of val) {
    console.log("panel:", p.collectionId, "skills:", p.skillsLen);
  }
  writeFileSync("/tmp/wb-cdp/panels.json", JSON.stringify(val));
  console.log("saved panels.json, bytes:", JSON.stringify(val).length);
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 20000);
