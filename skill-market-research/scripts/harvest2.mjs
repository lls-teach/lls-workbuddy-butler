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
const OUT = "/tmp/wb-cdp/harvest2.jsonl";
const PROG = "/tmp/wb-cdp/progress.txt";
let startPage = 1;
if (existsSync(PROG)) startPage = Number(readFileSync(PROG, "utf8").trim()) + 1;
const seen = new Set();
for (const s of JSON.parse(readFileSync("/tmp/wb-cdp/skills-union.json", "utf8"))) seen.add(s.skill_id);
console.log("resuming from page", startPage, "known:", seen.size);
ws.addEventListener("open", async () => {
  await send("Runtime.enable");
  await send("Runtime.evaluate", { expression: `(() => {
    const card=document.querySelector('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<80&&cur;h++){
      const t=String(cur.elementType??'');
      if(t.includes('SkillsMarketContent')){ window.__svc=cur.memoizedProps.services.marketBuiltinService; return 'ok'; }
      cur=cur.return;
    }
    return 'nf';
  })()`, returnByValue: true });
  const ti = await send("Runtime.evaluate", { expression: `JSON.stringify({total:window.__svc.store.getState().collections['fixed:recommend'].total,len:window.__svc.store.getState().collections['fixed:recommend'].skills.length})`, returnByValue: true });
  const { total, len } = JSON.parse(ti.result?.value ?? "{}");
  const pages = Math.ceil(total / 100);
  console.log("total:", total, "pages:", pages, "collection len:", len);
  let prevLen = len;
  for (let p = startPage; p <= pages; p++) {
    let ok = false;
    for (let attempt = 0; attempt < 4 && !ok; attempt++) {
      try {
        await send("Runtime.evaluate", { expression: `window.__svc.fetchCollectionSkills('fixed:recommend', ${p})`, returnByValue: false, awaitPromise: true });
        const st = await send("Runtime.evaluate", { expression: `(() => { const c=window.__svc.store.getState().collections['fixed:recommend']; return JSON.stringify({len:c.skills.length}); })()`, returnByValue: true });
        const nowLen = JSON.parse(st.result?.value ?? "{}").len ?? 0;
        if (nowLen > prevLen) {
          const chunk = await send("Runtime.evaluate", { expression: `JSON.stringify(window.__svc.store.getState().collections['fixed:recommend'].skills.slice(${prevLen}))`, returnByValue: true });
          const items = JSON.parse(chunk.result?.value ?? "[]");
          const fresh = items.filter(s => !seen.has(s.skill_id));
          for (const s of fresh) seen.add(s.skill_id);
          if (fresh.length) appendFileSync(OUT, JSON.stringify(fresh) + "\n");
          prevLen = nowLen;
          ok = true;
          if (p % 10 === 0) console.log(`page ${p}/${pages}: total known ${seen.size}`);
        } else {
          await new Promise(r => setTimeout(r, 1200));
        }
      } catch (e) {
        console.log(`page ${p} err:`, String(e).slice(0, 100));
        await new Promise(r => setTimeout(r, 2000));
      }
    }
    if (!ok) console.log(`page ${p}: failed`);
    writeFileSync(PROG, String(p));
  }
  console.log("harvest2 complete, unique:", seen.size);
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(3), 540000);
