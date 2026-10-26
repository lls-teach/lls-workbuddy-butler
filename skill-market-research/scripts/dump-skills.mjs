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
  const r = await send("Runtime.evaluate", { expression: `(() => {
    const card=[...document.querySelectorAll('.sm-card-name')].find(e=>e.textContent.trim()==='PDF 文档处理').closest('.sm-card');
    let cur=card[Object.keys(card).find(k=>k.startsWith('__reactFiber'))];
    for(let h=0;h<60&&cur;h++){
      const p=cur.memoizedProps;
      if(p&&Array.isArray(p.skills)&&p.skills[0]&&('skill_id' in p.skills[0]||'skillId' in p.skills[0])){
        return JSON.stringify({len:p.skills.length, hasMore:!!p.hasMore, items:p.skills});
      }
      cur=cur.return;
    }
    return 'not found';
  })()`, returnByValue: true });
  const v = r.result?.value;
  if (!v || v === 'not found') { console.log("RAW:", JSON.stringify(r).slice(0, 400)); process.exit(1); }
  const data = JSON.parse(v);
  writeFileSync("/tmp/wb-cdp/skills-page1.json", JSON.stringify(data, null, 1));
  console.log("len:", data.len, "hasMore:", data.hasMore, "bytes:", v.length);
  console.log("first item keys:", Object.keys(data.items[0]).join(","));
  console.log("sample:", JSON.stringify(data.items[0], null, 1).slice(0, 1500));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 20000);
