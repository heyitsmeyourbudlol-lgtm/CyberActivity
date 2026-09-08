# Integration proof — Newdrop AI draft URL allowlist (#82)

- **When:** 2026-09-08T04:01Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #78/#79 → tip #82)
- **Branch:** `peer/factory-draft-url-allowlist`
- **PR:** [#82](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/82) **MERGED** `eb9af5b`
- **Product commit:** squash `eb9af5b` — Strip invented URLs from AI changelog draft assist (#77/#79)
- **Needle:** Hard-fix #78/#79 draft path · `aiDraftUpdate` title/body → `stripDisallowedSupportUrls` · complements #79 spend kill (#77) · unit `ai-draft-url-allowlist.test.ts` · controls pin
- **Diff scope (UI untouched):**
  - `src/lib/support/support.ts` · `ai-draft-url-allowlist.test.ts`
  - `scripts/check-compliance-controls.sh`
  - `docs/playbooks/HARD_FIXES_PLAN.md` · `CHANGELOG.md` · `AGENT_MEMORY.md`
- **Verify (merge tip):**
  - `npm test` — **444 passed** / 77 files · EXIT 0
  - `npm run check:controls` — **65 ok · 0 fail** · EXIT 0
- **Same wave:** [#79](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/79) draft spend kill · [#78](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/78) webhook retries · [#71](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/71) CI tsc · [#64](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/64) AI kill+URL
- **Policy:** Backend sanitize only; **UI untouched** · **NO PAY**
- **Next step:** closed — Active after #82 left open
