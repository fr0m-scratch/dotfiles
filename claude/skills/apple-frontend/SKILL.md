---
name: apple-frontend
description: Build a clean, professional Apple-HIG-style web frontend (light, system-font, hairline borders, single restrained accent, no AI-slop). Use when the user wants a product UI / app shell / dashboard that looks like Apple (App Store / Numbers / System Settings / Sandbox) and explicitly NOT "AI-style". Master-detail app shell with segmented control, sidebar list, detail views; restrained confidence/data display. Pairs with apple-sales-doc.
---

# apple-frontend — Apple-grade product UI

Produce a frontend that reads as **Apple product-grade**: light, quiet, content-first.
The reference points are **Apple product pages / App Store / Numbers / System Settings / Sandbox** —
never a "techy/cool" dark neon dashboard. This skill is the distilled design system from a
real build (a CAD-quote工作台) that a design-judge panel scored 9/10 for HIG fidelity.

## The one rule that matters most: NO AI-slop
Any of these appearing = failure. Grep your output for them before finishing:
- gradients (`linear-gradient`/`radial-gradient`) as decoration, glow/`box-shadow` halos, neon, blur-heavy glassmorphism
- purple+gold "AI" palette, colored left-border cards, confidence shown as glowing progress meters
- emoji, decorative icons, marketing-y hero slogans, "科技感" treatments
Allowed exceptions: an authentic translucent nav bar (`backdrop-filter:saturate(180%) blur(20px)`),
and CSS crosshatch ONLY as a placeholder for a missing image (replace with the real image).

## Design tokens (use verbatim; remap for dark mode)
```css
:root{
  --bg:#fff; --bg-sub:#f5f5f7; --line:#d2d2d7; --line-2:#e8e8ed;
  --ink:#1d1d1f; --ink-2:#6e6e73; --ink-3:#86868b;
  --accent:#0066cc; --accent-soft:rgba(0,102,204,.12);
  --warn:#bf6b00; --ok:#1d7a4d;
  --radius:12px; --radius-sm:8px;
}
body{font-family:-apple-system,"SF Pro Display","SF Pro Text","PingFang SC",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased; font-size:14px; line-height:1.45; color:var(--ink); background:var(--bg);}
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum";} /* ALL numbers */
@media (prefers-color-scheme:dark){:root{
  --bg:#1d1d1f; --bg-sub:#000; --line:#3a3a3c; --line-2:#2c2c2e;
  --ink:#f5f5f7; --ink-2:#a1a1a6; --ink-3:#86868b;
  --accent:#2997ff; --accent-soft:rgba(41,151,255,.18); --warn:#ff9f0a; --ok:#30d158; }}
```
- **One accent only.** Use `--accent` in very few places (active tab, primary button, key pins). Everything else is ink/grey.
- Spacing on an **8px grid** (8/12/16/24/32). Radii small & uniform (8–12px). Elevation only where functional (`0 1px 2px rgba(0,0,0,.06)`).
- Type hierarchy by size/weight, not color noise. Titles `-0.02em` letter-spacing, 21–40px, weight 600.

## Canonical structure: master-detail app shell
```
.app (100vh, flex column)
 ├─ .topbar  — brand (mono mark) · segmented control (center) · source/actions (right); translucent
 ├─ .body (flex, min-height:0)
 │   ├─ .sidebar (fixed ~286px, bg-sub) — search + scrollable list of items (rows ≥44px)
 │   └─ .detail (flex:1, scroll) — .detail-inner max-width ~1120px centered
 │        └─ .view (toggle .show) ×N, switched by the segmented control
 └─ data via <script src="data/app.js"> as window.APP_DATA (NOT fetch — file:// CORS blocks it)
```
Segmented control = the primary nav (`原图 / 识别标注 / 清单`-style). Sidebar selection drives all views.

## Required interaction + a11y (judge-checked)
- `:focus-visible{box-shadow:0 0 0 3px rgba(0,102,204,.45)}` on tabs, rows, buttons, cards.
- Segmented control: `role=tablist` + `aria-selected`; buttons `role=tab`.
- Every interactive el has `:hover` and `:active` feedback. Rows `min-height:44px`.
- Empty / no-selection / loading states are designed, not blank.
- Deep-link via `?v=&p=` query params is cheap and lets you screenshot any view.

## Confidence / data display — RESTRAINED
Not a glowing bar. Use a 7px neutral dot + a quiet word (`高 / 中 / 待复核`) + `title`/`aria-label` with the exact %.
Color the dot `--ok`/`--warn` only; low-confidence rows get a subtle `--warn` tint, never a glow.

## Real content, real images
Wire real data + real images (relative `src`, not all base64). If overlaying detections/annotations
on an image, anchor boxes on **real coordinates** (e.g. OCR bboxes) over the *same image you measured* —
never model-guessed pixel coords (they misalign). Same image in = same image rendered (`width:100%;height:auto`,
overlay `position:absolute;inset:0`, boxes in %).

## Workflow
1. Write `index.html` (shell + all CSS inline), `ui.js` (render from `window.APP_DATA`), `data/app.js`.
2. `node --check ui.js` to catch syntax errors.
3. Self-verify visually: headless screenshot each view and Read it —
   `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --screenshot=/tmp/v.png --window-size=1440,900 --force-device-scale-factor=2 "file://$PWD/index.html?v=v2"`
4. If the user runs WaveTerm, open with `wsh web open "file://$PWD/index.html"`.
5. Grep for the anti-AI list; fix any hit.

When unsure on a visual call, choose the quieter option. Apple restraint > cleverness.
