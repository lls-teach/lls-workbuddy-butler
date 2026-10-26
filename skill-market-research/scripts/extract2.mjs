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
  // Step 1: probe - walk up from first card, report what we find (no big data).
  const probe = await send("Runtime.evaluate", { expression: `(() => {
    const card=document.querySelector('.sm-card');
    if(!card) return 'no card';
    let cur=card['__reactFiber$'+Object.keys(card).find(k=>k.startsWith('__reactFiber$'))] || card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    const found=[];
    for(let h=0;h<50&&cur;h++){
      const t=String(cur.elementType??'');
      const p=cur.memoizedProps;
      if(t.includes('CollectionPanel')&&p){
        found.push({h, collectionId:p.collectionId, len:Array.isArray(p.skills)?p.skills.length:-1, firstKeys:p.skills&&p.skills[0]?Object.keys(p.skills[0]):null});
      }
      cur=cur.return;
    }
    return JSON.stringify(found);
  })()`, returnByValue: true });
  console.log("probe:", probe.result?.value ?? JSON.stringify(probe).slice(0, 400));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
