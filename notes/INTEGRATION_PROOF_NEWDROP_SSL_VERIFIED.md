# Integration proof — Newdrop custom domain SSL-ready gate (#59)

- **When:** 2026-09-08T03:32Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #58 → #59)
- **Branch:** `peer/factory-ssl-verified-gate`
- **PR:** [#59](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/59) **MERGED** `b67c2fa`
- **Product commit:** `d7d1227` — Fail-close custom domain verified_at until SSL ready (#47)
- **Needle:** Hard-fix #47 · `verifyCustomDomain` stamps `custom_domain_verified_at` only when `getVercelDomainStatus().sslReady` · Refresh SSL can complete stamp
- **Diff scope (no redesign):**
  - `src/app/dashboard/actions.ts`
  - `src/lib/changelog/custom-domain.test.ts`
  - `scripts/check-compliance-controls.sh` · `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md`
- **Verify (merge tip worktree):**
  - `npm test` — **424 passed** / 75 files · EXIT 0
  - `npm run check:controls` — **46 ok · 0 fail** · EXIT 0
- **Policy:** Pending TLS must not mark domain live (Verified badge / custom-host routing); **UI untouched**.
- **Next step:** closed — Active after #59 left open
- **NO PAY**
