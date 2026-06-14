# TradeBot Research Workflow Integration

Using `agent-workflow-playbook` patterns + `szzg007-web-deep-research` framework.

---

## Current TradeBot Pipeline (Before)
```
Daemon (every 5min)
  → Scout (market scan)
  → Research (token safety check)
  → Execute (buy if signals align)
  → Monitor (price tracking)
```

Single agent, linear flow. Works but:
- No market context research before scouting
- Research is shallow (token safety score only)
- No trend analysis or sector rotation awareness

---

## Proposed Multi-Agent Pipeline (After)
```
Phase 1: MARKET RESEARCH (daily)
  Research Agent → Web search for sector trends
  → Compile into brief (szzg007 format)
  → Feed to Scout

Phase 2: SCOUTING (every 5min)
  Scout Agent → Scan DEXs for candidates
  → Filter against research brief sectors
  → Pass top 3 to Research

Phase 3: DEEP RESEARCH (on-demand)
  Research Agent v2 → Token safety + social sentiment
  → Generate report (szzg007 template)
  → Risk/opp assessment
  → Go/no-go to Executor

Phase 4: EXECUTE (on-demand)
  Executor Agent → Buy/sell with guardrails
  → Log + report

Phase 5: PORTFOLIO REVIEW (weekly)
  Review Agent → Portfolio health check
  → Sizing assessment
  → Strategy adjustments
```

---

## Key Improvements

1. **Context-aware scouting** — Research brief informs what sectors to watch
2. **Deeper due diligence** — Social sentiment + trend analysis before buys
3. **Risk layering** — Market risk (Phase 1) + token risk (Phase 3)
4. **Weekly calibration** — Portfolio review feeds back into sizing

---

## Implementation Steps

### Immediate (no code changes)
- Add daily market research pulse using `web_search`
- Format using `szzg007` report template
- Store in `trading-bot/research/` directory

### Short-term (minor code)
- Modify `scout_v2.py` to read latest research brief
- Filter candidates to match trending sectors
- Add social sentiment check to `research_v2.py`

### Long-term (new cron)
- `TradeBot-DailyResearch` cron (9 AM) — market pulse
- `TradeBot-EveningBrief` cron (6 PM) — portfolio + research alignment

---

## File Locations
- Research reports: `trading-bot/research/YYYY-MM-DD.md`
- Workflow guide: `docs/tradebot-research-workflow-integration.md`
- Skill references: `skills/agent-workflow-playbook/`, `skills/szzg007-web-deep-research/`

---

## Test Results
**Test date:** 2026-06-14
**Topic:** Solana meme coin trends
**Result:** Successfully generated structured report in ~30s using web search + szzg007 template. Patterns from agent-workflow-playbook clearly applicable to current TradeBot pipeline.

**Verdict:** Skills are safe (no executable code), documentation quality is high. Recommend proceeding with integration.

**Actual test run:** 2026-06-14 at 10:23 AM — successful. Report generated at `trading-bot/research/2026-06-14.md` (4,200 bytes, 10 sources, proper szzg007 format with Scout Guidance section).
