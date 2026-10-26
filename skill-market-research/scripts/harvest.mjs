import { writeFileSync, appendFileSync, existsSync, readFileSync } from "node:fs";
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
const OUT = "/tmp/wb-cdp/harvest.jsonl";
const donePages = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try { donePages.add(JSON.parse(line).page); } catch {}
  }
}
ws.addEventListener("open", async () => {
  await send("Runtime.enable");
  const totalInfo = await send("Runtime.evaluate", { expression: `(() => {
    const card=document.querySelector('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){ window.__svc=cur.memoizedProps.services.marketBuiltinService; const c=window.__svc.store.getState().collections['fixed:recommend']; return JSON.stringify({total:c.total}); }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  const { total } = JSON.parse(totalInfo.result?.value ?? "{}");
  const pages = Math.ceil(total / 100);
  console.log("total:", total, "pages:", pages, "already harvested:", donePages.size);
  for (let p = 1; p <= pages; p++) {
    if (donePages.has(p)) continue;
    let ok = false;
    for (let attempt = 0; attempt < 3 && !ok; attempt++) {
      try {
        await send("Runtime.evaluate", { expression: `window.__svc.fetchCollectionSkills('fixed:recommend', ${p})`, returnByValue: false, awaitPromise: true });
        const r = await send("Runtime.evaluate", { expression: `JSON.stringify(window.__svc.store.getState().collections['fixed:recommend'].skills)`, returnByValue: true });
        const skills = JSON.parse(r.result?.value ?? "[]");
        if (skills.length > 0) {
          appendFileSync(OUT, JSON.stringify({ page: p, skills }) + "\n");
          ok = true;
          if (p % 10 === 0) console.log(`page ${p}/${pages} got ${skills.length}`);
        } else {
          console.log(`page ${p}: empty, retry ${attempt + 1}`);
          await new Promise(r2 => setTimeout(r2, 1500));
        }
      } catch (e) {
        console.log(`page ${p}: ERR`, String(e).slice(0, 120));
        await new Promise(r2 => setTimeout(r2, 2000));
      }
    }
    if (!ok) console.log(`page ${p}: FAILED after retries`);
  }
  console.log("harvest complete");
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 590000);
