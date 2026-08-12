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

## 2026-08-12 — 我把刚买的 DeepSeek key 打进了会话 transcript
- **Error:** 验证新写的 `api_keys pool` 时直接跑了 `api_keys pool deepseek`。它的 stdout 契约
  就是 `export DEEPSEEK_API_KEY='sk-...'`（`eval "$(...)"` 要靠它），而 agent 的 stdout 是被
  捕获并写进 transcript 的管道 —— 密钥当场落进 `~/.claude/projects/.../<session>.jsonl`
  （及其 `~/.claude-vault` 硬链接），共 2 处。key 是用户几小时前才买的。
- **Cause:** 一是我的操作：验证一个会打印密钥的命令，不该让它真打印。二是工具的缺陷：
  `export`/`pool` 只考虑了「人类在自己 shell 里 eval」，没考虑「agent 在跑它」——
  而 `[ -t 1 ]` 对 agent 是 false（管道），所以单靠 tty 判断保护不了这种情况。
- **Resolution:**
  1. **机制**：`stdout_is_recorded()` —— stdout 是终端**或**环境里有 `CLAUDECODE` /
     `CLAUDE_CODE_ENTRYPOINT` / `CURSOR_AGENT` 时，`export` 与 `pool` 一律不打印值
     （`pool` 仍在 stderr 报出选中哪个槽，那不含密钥）。真正会立刻吞掉值的消费者用
     `API_KEYS_ALLOW_STDOUT=1` 显式开（已给 `core-connect` 加上），人要看用 `--force`。
  2. **清痕**：用 Python 以 `r+b` **等长原地覆写**那 35 字节（`sk-REDACTED-LEAKED-INTO-TRANSCRIPT-`），
     不是临时文件改名 —— transcript 正在被追加写且被硬链接进 vault，改名会让写进程的 fd
     指向孤儿 inode（transcript 从此静默停止增长，正是 2026-07 那次事故的形状）并断开硬链接。
     等长覆写保住 inode、大小、所有 offset，JSON 仍合法。复扫 634 个 transcript/history 文件：0 命中。
  3. **仍需用户做**：值已随本轮对话发给模型提供方，本机清干净不等于没泄露 → **建议轮换这把 key**
     （DeepSeek 控制台新建 → `api_keys set deepseek_api_key_2` → `api_keys pool --refresh --sync-bao deepseek` → 控制台删旧的）。
- **Lesson:** 验证「会输出密钥」的命令时，永远只验证它的**元数据**（长度、digest、选中哪个槽），
  绝不让真值进 stdout；工具侧则要把「调用者是 agent」当成和「stdout 是终端」同级的危险面。
