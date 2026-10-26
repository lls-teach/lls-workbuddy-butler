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
  const probe = await send("Runtime.evaluate", { expression: `(() => {
    const card=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='PDF 文档处理').closest('.sm-card');
    if(!card) return 'no card';
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    const found=[];
    for(let h=0;h<60&&cur;h++){
      const t=String(cur.elementType??'');
      const p=cur.memoizedProps;
      if(p){
        const pk=Object.keys(p);
        const arrKey=pk.find(k=>Array.isArray(p[k])&&p[k].length&&p[k][0]&&typeof p[k][0]==='object'&&('skill_id' in p[k][0]||'skillId' in p[k][0]||'id' in p[k][0]));
        if(t.includes('Collection')||arrKey) found.push({h, t:t.slice(0,40), arrKey, len:arrKey?p[arrKey].length:-1});
      }
      cur=cur.return;
    }
    return JSON.stringify(found);
  })()`, returnByValue: true });
  console.log("probe:", probe.result?.value ?? JSON.stringify(probe).slice(0, 500));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 15000);
