#!/usr/bin/env node
// svg2png.mjs — render an SVG file to a high-DPI PNG via headless Chrome CDP (zero deps, Node >=21).
// Usage: node svg2png.mjs input.svg output.png [scale]
// The SVG must declare width/height attributes (CSS pixels); output = that size * scale.
import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const [svgPath, pngPath, scaleArg] = process.argv.slice(2);
if (!svgPath || !pngPath) { console.error("usage: node svg2png.mjs in.svg out.png [scale=3]"); process.exit(1); }
const scale = Number(scaleArg || 3);

const svg = readFileSync(svgPath, "utf8");
const m = svg.match(/<svg[^>]*\bwidth="(\d+(?:\.\d+)?)"[^>]*\bheight="(\d+(?:\.\d+)?)"/s) ||
          svg.match(/<svg[^>]*\bheight="(\d+(?:\.\d+)?)"[^>]*\bwidth="(\d+(?:\.\d+)?)"/s);
let w, h;
{
  const wm = svg.match(/<svg[^>]*?\bwidth="(\d+(?:\.\d+)?)"/s);
  const hm = svg.match(/<svg[^>]*?\bheight="(\d+(?:\.\d+)?)"/s);
  if (!wm || !hm) { console.error("SVG must have explicit width= and height= attributes"); process.exit(1); }
  w = Math.ceil(Number(wm[1])); h = Math.ceil(Number(hm[1]));
}

const html = `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:transparent}svg{display:block}</style>${svg}`;
const dir = mkdtempSync(join(tmpdir(), "svg2png-"));
const htmlPath = join(dir, "fig.html");
writeFileSync(htmlPath, html);

const port = 9333 + Math.floor(Math.random() * 500);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", `--remote-debugging-port=${port}`, "--no-first-run", "--no-default-browser-check",
  `--user-data-dir=${join(dir, "profile")}`, "--hide-scrollbars", "--force-device-scale-factor=1",
  `--window-size=${w},${h}`, "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function getWsUrl() {
  for (let i = 0; i < 50; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      const tabs = await res.json();
      const page = tabs.find((t) => t.type === "page");
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(200);
  }
  throw new Error("chrome CDP not reachable");
}

const ws = new WebSocket(await getWsUrl());
let seq = 0; const pending = new Map();
ws.onmessage = (ev) => { const msg = JSON.parse(ev.data); if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); } };
const send = (method, params = {}) => new Promise((res) => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
await new Promise((r) => { ws.onopen = r; });

await send("Page.enable");
await send("Page.navigate", { url: `file://${resolve(htmlPath)}` });
await sleep(700); // fonts + layout settle
await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: scale, mobile: false });
await sleep(300);
const shot = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: w, height: h, scale } });
writeFileSync(pngPath, Buffer.from(shot.result.data, "base64"));
chrome.kill();
await sleep(200);
try { rmSync(dir, { recursive: true, force: true }); } catch {}
console.log(`WROTE ${pngPath} (${w}x${h} @${scale}x)`);
process.exit(0);
