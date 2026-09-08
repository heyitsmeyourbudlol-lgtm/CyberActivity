# Integration proof — Newdrop public /c + RSS maintenance fail-closed (#51)

- **When:** 2026-09-08T03:14Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #46/#50 → #51)
- **Branch:** `peer/factory-public-maint-fail-closed`
- **PR:** [#51](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/51) **MERGED** `9fded1e`
- **Product commit:** `8464649` — Fail-close public /c HTML and RSS during maintenance
- **Needle:** `rejectIfMaintenance` on RSS · `getMaintenanceStatus` on `/c/[slug]` · deep health `maintenance` · existing `MaintenanceBanner` only (flaw parity vs API 503)
- **Diff scope (no redesign):**
  - `src/app/c/[slug]/rss.xml/route.ts`
  - `src/app/c/[slug]/page.tsx` (existing banner only — HTML must not keep serving updates while APIs are in maintenance)
  - `src/app/api/health/route.ts`
  - `src/lib/security/maintenance.test.ts`
  - `scripts/check-compliance-controls.sh` · `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md`
- **Verify (merge tip worktree):**
  - `npm test` — **401 passed** / 73 files · EXIT 0
  - `npm run check:controls` — **33 ok · 0 fail** · EXIT 0
- **Policy:** Public HTML/RSS must fail-closed with widget/API maintenance plane; deep health reports maintenance next to `env_kills`.
- **Next step:** closed — Active after #51 left open
- **NO PAY**
