---
name: kickback
description: Check, bring up, or fix Kickbacks.ai — the ad spinner/statusline in Claude Code that earns micropayments. Use when the user says "bring up / start / check / fix / 拉起 kickback", reports kickback stopped / shows $0 / "sign-in needed" / 掉登录, wants the earning status, or asks why the ad isn't showing. Runs the status → refresh → reload runbook; NEVER fakes impressions (ad fraud).
---

# kickback — bring up & keep Kickbacks.ai earning

Kickbacks.ai injects a rotating ad into Claude Code's **spinner verbs + statusline** and pays
micropayments for impressions. Your job when this skill fires: report status, and if it's down,
walk the **bring-up runbook** to resume EARNING — or, if only an interactive login can fix it,
tell the user the one command to run.

The current request may narrow the ask (for example `status`, `why $0`, or `fix login`). Otherwise
perform the full status check and bring it up if it is not serving.

## Two hard truths (never violate)
1. **Earning = impression telemetry = the VS Code extension ONLY.** The brew `kickback` CLI is a
   read-only companion — it can DISPLAY the ad and read earnings but **cannot report impressions**.
   So real earning requires the `kickbacksai.kickbacks-ai` extension serving inside a running
   **VS Code** (Cursor does NOT have the extension — ignore Cursor entirely).
2. **Never fabricate/replay impressions to "earn."** That is ad fraud. If asked, refuse. The only
   legitimate levers are: valid auth token + VS Code extension actively serving.

## Status — always start here
```bash
kickback --json      # machine-readable: verdict, health, earnings.{lifetime,today}, ad_*, spinner_on, statusline_on, token_source
kickback doctor      # editor:Code valid/running, backend reachable, extension version, jobs
```
Read from `--json`: `verdict` (`"ok"` vs `"sign-in needed"`), `health` (`"401"` = auth failing),
`spinner_on`/`statusline_on` (true = ad wiring pinned = serving), `ad_fresh`, and
`earnings.lifetime_usd`/`today_usd`. **Serving+earning ⇔ `verdict` not "sign-in needed" AND
`statusline_on:true` AND `spinner_on:true`.**

## Bring-up runbook (do in order, re-check after each step)
1. **Healthy already?** If `verdict` is ok and `statusline_on`/`spinner_on` are true → it's earning.
   Report lifetime/today and stop.

2. **Token soft-expired / `health:"401"`** → free refresh (safe, race-free):
   ```bash
   kickback refresh --force
   ```
   Re-run `kickback --json`. If it recovers → done.

3. **Still "sign-in needed" / 401, but `kickback doctor` shows `editor:Code valid … running` +
   `backend reachable`** → the **extension is stuck in its signed-out in-memory state**; the token
   is fine, the extension just needs to reload to pick it up. Graceful **background** reload
   (VS Code Hot Exit preserves unsaved buffers; `-g` = no focus steal):
   ```bash
   osascript -e 'quit app "Visual Studio Code"'
   open -g -a "Visual Studio Code"
   ```
   Wait ~15s, then re-check `kickback --json` — the extension re-auths and takes over the
   statusLine + writes `~/.vibe-ads/cli-ad.json` → `statusline_on`/`spinner_on` flip true, earning
   resumes.

4. **Refresh fails ("refresh token dead") OR `doctor` shows the token invalid/expired** → only an
   interactive Google OAuth sign-in can fix it, and it **cannot be automated**. Tell the user to run:
   ```
   kickback login --yes
   ```
   (Suggest they type it as `! kickback login --yes` in the prompt so its output lands in-session.)
   After they log in, reload VS Code (step 3's two commands) so the extension serves with the fresh token.

## The keeper (auto-heal — usually already handling this)
`~/.claude/kickback-keeper/` + launchd `ai.kickbacks.keeper` runs `ensure.py` every 60s:
`token_guard` auto-refreshes soft token expiries; if VS Code is DOWN it auto-reopens it in the
background (`open -g -a`); if it's UP-but-stuck it restarts it (2-tick grace, rate-limited); and it
pins a keeper **display fallback** ad (`vibe-ads-statusline.mjs`) so the surface never goes blank.
- **Display fallback ≠ earning:** the fallback shows an ad but earns $0; only the VS Code extension
  serving (statusLine == the extension's own `~/.vibe-ads/vibe-ads-statusline.mjs`) actually earns.
- **Opt out of auto-managing VS Code:** `touch ~/.claude/kickback-keeper/.earner-off`
  (re-enable: `rm` it). Use when the user wants VS Code to stay closed.
- The keeper needs the token valid; it can't do the interactive `kickback login --yes` — that's
  always the user's step.

## Do NOT
- **Never** run `kickback enable autorewire` / `kickback disable autorewire` — both DISMANTLE the
  working wiring (blank `spinnerVerbs`, revert `statusLine`, delete `~/.vibe-ads/*`). The extension
  wires itself live; the keeper is the durable pin. Leave autorewire OFF.
- Don't hand serving off to Cursor — the extension isn't there; only VS Code earns.
- Don't fake impressions (see truth #2).

## Verify & report
End with `kickback --json` (or `kickback` for the pretty view) and state plainly:
verdict, `$today / $lifetime` earned, and whether it's **serving (earning)** or on **display
fallback**. If you had to punt to `kickback login --yes`, say so clearly as the one action the
user must take.
