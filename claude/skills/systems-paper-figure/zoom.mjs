#!/usr/bin/env node
// zoom.mjs — re-render a rectangular REGION of an SVG at high scale, for close visual inspection.
// Usage: node zoom.mjs fig.svg out.png X Y W H [scale=3]
// X/Y/W/H are in the SVG's own user units (same coordinate space you hand-laid).
//
// Why this exists: `sips --cropOffset` is measured from the image CENTRE, not the top-left,
// so cropping a rendered PNG silently gives you the wrong region. Re-rendering through the
// viewBox is exact and also gives you real resolution instead of upscaled pixels.
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const [svgPath, pngPath, X, Y, W, H, scaleArg] = process.argv.slice(2);
if (!svgPath || !pngPath || W === undefined || H === undefined) {
  console.error("usage: node zoom.mjs fig.svg out.png X Y W H [scale=3]");
  process.exit(1);
}
const scale = scaleArg || "3";
const here = dirname(fileURLToPath(import.meta.url));

const src = readFileSync(svgPath, "utf8");
// Replace the root width/height/viewBox with the requested window.
const patched = src.replace(
  /<svg([^>]*?)\bwidth="[^"]*"([^>]*?)\bheight="[^"]*"([^>]*?)\bviewBox="[^"]*"/s,
  `<svg$1width="${W}"$2height="${H}"$3viewBox="${X} ${Y} ${W} ${H}"`,
);
if (patched === src) {
  console.error("could not rewrite root <svg>: it must carry width=, height= and viewBox=");
  process.exit(1);
}

const dir = mkdtempSync(join(tmpdir(), "svgzoom-"));
const tmp = join(dir, "region.svg");
writeFileSync(tmp, patched);
const r = spawnSync("node", [join(here, "svg2png.mjs"), tmp, resolve(pngPath), scale], { stdio: "inherit" });
try { rmSync(dir, { recursive: true, force: true }); } catch {}
process.exit(r.status ?? 1);
