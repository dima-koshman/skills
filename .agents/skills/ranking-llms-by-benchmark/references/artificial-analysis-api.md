# Artificial Analysis as a data source

`https://artificialanalysis.ai` is the best single vendor-neutral view of
quality-vs-cost-vs-speed. Two very different ways to get data out of it.

## 1. The v2 REST API (needs `$AA_API_KEY`)

Spec: `https://artificialanalysis.ai/api/v2/openapi` — **YAML, not JSON**, despite the
path. Parse with `yaml.safe_load`.

Auth: `-H "x-api-key: $AA_API_KEY"`. **Free tier allows 100 requests/day** — budget them.

Free-tier keys may only call the `/free` endpoints. `/api/v2/language/models` returns
`403 {"error":"Language models list requires a Pro subscription"}`. Use:

```bash
curl -s "https://artificialanalysis.ai/api/v2/language/models/free?page=1" \
  -H "x-api-key: $AA_API_KEY"
```

Paginated at 200/page; check `pagination.total_pages` and loop (≈590 models over 3 pages,
so the full catalogue costs 3 of your 100 daily requests). Each row gives:

- `evaluations.artificial_analysis_intelligence_index` — general composite
- `evaluations.artificial_analysis_coding_index` — **coding composite (CI)**
- `evaluations.artificial_analysis_agentic_index` — **agentic composite (AG)**
- `pricing.price_1m_{input,output,cache_hit,cache_write}_tokens`
- `performance.median_output_tokens_per_second`, `median_time_to_first_token_seconds`
- `release_date`, `model_creator`

`null` indices mean not-yet-evaluated, not zero. Filter them out; never treat as 0.

**Match on `release_date`, not on the name.** AA versions models aggressively and a
provider may serve an older build under an unversioned ID. Real example: opencode Zen Go
lists `deepseek-v4-flash` dated 2026-04-24, which is AA's `deepseek-v4-flash-0420`
(CI 56.2) — *not* AA's unsuffixed `deepseek-v4-flash`, which is the 0731 build at CI 69.1.
Picking the wrong one overstates quality by 13 index points.

Also note AA splits reasoning effort into separate slugs (`gpt-5-6-luna` is the *max*
effort variant; `-low`/`-medium`/`-high`/`-xhigh`/`-non-reasoning` are separate rows with
very different scores). Match the effort level you actually configure.

## 2. The agent leaderboards (no API, no quota)

`https://artificialanalysis.ai/agents/coding-agents` measures a whole *harness + model*
combination — Coding Agent Index, **Cost per Task**, **Time per Task** — which the v2 API
does not expose at all. There is no `/agents` endpoint; don't go looking for one.

The page is a Next.js RSC app. Two extraction routes:

- **Charts only (10 rows each):** four `<script type="application/ld+json">` Dataset blocks
  hold the top-10 for each chart. Easy, but truncated.
- **Full table (~52 rows):** reconstruct the flight payload, then brace-match each record.

```python
parts = re.findall(r'self\.__next_f\.push\(\[1,(".*?")\]\)</script>', html, re.S)
flight = "".join(json.loads(p) for p in parts)
# then scan for {"id":"<hex>","agentName": ... and brace-match to the closing }
```

Each record carries `displayLabel`, `indexScore`, per-eval breakdown (DeepSWE,
SWE-Atlas-QnA, Terminal-Bench v2) and a `mean` block with `costUsd`, `agentWallTimeSec`,
**`steps`**, `inputTokens`, `cacheTokens`, `outputTokens`, `cacheHitRate`.

`mean.steps` (median ≈84 API calls per coding task) is the number that converts a
per-request price into a per-task price. It is not available anywhere else and it varies
2-3x across models — Grok 4.5 finishes in ~61 steps, GLM-5.1 takes ~174.

`totalTokens` double-counts: it equals `inputTokens + cacheTokens + outputTokens`, but
`cacheTokens` is a *subset* of `inputTokens`. Compute fresh tokens as
`inputTokens - cacheTokens`.

## Reconciling AA cost against a provider's price sheet

Cost per task from a price sheet is only trustworthy if you check it against AA's measured
`costUsd`. Doing this for opencode Zen Go reconciled to within 1% for GLM-5.2, GLM-5.1,
Kimi K2.6 and DeepSeek V4 Pro — and revealed three real effects that a naive calculation
misses entirely:

| Model | Naive (cached) | AA measured | Why |
|---|---|---|---|
| Grok 4.5 | $0.96 | $2.59 | Ran in the **>200K context tier** — double rates. `1.72M×$0.60 + 0.10M×$4 + 40k×$12 = $2.59` exactly. |
| GPT 5.6 Luna | $0.33 | $1.57 | Got **almost no effective cache credit** in the harness. |
| Qwen3.7 Plus | $0.55 | $6.23 | Same, plus the >256K tier. |
| GLM-5.2 | $2.82 | $6.51 | Only achieved a **34% cache hit rate** — worst on the board (median is 93%). |

**Cache-hit rate dominates agentic cost**, and it is a property of the harness/provider
pair, not of the price sheet. Quote cost as a band — cached-optimistic to no-cache — and
say which end the measured data lands on. A single point estimate is false precision.
