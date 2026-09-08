# Integration proof — Newdrop operator secrets rotation (#62)

- **When:** 2026-09-08T03:45Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #61 → tip #62)
- **Branch:** `peer/factory-secrets-rotation-69`
- **PR:** [#62](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/62) **MERGED**
  - merge commit `80ccb477a3e057887f174846c59f2b58bb602dc3` on `main`
  - product `5188603` — Close Hard-fix #69: secrets rotation runbook + dual-key expiry
- **Needle:** Hard-fix #69 closed — `docs/playbooks/SECRETS_ROTATION.md`; SECURITY_AUDIT cron≠admin; containment `rotate_key` → `dual_key_expires_at`; admin/cron 503 fail-closed already on tip
- **Diff scope (UI untouched):**
  - `docs/playbooks/SECRETS_ROTATION.md` (new)
  - `docs/playbooks/HARD_FIXES_PLAN.md` · `SECURITY_AUDIT.md` · `LONG_TERM.md` · `AGENT_WORKFLOW.md`
  - `src/app/api/admin/containment/route.ts` + `routes-fail-closed.test.ts`
  - `scripts/check-compliance-controls.sh` · `CHANGELOG.md` · `AGENT_MEMORY.md`
- **Verify (merge tip):**
  - `npm test` — **425 passed** / 75 files · EXIT 0
  - `npm run check:controls` — **50 ok · 0 fail** (51 with local AAL2) · EXIT 0
- **Policy:** Operator secret rotation runbook + dual-key window visibility; cron never accepts ADMIN bearer.
- **Next step:** closed — tip advanced through [#64](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/64); Active after #64 open
- **NO PAY**
