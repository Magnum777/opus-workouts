# Opus To-Do List

> Read by the daily brief cron every morning at 7am.
> Mark items [x] when done. Add new items with priority and due date.

## Priority 1 — Blocked (Needs Opus)

- [ ] **Get Google AdSense publisher ID** — Script ready (`add_analytics_adsense.py`), blocked until Opus provides ca-pub-XXXXXXX. Apply at <https://www.google.com/adsense>
- [ ] **Get Google Analytics 4 measurement IDs** — Need GA4 IDs for aitoolalliance.com and aicofounderstack.com (aibusinessinsider already has GA)
- [ ] **Create Beehiiv account** — Go to <https://beehiiv.com>, set up "AI Tools That Actually Work" newsletter, add API key to `.secrets` as `BEEHIIV_API_KEY`
- [ ] **Decide on SitePulse AI** — Build MVP (2 weeks) or keep as concept only? See `docs/wp-audit-plugin/CONCEPT.md`
- [ ] **Approve internal link builder for live run** — 204 cross-site link opportunities found in dry run. Running for real modifies live WP posts. See `scripts/internal_link_builder.py`

## Priority 2 — Ready to Execute (Nova can do when approved)

- [ ] **Deploy recommendation widget to aitoolalliance** — Run `python scripts/recommendation_widget.py deploy`. 28 tools, 6 categories, affiliate tracking, GA4 events.
- [ ] **Run affiliate link injector dry run on all 3 sites** — `python scripts/affiliate_injector.py scan <site>` then `inject-all --dry-run`. 25-product registry ready.
- [ ] **Add GA to aitoolalliance and aicofounderstack** — Once GA4 IDs are provided, run `python scripts/add_analytics_adsense.py add-ga`
- [ ] **Add AdSense to all 3 sites** — Once publisher ID is provided, run `python scripts/add_analytics_adsense.py add-adsense`
- [ ] **TradeBot decision** — 6 crons still disabled, portfolio ~$103. Revive with strategy or kill entirely?

## Priority 3 — Backlog

- [ ] **Wire UPLOAD_POST_API_KEY** — Twitter/Bluesky posting for EveOnion and Kybernauts (blocked, Opus said revisit later)
- [ ] **Explore newsletter monetization** — Once Beehiiv is set up, configure ad network + affiliate links in each issue
- [ ] **Run content quality validator on all recent posts** — `python scripts/content_quality_validator.py check --all`
- [ ] **Set up proactive website monitoring alerts** — site_monitor.py is wired into ops-assessment, but could add Discord webhook alerts for downtime
- [ ] **Review and clean up ontology** — 90 entries, validate stale data quarterly

## Priority 4 — Older / On Hold

- [ ] **RateMyFC — staging site + real data testing** — 6 PHP bugs fixed, mockup built (July 21). Staging site not set up yet. Needs EVE SSO callback URL for live testing.
- [ ] **KyberAPM — 13 feedback items from Harv** — Repo rebranded to Magnum777/kyber-apm. Feedback items need triage and fixes.
- [ ] **UniFi network** — Flat network confirmed permanent. Guest portal branded and working. VLANs abandoned. No outstanding issues.
- [ ] **EVE Forum Bump** — Needs browser automation + EVE SSO credentials. Was working May 27, may need re-auth.
- [ ] **Stale docs cleanup** — Several workspace docs reference old install (SYSTEMS.md, SUBMIND_INTEGRATION.md, LOCAL-AI-AUTOMATION.md reference fantasy JS SDK). Needs audit.
- [ ] **P2 skill integrations** — task-prism, ontology+cogmem were deferred June 14. Cogmem needs WSL/Ollama setup.
- [ ] **Discord @mention test** — Confirm bot responds in #nova when @mentioned (from April, never verified)

## Done

- [x] ~~Restore deleted scripts from NAS backup~~ (Aug 2)
- [x] ~~Code standards audit (23 scripts)~~ (Aug 2)
- [x] ~~Error handling audit (10 scripts)~~ (Aug 2)
- [x] ~~Unified credential helper (creds.py)~~ (Aug 2)
- [x] ~~Content analytics dashboard~~ (Aug 2)
- [x] ~~Cron health monitor~~ (Aug 2)
- [x] ~~Cron audit (29 crons, uniform failure alerts)~~ (Aug 2)
- [x] ~~Cron prompt audit (15 fixes)~~ (Aug 2)
- [x] ~~Amazon affiliate dynamic queue system~~ (Aug 2)
- [x] ~~Proactive monitoring (site_monitor, content quality)~~ (Aug 2)
- [x] ~~Incident response process (P0-P3)~~ (Aug 2)
- [x] ~~Communication protocol (5 rules)~~ (Aug 2)
- [x] ~~5 monetization tools built~~ (Aug 2)
- [x] ~~UniFi guest portal branding~~ (June 14-15)
- [x] ~~RateMyFC 6 PHP bugs fixed~~ (July 21)
- [x] ~~KyberAPM rebrand + Harv feedback~~ (July 17-18)
- [x] ~~P0+P1 skill integrations~~ (June 14)