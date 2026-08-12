# Errors

> Log every error encountered and how it was resolved.

## 2026-06-09 — install.sh: FORMULAE[@] unbound variable
- **Error:** `FORMULAE[@]: unbound variable` on both dry-runs.
- **Cause:** macOS `/bin/bash` is 3.2; under `set -u`, expanding an empty array is an error there.
- **Resolution:** length-gate first and use the `${arr[@]+"${arr[@]}"}` safe-expansion idiom. Re-ran clean.

## 2026-06-09 — shellcheck SC2294 in run()
- **Error:** `eval "$@"` flagged (eval negates array benefit).
- **Cause:** dry-run helper builds command strings deliberately.
- **Resolution:** switched to `eval "$*"`; intentional string-eval, warning cleared.

## 2026-06-09 — git push failed: exit status 128 (SSH)
- **Error:** `gh repo create dotfiles --source=. --remote=origin --push` created the GitHub repo and added an SSH `origin` (`git@github.com:...`), but the push failed: "make sure you have the correct access rights ... exit status 128". Retries with other names hit "Name already exists".
- **Cause:** No SSH key registered with GitHub; `origin` was set to the SSH URL. The repo already existed from the first (partial) attempt, so re-creating collided.
- **Resolution:** `gh auth setup-git` (HTTPS credential helper) → `git remote set-url origin https://github.com/fr0m-scratch/dotfiles.git` → `git push -u origin main`. Succeeded.

## 2026-08-12 — api_keys 的 DeepSeek 余额行报了「USD 0.00」，账户其实有 CNY 88.62
- **Error:** 新加的 `deepseek_balance` 用 `json_field` 取 `currency` / `total_balance`，
  对新 key 打出 `balance USD 0.00`，看上去像一把没充值的 key —— 而它同一刻真跑通了 completion。
- **Cause:** `/user/balance` 的 `balance_infos` 是**每币种一条**的数组，且 USD 在前（即使账户
  一分美元都没有）。`json_field` 只取第一处匹配，于是读到 USD 那条，CNY 88.62 那条被丢掉。
  这正是本工具最反对的那类缺陷：探针本身在撒谎。
- **Resolution:** 改成把 `currency` 与 `total_balance` 两串按文档顺序 zip（每个对象里
  currency 必在 total_balance 之前，故两列对齐），输出 `balance USD 0.00, CNY 88.35`。
  在 `/bin/bash` 3.2 下复跑通过（数组只用 `${#a[@]}` 与带默认值的下标，未踩空数组 `set -u` 的坑）。
- **Lesson:** 面向「余额/配额」的字段，先看它是不是数组；单值取法遇上多币种/多资源包一定失真。
