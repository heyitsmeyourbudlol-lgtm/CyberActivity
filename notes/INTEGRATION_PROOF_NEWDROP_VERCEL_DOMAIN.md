# Integration proof — Newdrop Vercel domain attach prod gate (#49)

- **When:** 2026-09-08T03:11Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #44 → #49)
- **Branch:** `peer/factory-vercel-domain-prod-gate`
- **PR:** [#49](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/49) **MERGED** `84842ac`
- **Product commit:** `a76617a` — Fail-close Vercel domain attach in production (#48)
- **Needle:** `isVercelDomainsConfigured` · production `manual=false` · verify early-gate · restore no silent skip
- **Diff scope (UI untouched):**
  - `src/lib/changelog/custom-domain.ts` (+ `custom-domain.test.ts`)
  - `src/app/dashboard/actions.ts` (verify + restore)
  - `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md` · `scripts/check-compliance-controls.sh`
- **Verify (merge tip):**
  - `npm test` — **392 passed** / 71 files · EXIT 0
  - `npm run check:controls` — **26 ok · 0 fail** · EXIT 0
- **Policy:** Production custom-domain verify/restore must not half-work without `VERCEL_TOKEN` + `VERCEL_PROJECT_ID`.
- **Next step:** closed — Active after #49 left open
