# Integration proof — Newdrop Vercel domain detach on trash/clear (#54)

- **When:** 2026-09-08T03:20Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #53 → #54)
- **Branch:** `peer/factory-orphan-vercel-detach`
- **PR:** [#54](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/54) **MERGED** `9cbe5fa`
- **Product commit:** `918ffd3` — Fail-close Vercel domain detach on trash/clear (#50)
- **Needle:** `detachDomainFromVercel` · production `vercel_not_configured` · `custom_domain_verified_at` clear · Hard-fix #50
- **Diff scope (UI untouched):**
  - `src/lib/changelog/custom-domain.ts` (+ `custom-domain.test.ts`)
  - `src/app/dashboard/actions.ts` (`deleteProject` + domain clear)
  - `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md` · `scripts/check-compliance-controls.sh`
- **Verify (merge tip `9cbe5fa`):**
  - `npm test` — **411 passed** / 73 files · EXIT 0
  - `npm run check:controls` — **39 ok · 0 fail** · EXIT 0
- **Policy:** Production trash/clear must not leave orphan Vercel Domains API entries when credentials missing; soft-delete stops custom-host routing via `custom_domain_verified_at=null`.
- **Next step:** closed — Active after #54 left open
