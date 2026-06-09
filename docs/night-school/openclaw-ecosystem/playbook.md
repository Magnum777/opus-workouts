# OpenClaw Ecosystem Monitoring

**Purpose:** Track OpenClaw updates, community issues, and best practices to keep our stack current and secure.

**Monitoring Schedule:** Check during each Night School session (daily 8pm ET)

**Last Updated:** 2026-04-29

---

## Sources to Monitor

### Primary
1. **GitHub** - https://github.com/openclaw/openclaw
   - Releases: New versions, breaking changes
   - Issues: Common problems, workarounds
   - Discussions: Community patterns

2. **Discord** - OpenClaw official server
   - #announcements: Critical updates
   - #general: User-reported issues
   - #dev: Technical discussions

3. **Documentation** - https://docs.openclaw.ai
   - Changelog: Feature additions
   - Migration guides: Breaking changes

### Secondary
- Reddit r/OpenClaw (community tips)
- Twitter/X @openclaw (announcements)
- Blog posts and tutorials

---

## Monitoring Checklist

### Daily (During Night School)
- [ ] Check GitHub releases for new versions
- [ ] Review recent GitHub issues (last 24h)
- [ ] Scan Discord #announcements
- [ ] Check our system against known issues

### Weekly
- [ ] Review closed issues for patterns
- [ ] Check if any deprecated features affect us
- [ ] Update AGENT-SYNC.md with relevant findings
- [ ] Review this playbook for needed updates

### On New Release
- [ ] Read release notes thoroughly
- [ ] Check for breaking changes
- [ ] Test in non-production first
- [ ] Update configs as needed
- [ ] Document any migration steps

---

## Known Issues & Workarounds

### Current Version: 2026.4.15

#### Issue: Cron jobs with `sessionTarget: "isolated"` may timeout
**Status:** Known, workaround exists  
**GitHub:** Issue #44257  
**Workaround:** Use explicit `timeoutSeconds` in payload, switch to `agent:` target if persistent needed  
**Our Status:** ✅ Implemented - all crons have timeouts

#### Issue: gpt-oss:120b-cloud 500 errors
**Status:** Intermittent cloud endpoint issue  
**Workaround:** Use kimi-k2.5:cloud as primary, gpt-oss as fallback  
**Our Status:** ✅ Fixed - changed default model

#### Issue: Context overflow with qwen3:14b (24K limit)
**Status:** By design - small model  
**Workaround:** Use compaction, switch to larger model for big sessions  
**Our Status:** ✅ Documented in agentic-ai-lessons playbook

#### Issue: Browser automation flaky
**Status:** Known limitation  
**Workaround:** Prefer APIs over browser when possible  
**Our Status:** ⚠️ Monitoring - Reddit crons affected

---

## Version Tracking

| Version | Date | Breaking Changes | Our Action |
|---------|------|------------------|------------|
| 2026.4.15 | Current | None major | Running stable |
| 2026.3.13 | Apr 2026 | Cron behavior changed | Updated configs |
| 2026.3.11 | Mar 2026 | Isolated session fixes | Added timeouts |

---

## Action Items

### Immediate
- [ ] Monitor gpt-oss stability - if continues, remove from fallbacks
- [ ] Check if 2026.4.16 release imminent

### Short Term
- [ ] Evaluate new features in recent releases
- [ ] Consider migrating Reddit crons to API-based (not browser)

### Long Term
- [ ] Track multi-agent orchestration improvements
- [ ] Monitor for native tiering/routing features

---

## Integration Notes

### When to Update AGENT-SYNC.md
- New security advisories → Immediate
- Performance improvements → Next maintenance window
- New features → Evaluate first, then document
- Bug fixes affecting us → After testing fix

### When to Update Other Playbooks
- Cron behavior changes → Update agentic-ai-lessons
- Model/provider changes → Update cron-model-tiering
- Trading/security changes → Update relevant playbooks

---

## Community Patterns Worth Adopting

### From GitHub Discussions
- **Model routing:** Some users use OpenRouter for automatic fallback
- **Session management:** Compact aggressively, many small sessions > few large
- **Cron design:** Keep payloads simple, do complex work in scripts

### From Discord
- **Debugging:** Use `openclaw status --deep` for detailed diagnostics
- **Performance:** Local Ollama for speed, cloud for quality
- **Security:** Regular `openclaw security audit`

---

*Check during each Night School session. Update with findings.*
