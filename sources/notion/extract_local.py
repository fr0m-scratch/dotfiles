#!/usr/bin/env python3
"""
Notion LOCAL-CACHE extractor — gathers content from the running Notion desktop app's
local SQLite cache (~/Library/Application Support/Notion/notion.db). Works WITHOUT the API
and WITHOUT sharing pages to an integration: if it's visible in your Notion app, it's here.

Usage:
  python3 extract_local.py "<query1,query2,...>" <output_dir>
  python3 extract_local.py "伊芙丽,YFL" /path/to/intake/notion

Strategy (two sweeps, deduped):
  A. Each matching page → render its FULL subtree (children ordered via `content`).
  B. Scattered matches inside OTHER pages → a `_mentions-elsewhere.md` with parent context.
Filters alive=1, untrashed, unarchived. Read-only: copies the DB via `.backup` first.
Output is REFERENCE-ONLY (provenance + banner) — never ground truth.
"""
import sqlite3, json, re, os, sys, subprocess, tempfile, datetime

SRC = os.path.expanduser("~/Library/Application Support/Notion/notion.db")

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    needles = tuple(x.strip() for x in sys.argv[1].split(",") if x.strip())
    out = sys.argv[2]
    date = datetime.date.today().isoformat()
    os.makedirs(out, exist_ok=True)

    snap = os.path.join(tempfile.mkdtemp(prefix="notion_snap_"), "snap.db")
    subprocess.run(["sqlite3", SRC, f".backup '{snap}'"], check=True)
    con = sqlite3.connect(snap); con.row_factory = sqlite3.Row
    B = {r["id"]: dict(r) for r in con.execute(
        "SELECT id,type,properties,content,parent_id,parent_table,format FROM block "
        "WHERE alive=1 AND moved_to_trash_id IS NULL AND archived_time IS NULL")}

    def J(s):
        try: return json.loads(s) if s else None
        except Exception: return None
    def title_of(b):
        p = J(b.get("properties")) or {}
        return rich(p.get("title")) if isinstance(p, dict) else ""
    def rich(runs):
        if not runs: return ""
        o=[]
        for run in runs:
            if not isinstance(run, list) or not run: continue
            t=run[0]
            if t=="‣" and len(run)>1:
                try:
                    k,ref=run[1][0][0],run[1][0][1]
                    o.append(f"[[{title_of(B[ref]) or 'page'}]]" if k=="p" and ref in B else ("[date]" if k=="d" else ""))
                except Exception: o.append("")
            else: o.append(str(t))
        return "".join(o)
    def children(b):
        c=J(b.get("content"))
        if isinstance(c,list) and c: return [x for x in c if x in B]
        return [k for k,v in B.items() if v.get("parent_id")==b["id"]]

    covered=set()
    def render(bid, depth=0):
        if bid not in B or bid in covered: return []
        b=B[bid]; covered.add(bid); t=b["type"]; ind="  "*depth; txt=title_of(b); L=[]
        if t=="page":
            L.append(f"# {txt or '(untitled)'}\n" if depth==0 else f"\n{'#'*min(depth+1,6)} {txt or '(untitled)'}\n")
        elif t=="header": L.append(f"\n## {txt}\n")
        elif t=="sub_header": L.append(f"\n### {txt}\n")
        elif t=="sub_sub_header": L.append(f"\n#### {txt}\n")
        elif t=="bulleted_list": L.append(f"{ind}- {txt}")
        elif t=="numbered_list": L.append(f"{ind}1. {txt}")
        elif t=="to_do":
            chk="x" if (J(b.get("properties")) or {}).get("checked",[["No"]])[0][0]=="Yes" else " "
            L.append(f"{ind}- [{chk}] {txt}")
        elif t in ("quote","callout"): L.append(f"> {txt}")
        elif t=="toggle": L.append(f"{ind}- {txt}")
        elif t=="code": L.append(f"```\n{txt}\n```")
        elif t=="divider": L.append("\n---\n")
        elif t=="table_row":
            p=J(b.get("properties")) or {}
            L.append("| "+" | ".join(rich(v) for v in p.values())+" |") if isinstance(p,dict) else None
        elif t=="image": L.append(f"{ind}![image]()")
        elif txt: L.append(f"{ind}{txt}")
        nd=depth+1 if t in ("bulleted_list","numbered_list","to_do","toggle") else depth
        for cid in children(b): L+=render(cid, nd)
        return L

    def slug(s): return (re.sub(r'[\\/:*?"<>|]+',"-",(s or "untitled")).strip()[:60] or "untitled")
    def match(b): return b.get("properties") and any(n in b["properties"] for n in needles)
    def banner(bid,title): return (f"---\nsource: notion\nnotion_block_id: {bid}\ntitle: {title}\n"
        f"fetched_at: {date}\nextraction: local-cache (notion.db)\nstatus: reference-only\n---\n"
        f"> ⚠️ Reference only — NOT ground truth. Extracted from the local Notion app cache on {date}.\n\n")

    mentions=[b for b in B.values() if match(b)]
    seeds=[b for b in mentions if b["type"]=="page"]; seed_ids={b["id"] for b in seeds}
    def has_seed_anc(b):
        cur=b.get("parent_id"); seen=set()
        while cur in B and cur not in seen:
            seen.add(cur)
            if cur in seed_ids: return True
            cur=B[cur].get("parent_id")
        return False
    written=[]
    for b in [s for s in seeds if not has_seed_anc(s)]:
        body="\n".join(render(b["id"],0))
        fn=os.path.join(out, slug(title_of(b))+".md")
        open(fn,"w").write(banner(b["id"],title_of(b))+body+"\n"); written.append(fn)

    def page_ctx(b):
        cur=b.get("parent_id"); seen=set()
        while cur in B and cur not in seen:
            seen.add(cur)
            if B[cur]["type"]=="page": return title_of(B[cur])
            cur=B[cur].get("parent_id")
        return "(unknown page)"
    scattered=[b for b in mentions if b["id"] not in covered]
    if scattered:
        L=[banner("(multiple)","散落的提及"), "# 散落的提及（在其他页面中）\n"]
        for b in scattered:
            L+=[f"\n## 在《{page_ctx(b)}》中\n", f"- {title_of(b)}"]
            pid=b.get("parent_id")
            if pid in B and title_of(B[pid]): L.append(f"  - (父块上下文) {title_of(B[pid])[:200]}")
        fn=os.path.join(out,"_mentions-elsewhere.md"); open(fn,"w").write("\n".join(L)+"\n"); written.append(fn)

    print(f"needles={needles} matches={len(mentions)} pages={len(seeds)} scattered={len(scattered)}")
    for fn in written: print("  wrote", fn)

if __name__=="__main__": main()
