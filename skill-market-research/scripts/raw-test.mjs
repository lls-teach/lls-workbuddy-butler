const list = await (await fetch("http://127.0.0.1:9222/json")).json();
const page = list.find(t => t.type === "page");
const ws = new WebSocket(page.webSocketDebuggerUrl);
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id === 1) {
    const val = m.result?.result?.value ?? "";
    console.log("value length:", val.length, "| full msg bytes:", ev.data.length);
    process.exit(0);
  }
});
ws.addEventListener("open", () => {
  ws.send(JSON.stringify({ id: 1, method: "Runtime.evaluate", params: { expression: "'y'.repeat(2000)", returnByValue: true } }));
});
setTimeout(() => process.exit(1), 8000);
