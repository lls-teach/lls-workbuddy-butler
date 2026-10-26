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
  let lastLen = -1, stable = 0;
  for (let i = 0; i < 120; i++) {
    const r = await send("Runtime.evaluate", { expression: `(() => {
      const grid=document.querySelector('.sm-grid');
      let el=grid, scroller=null;
      while(el){ if(el.scrollHeight>el.clientHeight+50){ scroller=el; } el=el.parentElement; }
      if(scroller){ scroller.scrollTop=scroller.scrollHeight; scroller.dispatchEvent(new Event('scroll',{bubbles:true})); }
      const nameCard=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='PDF 文档处理');
      let len=-1, hasMore=null;
      if(nameCard){
        let cur=nameCard.closest('.sm-card')[Object.keys(nameCard.closest('.sm-card')).find(k=>k.startsWith('__reactFiber'))];
        for(let h=0;h<60&&cur;h++){
          const p=cur.memoizedProps;
          if(p&&Array.isArray(p.skills)&&p.skills[0]&&('skill_id' in p.skills[0])){ len=p.skills.length; hasMore=!!p.hasMore; break; }
          cur=cur.return;
        }
      }
      return JSON.stringify({len, hasMore, scrolled: scroller? scroller.scrollTop : -1});
    })()`, returnByValue: true });
    const s = JSON.parse(r.result?.value ?? "{}");
    if (i % 5 === 0) console.log(`iter ${i}: len=${s.len} hasMore=${s.hasMore} scrollTop=${s.scrolled}`);
    if (s.len === lastLen && s.hasMore === false) { console.log("done at iter", i, "len", s.len); break; }
    if (s.len === lastLen) stable++; else stable = 0;
    if (stable > 15) { console.log("stable no-growth at iter", i, "len", s.len, "hasMore", s.hasMore); break; }
    lastLen = s.len;
    await new Promise(r2 => setTimeout(r2, 1200));
  }
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 240000);
