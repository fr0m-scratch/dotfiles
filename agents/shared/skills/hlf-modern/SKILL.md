---
name: hlf-modern
description: >-
  Apply the HLF-Modern landing and pitch style: a current, launch-grade skin on
  top of the restrained HLF/Apple-clean design language. Use for modern HLF
  landing pages with an oversized hero, cool flat canvas, real window-shell
  product shots, sticky navigation, restrained motion, and zero AI-style excess.
---

# hlf-modern — HLF, amplified to 2026 launch grade

A landing/pitch skin that keeps **every HLF invariant** and adds the few *signature moves* that
make a page read "current Product-Hunt launch" instead of "2019 Apple". Distilled from a real
4-direction × 3-judge design workflow on the 工核CADQuota sales page (winner: the "keynote"
direction, judged 9/10 on HLF-fidelity). It is the modern sibling of `apple-sales-doc`: same content
recipe, louder presentation.

## Keep these HLF invariants (breaking any = failure — grep before finishing)
- Light, content-first, restrained. System fonts only: `-apple-system,"SF Pro Display","PingFang SC",system-ui,sans-serif`. ALL numbers `font-variant-numeric:tabular-nums`.
- **One** accent `--acc:#0066cc`, used in <6 places (hero clause / primary button / kicker / table ✓ / one anchor emphasis). Everything else ink/grey + hairlines.
- 8px grid. Radii 8–20px. Only soft, functional shadows.
- NO AI-slop: no decorative gradient color-blocks, glow/halo shadows, neon, heavy glassmorphism, purple-gold "AI" palette, emoji, colored left-border cards, glowing confidence meters, marketing bombast, "科技感" FX.
- Only sanctioned blur: the translucent nav (`backdrop-filter:saturate(180%) blur(20px)`).
- Honest tone, REAL screenshots, REAL numbers.

## The signature moves (this is what makes it "modern")
1. **Cool flat-tint canvas, white paper on top.** `--canvas:#f4f6fb` page bg (a *flat* tint, NOT a gradient), content sheets/cards stay pure `#fff`. (Warm variant: `#f6f5f2`.) This one line reads instantly current.
2. **Oversized hero.** `h1{font-size:clamp(40px,6vw,72px);font-weight:600;letter-spacing:-.03em;line-height:1.06;max-width:14ch}`, one clause in `--acc`; 18–21px grey lead at `max-width:42ch`; 128px top padding. Center it (keynote) or split copy-left/shot-right (SaaS).
3. **Hero product anchor.** Lift a window-shell product shot into the FIRST screen, right after the CTAs (`max-width:1000px`, slight bleed). Customer sees the real tool in 5 seconds.
4. **Window-shell product shots.** Every screenshot wrapped in a mac/browser chrome: 3 traffic dots + a fake URL bar with a **pure-CSS lock icon** (no image/emoji) showing a real route, then the image, then a 12px grey `figcaption` prefixed `真实截图 ·`. `border-radius:18px; border:1px solid --line; box-shadow:0 24px 60px rgba(0,0,0,.10)`. Print: `box-shadow:none`.
5. **Sticky translucent nav.** mono mark (a `--ink` rounded square with 2–3 char wordmark, e.g. 工核) left · sparse grey links center · ONE accent pill CTA right.
6. **Hairline 4-up stats band.** `border-top/bottom` hairline, no card/round/shadow; numbers `clamp(34px,4vw,48px); letter-spacing:-.03em; tabular-nums`; 12.5px grey labels. Real metrics only.
7. **Uppercase-tracking kickers.** `12px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:--ink3` per section (or numbered `01/02`).
8. **One monochrome "jewel" — at most one.** Make the mono mark crisp, or a single masked **dot-grid texture** in the hero (`radial-gradient(rgba(29,29,31,.06) 1px,transparent 1px) 22px`, masked by a soft ellipse, `display:none` in print). NEVER a colored AI orb/glow.
9. **Proactive honesty card.** If the demo is pre-baked/limited, a small grey `演示边界·主动坦白` card right after the stats (plus the footer note). Owning limits builds trust.
10. **Near-invisible table emphasis.** Comparison "我方" column gets `rgba(0,102,204,.025)` tint + accent `✓` — guides the eye without breaking restraint.
11. **Restrained motion, CSS-only.** Card hover `translateY(-2px)`+shadow; nav blur. No JS dependency — the file must open over `file://`.

## Drop-in token head
```css
:root{
  --acc:#0066cc; --acc-tint:rgba(0,102,204,.025);
  --ink:#1d1d1f; --ink2:#6e6e73; --ink3:#86868b; --line:#d2d2d7;
  --canvas:#f4f6fb; --paper:#fff; --radius:16px;
  --shot-shadow:0 24px 60px rgba(0,0,0,.10);
}
body{font-family:-apple-system,"SF Pro Display","PingFang SC",system-ui,sans-serif;background:var(--canvas);color:var(--ink);line-height:1.5;font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
```

## Section recipe (top → bottom)
nav (sticky translucent) → hero (kicker? + h1 + lead + pain pill + 2 CTAs + **hero shot**) → hairline stats band →
honesty card → proof sections (kicker + h2 + ≤700px desc + ONE window-shell shot + caption), alternating with
advantage-card grids → comparison table (3 col, 我方 tinted) → path-to-adopt steps → footer (CTA line + honesty note).
Same content as `apple-sales-doc`; only the presentation is amplified.

## Build workflow
1. Capture REAL UI screenshots (deep-link `?v=&p=` per apple-frontend), one per section.
2. Author ONE self-contained HTML with inline CSS, using placeholders `__IMG_0__…__IMG_n__` for the shots (keeps the design pass small); inject the base64 data-URIs afterward with a tiny Python pass.
3. Self-verify: headless-screenshot (`--headless=new --window-size=1280,3200`) and Read it — confirm images load, layout holds, and grep the no-AI-slop list.
4. WaveTerm: `wsh web open "file://$PWD/.check/<slug>.html"`. ~1–2MB with 4–5 embedded shots is fine.

When in doubt, choose the quieter option and lean on scale + whitespace, not decoration. HLF restraint > cleverness — just bigger and more current.
