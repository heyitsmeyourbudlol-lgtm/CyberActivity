# Integration proof — Newdrop embed CDN TTL s-maxage=5 (#98)

- **When:** 2026-09-08T04:20Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #97 → tip #98)
- **Branch:** `peer/factory-embed-ttl-5`
- **PR:** [#98](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/98) **MERGED** `2b85531`
- **Product commit:** `eb3039d` — Tighten embed.js CDN TTL to s-maxage=5
- **Needle:** Hard-Fix #88 follow-up · `/embed.js` `s-maxage=5` + `stale-while-revalidate=30` (was 15/60) · AGENT_WORKFLOW + `check:controls` pin
- **Diff scope (UI untouched):**
  - `next.config.ts`
  - `docs/agent/AGENT_WORKFLOW.md` · `docs/playbooks/HARD_FIXES_PLAN.md`
  - `scripts/check-compliance-controls.sh`
  - `CHANGELOG.md` · `AGENT_MEMORY.md`
- **Verify (pre-merge):**
  - `npm test` — **452 passed** / 80 files · EXIT 0
  - `npm run check:controls` — **81 ok · 0 fail** · EXIT 0
  - `npx tsc --noEmit` · EXIT 0
- **Same wave:** [#97](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/97) branch-protection residual · [#92](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/92) embed hotfix path · [#79](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/79) AI draft spend kill
- **Policy:** Backend/CDN headers only; **UI untouched** · **NO PAY**
- **Next step:** closed — Active after #98 left open
