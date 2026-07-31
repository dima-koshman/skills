#!/usr/bin/env python3
"""Rank opencode Zen Go models by Artificial Analysis benchmarks against the shared usage pool.

Fetches everything live:
  - model list + prices + usage multipliers + request estimates  <- opencode.ai/docs/go
  - prices, context limits, release dates                        <- models.dev/api.json
  - Coding / Agentic / Intelligence indices, tok/s               <- artificialanalysis.ai v2 API
  - measured steps-per-task for agentic coding                   <- artificialanalysis.ai/agents/coding-agents

Usage:  AA_API_KEY=... python3 rank_opencode_go.py [--json out.json]

Costs 3 of the 100/day free-tier AA API requests. The coding-agents scrape costs none.
"""

import argparse
import html
import json
import os
import re
import statistics
import sys
import urllib.request

DOCS_GO = "https://opencode.ai/docs/go"
MODELS_DEV = "https://models.dev/api.json"
AA_MODELS = "https://artificialanalysis.ai/api/v2/language/models/free"
AA_AGENTS = "https://artificialanalysis.ai/agents/coding-agents"

# opencode Zen Go account limits, in "usage dollars" (opencode.ai/docs/go).
# ONE pool shared across every model - not a per-model budget.
POOL = {"5h": 12.0, "week": 30.0, "month": 60.0}


def get(url, headers=None):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", **(headers or {})}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def tables(page):
    """Every <table> on an HTML page, as a list of rows of cell strings."""
    out = []
    for tbl in re.findall(r"<table[^>]*>(.*?)</table>", page, re.DOTALL):
        rows = []
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, re.DOTALL):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.DOTALL)
            rows.append(
                [html.unescape(re.sub("<[^>]+>", "", c)).strip() for c in cells]
            )
        if rows:
            out.append(rows)
    return out


def money(s):
    s = s.replace("$", "").replace(",", "").strip()
    if s in ("-", "", "Free"):
        return 0.0
    return float(s)


def fetch_zen_go():
    """Model id -> prices, usage multiplier, opencode's own request estimates."""
    page = get(DOCS_GO)
    tbs = tables(page)
    price, usage, reqs, ids = {}, {}, {}, {}
    for rows in tbs:
        head = [c.lower() for c in rows[0]]
        if "input" in head and "usage" in head:  # pricing + usage-multiplier table
            for r in rows[1:]:
                if len(r) < 6:
                    continue
                name = re.sub(
                    r"\s*\(.*?\)", "", r[0]
                ).strip()  # drop "(<= 272K tokens)"
                if name in price:  # keep the first (cheapest) context tier
                    continue
                price[name] = {
                    "input": money(r[1]),
                    "output": money(r[2]),
                    "cache_read": money(r[3]),
                    "cache_write": money(r[4]),
                }
                usage[name] = money(r[5])
        elif "requests per month" in head:  # opencode's derived request estimates
            for r in rows[1:]:
                if len(r) >= 4:
                    reqs[r[0].strip()] = int(r[3].replace(",", ""))
        elif "model id" in head:  # name -> api id
            for r in rows[1:]:
                if len(r) >= 2:
                    ids[r[0].strip()] = r[1].strip()

    # normalise display names ("MiMo-V2.5" vs "MiMo V2.5") to the api id
    def key(n):
        return re.sub(r"[^a-z0-9.]", "", n.lower())

    by_id = {}
    idmap = {key(n): i for n, i in ids.items()}
    for name, p in price.items():
        mid = idmap.get(key(name))
        if not mid:
            continue
        by_id[mid] = {
            "name": name,
            "price": p,
            "usage": usage[name],
            "req_month": reqs.get(name)
            or next((v for k, v in reqs.items() if key(k) == key(name)), None),
        }
    return by_id


def fetch_models_dev():
    cat = json.loads(get(MODELS_DEV))["opencode-go"]["models"]
    return {
        k: {
            "release": v.get("release_date"),
            "context": v.get("limit", {}).get("context"),
            "cost": v.get("cost", {}),
        }
        for k, v in cat.items()
    }


def fetch_aa_models(api_key):
    rows, page, pages = [], 1, 1
    while page <= pages:
        d = json.loads(get(f"{AA_MODELS}?page={page}", {"x-api-key": api_key}))
        rows += d["data"]
        pages = d["pagination"]["total_pages"]
        page += 1
    return rows


