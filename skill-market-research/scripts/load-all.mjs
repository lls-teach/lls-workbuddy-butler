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
  let lastLen = -1;
  for (let i = 0; i < 200; i++) {
    const r = await send("Runtime.evaluate", { expression: `(() => {
      const card=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='PDF 文档处理').closest('.sm-card');
      let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
      for(let h=0;h<60&&cur;h++){
        const p=cur.memoizedProps;
        if(p&&Array.isArray(p.skills)&&p.skills[0]&&('skill_id' in p.skills[0])){
          if(p.hasMore&&typeof p.onLoadMore==='function'){ try{ p.onLoadMore(); }catch(e){ return 'ERR '+e.message; } }
          return JSON.stringify({len:p.skills.length, hasMore:!!p.hasMore});
        }
        cur=cur.return;
      }
      return 'not found';
    })()`, returnByValue: true });
    const s = JSON.parse(r.result?.value ?? "{}");
    if (i % 10 === 0 || s.hasMore === false) console.log(`iter ${i}: len=${s.len} hasMore=${s.hasMore}`);
    if (s.hasMore === false) { console.log("COMPLETE at iter", i, "total", s.len); break; }
    if (s.len === lastLen && i % 20 === 19) console.log("warning: no growth at iter", i);
    lastLen = s.len;
    await new Promise(r2 => setTimeout(r2, 900));
  }
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 300000);
