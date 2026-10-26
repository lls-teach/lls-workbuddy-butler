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
  const scrollOnce = await send("Runtime.evaluate", { expression: `(() => {
    // find scrollable ancestor of the sm-grid
    const grid=document.querySelector('.sm-grid');
    let el=grid, scroller=null;
    while(el){ if(el.scrollHeight>el.clientHeight+50){ scroller=el; } el=el.parentElement; }
    if(!scroller) return 'no scroller';
    scroller.scrollTop=scroller.scrollHeight;
    scroller.dispatchEvent(new Event('scroll',{bubbles:true}));
    return 'scrolled to '+scroller.scrollTop+'/'+scroller.scrollHeight+' cls='+String(scroller.className).slice(0,60);
  })()`, returnByValue: true });
  console.log(scrollOnce.result?.value ?? JSON.stringify(scrollOnce).slice(0,300));
  ws.close(); process.exit(0);
});
setTimeout(() => process.exit(1), 12000);