def fetch_aa_agents():
    """Full coding-agents leaderboard from the RSC flight payload (no API quota)."""
    page = get(AA_AGENTS)
    parts = re.findall(
        r'self\.__next_f\.push\(\[1,(".*?")\]\)</script>', page, re.DOTALL
    )
    flight = "".join(json.loads(p) for p in parts)
    recs = []
    for m in re.finditer(r'\{"id":"[0-9a-f]{16,}","agentName":', flight):
        depth, instr, esc = 0, False, False
        for j in range(m.start(), len(flight)):
            c = flight[j]
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = not instr
            elif not instr and c == "{":
                depth += 1
            elif not instr and c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        recs.append(json.loads(flight[m.start() : j + 1]))
                    except json.JSONDecodeError:
                        pass
                    break
    return recs


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def match_aa(mid, release, aa_rows):
    """Pick the AA row for an opencode-go model id.

    AA splits one model into many slugs: reasoning-effort variants (`-low`, `-high`,
    `-non-reasoning`), sibling models (`-pro`), and dated rebuilds (`-0420`). Only the
    base slug and a date suffix denote the same model at full effort, so restrict to
    those first - otherwise `mimo-v2.5` matches `mimo-v2-5-pro` and `gpt-5.6-luna`
    matches `gpt-5-6-luna-low` (CI 44.2 instead of 71.4).

    Then prefer an exact release-date match, because providers serve older builds under
    unversioned ids: opencode's deepseek-v4-flash (2026-04-24) is AA's
    deepseek-v4-flash-0420, not AA's unsuffixed (and much stronger) deepseek-v4-flash.
    """
    n = norm(mid)
    cands = [r for r in aa_rows if norm(r["slug"]).startswith(n)]
    if not cands:
        return None
    same = [
        r for r in cands if norm(r["slug"])[len(n) :].isdigit() or norm(r["slug"]) == n
    ]
    pool = same or cands
    dated = [r for r in pool if r.get("release_date") == release]
    return min(dated or pool, key=lambda r: len(r["slug"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="write the full table here")
    args = ap.parse_args()
    key = os.environ.get("AA_API_KEY")
    if not key:
        sys.exit("AA_API_KEY not set")

    go, md = fetch_zen_go(), fetch_models_dev()
    aa_rows, agents = fetch_aa_models(key), fetch_aa_agents()

    # Measured steps per coding task, indexed two ways. `exact` keys on the full agent
    # label ("GPT-5.6 Luna (max)") so steps come from the same reasoning-effort variant
    # the AA index came from; `loose` strips the effort suffix as a fallback.
    steps_exact, steps_loose = {}, {}
    for a in agents:
        s = a.get("mean", {}).get("steps")
        if not s:
            continue
        name = a["display"]["model"]
        steps_exact.setdefault(norm(name), []).append(s)
        steps_loose.setdefault(norm(re.sub(r"\(.*?\)", "", name)), []).append(s)
    med_steps = statistics.median(
        [a["mean"]["steps"] for a in agents if a.get("mean", {}).get("steps")]
    )

    rows, unmatched = [], []
    for mid, g in sorted(go.items()):
        info = md.get(mid, {})
        aa = match_aa(mid, info.get("release"), aa_rows)
        if not aa:
            unmatched.append(mid)
            continue
        ev = aa["evaluations"]
        st = steps_exact.get(norm(aa["name"])) or steps_loose.get(norm(g["name"]))
        steps, measured = (statistics.median(st), True) if st else (med_steps, False)
        req = g["req_month"]
        tasks = req / steps if req else None
        # One task's draw on the shared monthly pool. opencode's req_month already
        # folds in the usage multiplier, so pool$ = monthly_pool / tasks_per_month.
        pool_per_task = POOL["month"] / tasks if tasks else None
        rows.append(
            {
                "model": mid,
                "name": g["name"],
                "usage_multiplier": g["usage"],
                "burn_vs_best": round(POOL["month"] / g["usage"], 1),
                "coding_index": ev["artificial_analysis_coding_index"],
                "agentic_index": ev["artificial_analysis_agentic_index"],
                "intelligence_index": ev["artificial_analysis_intelligence_index"],
                "aa_slug": aa["slug"],
                "aa_release": aa.get("release_date"),
                "oc_release": info.get("release"),
                "steps_per_task": round(steps),
                "steps_measured": measured,
                "req_month": req,
                "tasks_month": round(tasks) if tasks else None,
                "pool_usd_per_task": round(pool_per_task, 2) if pool_per_task else None,
                "tasks_per_5h": int(POOL["5h"] / pool_per_task)
                if pool_per_task
                else None,
                "tps": aa["performance"]["median_output_tokens_per_second"],
                "context": info.get("context"),
                "price": g["price"],
            }
        )

    # Cross-check the docs price sheet against models.dev and AA. Real discrepancies show
    # up here: Grok 4.5 cache read is $0.30 on opencode.ai/docs/go but $0.50 in both
    # models.dev and AA.
    disagree = []
    for r in rows:
        md_cost = md.get(r["model"], {}).get("cost") or {}
        aa_price = next((x for x in aa_rows if x["slug"] == r["aa_slug"]), {}).get(
            "pricing", {}
        )
        for ours, theirs, label in (
            ("input", "price_1m_input_tokens", "input"),
            ("output", "price_1m_output_tokens", "output"),
            ("cache_read", "price_1m_cache_hit_tokens", "cache read"),
        ):
            mine = r["price"][ours]
            for src, val in (
                ("models.dev", md_cost.get(ours)),
                ("AA", aa_price.get(theirs)),
            ):
                if val is not None and abs(val - mine) > max(0.02 * mine, 0.005):
                    disagree.append(
                        f"   {r['model']:19} {label:10} docs ${mine} vs {src} ${val}"
                    )

    rows.sort(key=lambda r: -(r["coding_index"] or 0))
    print(
        f"opencode Zen Go - shared pool ${POOL['month']:.0f}/mo, ${POOL['week']:.0f}/wk, "
        f"${POOL['5h']:.0f}/5h  |  median {med_steps:.0f} steps/task\n"
    )
    print(
        f"{'model':19}{'CI':>5}{'AG':>5}{'II':>5}{'mult':>6}{'burn':>6}{'req/mo':>9}"
        f"{'steps':>7}{'tasks/mo':>9}{'pool$/task':>11}{'/5h':>5}{'tps':>7}"
    )

    def f(v):
        """Render a missing metric as '-' rather than 'None'."""
        return "-" if v is None else v

    for r in rows:
        print(
            f"{r['model']:19}{f(r['coding_index'])!s:>5}{f(r['agentic_index'])!s:>5}"
            f"{f(r['intelligence_index'])!s:>5}{r['usage_multiplier']:5.0f}x{r['burn_vs_best']:5.0f}x"
            f"{f(r['req_month'])!s:>9}{r['steps_per_task']:6}{'' if r['steps_measured'] else '~'}"
            f"{f(r['tasks_month'])!s:>9}{f(r['pool_usd_per_task'])!s:>11}"
            f"{f(r['tasks_per_5h'])!s:>5}{f(r['tps'])!s:>7}"
        )
    print(
        "  ~ steps estimated from the median (model absent from the coding-agents board)"
    )
    if unmatched:
        print(f"  no AA benchmark data: {', '.join(unmatched)}")

    for label, k in (("CODING", "coding_index"), ("AGENTIC", "agentic_index")):
        front = [
            a
            for a in rows
            if a[k]
            and a["tasks_month"]
            and not any(
                b[k]
                and b["tasks_month"]
                and b[k] >= a[k]
                and b["tasks_month"] > a["tasks_month"]
                for b in rows
                if b is not a
            )
        ]
        print(f"\nPareto ({label} index vs tasks/month on the shared pool):")
        for r in sorted(front, key=lambda x: -x["tasks_month"]):
            print(
                f"   {r['model']:19} {r[k]:5}  {r['tasks_month']:5} tasks/mo  "
                f"(${r['pool_usd_per_task']}/task)"
            )

    if disagree:
        print(
            "\nPrice sheets disagree (docs vs other sources) - verify before quoting:"
        )
        print("\n".join(sorted(set(disagree))))

    over = [
        r
        for r in rows
        if r["pool_usd_per_task"] and r["pool_usd_per_task"] > POOL["5h"]
    ]
    if over:
        print("\nWARNING - one full-size task exceeds the entire $12 5-hour window:")
        for r in over:
            print(f"   {r['model']:19} ${r['pool_usd_per_task']}/task")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(rows, fh, indent=1)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
