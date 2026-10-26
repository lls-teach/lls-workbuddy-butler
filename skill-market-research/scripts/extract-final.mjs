// Final extraction: pull the full recommend list from the market store in chunks.
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
  const getStateExpr = `(() => {
    const card=document.querySelector('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){
        return cur.memoizedProps.services.marketBuiltinService.store.getState().collections['fixed:recommend'];
      }
      cur=cur.return;
    }
    return null;
  })()`;
  // store the collection in a temp window var for chunked reads
  await send("Runtime.evaluate", { expression: `window.__wbColl = ${getStateExpr}; 'ok'`, returnByValue: false });
  const meta = await send("Runtime.evaluate", { expression: `JSON.stringify({len:window.__wbColl.skills.length,total:window.__wbColl.total,sortBy:window.__wbColl.sortBy,hasMorePage:window.__wbColl.loading})`, returnByValue: true });
  const metaV = JSON.parse(meta.result?.value ?? "{}");
  console.log("meta:", JSON.stringify(metaV));
  const total = metaV.len;
  const all = [];
  const CH = 1500;
  for (let i = 0; i < total; i += CH) {
    const r = await send("Runtime.evaluate", { expression: `JSON.stringify(window.__wbColl.skills.slice(${i}, ${i + CH}))`, returnByValue: true });
    const chunk = JSON.parse(r.result?.value ?? "[]");
    all.push(...chunk);
    process.stdout.write(`\rchunked ${all.length}/${total}`);
  }
  console.log();
  writeFileSync("/tmp/wb-cdp/skills-all.json", JSON.stringify({ total: metaV.total, sortBy: metaV.sortBy, count: all.length, skills: all }));
  console.log("saved skills-all.json, items:", all.length);
  // featured too
  const fr = await send("Runtime.evaluate", { expression: `(() => { const card=document.querySelector('.sm-card'); let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))]; for(let h=0;h<80&&cur;h++){ const t=String(cur.elementType??''); if(t.includes('SkillsMarketContent')){ return JSON.stringify(cur.memoizedProps.services.marketBuiltinService.store.getState().collections['fixed:featured'].skills); } cur=cur.return; } return '[]'; })()`, returnByValue: true });
  writeFileSync("/tmp/wb-cdp/skills-featured.json", fr.result?.value ?? "[]");
  console.log("featured saved:", JSON.parse(fr.result?.value ?? "[]").length);
  delete window.__wbColl;
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 120000);
