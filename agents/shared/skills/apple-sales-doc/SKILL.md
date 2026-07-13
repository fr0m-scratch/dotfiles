---
name: apple-sales-doc
description: Generate a polished, Apple-clean one-page sales / product pitch document as a SINGLE self-contained HTML file, with real product screenshots embedded as base64. Use when the user wants a sales doc / pitch / one-pager / 销售文档 that explains a product's value and technical advantages and must be shareable, print-to-PDF friendly, and NOT AI-styled. Pairs with apple-frontend (screenshot that UI into this doc).
---

# apple-sales-doc — Apple-clean sales one-pager

Produce ONE **self-contained** HTML file (inline CSS, all images base64-embedded, no network deps)
that pitches a product: punchy hero → proof stats → value/tech-advantage sections interleaved with
**real product screenshots** → comparison table → path-to-adopt → CTA. Audience is a real customer/buyer,
not engineers. Tone: confident, concrete, honest. Aesthetic matches `apple-frontend` (light, restrained).

## Hard rules
- **Self-contained**: embed every screenshot as `data:image/png;base64,…`. No external/CDN fonts/CSS/JS.
- **Real screenshots only.** Capture the actual product UI (see apple-frontend's headless-Chrome step),
  downscale to ~1440w (`sips --resampleWidth 1440`) before base64 to control size. Never fake/mock a screenshot.
- **Print-friendly**: include `@media print{body{background:#fff}.shot{box-shadow:none}.sec,.hero{break-inside:avoid}}`.
- **No AI-slop** (same list as apple-frontend): no gradients/glow/neon/purple-gold/emoji/colored-border cards.
- **Honest footnote**: if the demo is pre-baked / limited, say so quietly in the footer — don't oversell.
- Pull headline numbers from real data (totals, counts, accuracy), not invented figures.

## Design tokens (verbatim)
```css
:root{--bg:#fff;--sub:#f5f5f7;--line:#d2d2d7;--line2:#e8e8ed;--ink:#1d1d1f;--ink2:#6e6e73;--ink3:#86868b;--acc:#0066cc;--warn:#bf6b00;--ok:#1d7a4d}
body{font-family:-apple-system,"SF Pro Display","PingFang SC",system-ui,sans-serif;color:var(--ink);background:var(--sub);-webkit-font-smoothing:antialiased;line-height:1.5;font-size:15px}
.wrap{max-width:940px;margin:0 auto;background:var(--bg)}   /* the document is a centered white sheet */
.num{font-variant-numeric:tabular-nums}
```

## Section recipe (top → bottom)
1. **Hero** (`padding:64px 56px 40px`): mono brand mark + name; `h1` 40px/600/`-0.025em` with ONE clause in `--acc`;
   18px grey lead; a single bordered "痛点/problem" pill. State the before→after transformation.
2. **Stats band**: `grid;repeat(4,1fr)` with 1px dividers; each = big 30px tabular number + 12.5px grey label. Use real metrics.
3. **Proof sections** (`.sec`, `padding:48px 56px`, bottom hairline): each has a `.kicker` (12px/700/uppercase/`--acc`),
   27px `h2`, ≤700px grey desc, then a `.shot` (bordered, `border-radius:14px`, soft `box-shadow:0 10px 40px rgba(0,0,0,.08)`)
   wrapping ONE real screenshot, + centered 12.5px grey `.cap`. Alternate screenshot ↔ advantage-card sections.
4. **Advantage cards**: `.adv{grid;1fr 1fr;gap:22px}`; each `.card` = numbered chip (`.n`) + 17px `h3` + 14px grey `p`
   + a mono `.ex` example box (`background:var(--sub)`). Show a concrete before→after using `.bad`(strikethrough grey)
   `→` `.good`(green) when demonstrating correction/quality.
5. **Comparison table** `.cmp`: 3 cols (dimension / 旧方式 / 本产品). "本产品" cells `font-weight:600` with `::before{content:"✓ ";color:var(--ok)}`.
6. **Path-to-adopt** `.steps{grid;repeat(4,1fr)}`: numbered step cards (① identify → … → adopt).
7. **Footer**: bold 20px CTA line + grey supporting sentence + a small grey honesty `.note` (hairline top border).

## Build workflow
1. Screenshot the real UI (multiple views/variants for variety), `sips --resampleWidth 1440`, base64 each.
2. Generate the HTML with a small Python script that injects the data-URIs + real stat numbers into the template
   (f-string; remember to double `{{ }}` for literal CSS braces). Write to `.check/<slug>.html` (or as the user asks).
3. Self-verify: headless-screenshot the doc and Read it to confirm images loaded and layout holds.
4. WaveTerm: `wsh web open "file://$PWD/.check/<slug>.html"`. File size ~1–2MB with 4–5 embedded shots is fine.

More screenshots = more persuasive, but keep each section to ONE shot with a caption that says what it proves.
