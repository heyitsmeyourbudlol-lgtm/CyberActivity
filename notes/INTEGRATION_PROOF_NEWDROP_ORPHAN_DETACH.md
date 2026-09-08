# Integration proof — Newdrop Vercel detach orphan guard (#54)

- **When:** 2026-09-08T03:19Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #53 → #54)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/54
  - branch `peer/factory-orphan-vercel-detach`
  - product commit `918ffd3`
  - merge commit `9cbe5fac9ba9ac8c0a26779cbe113f44b3b21976` on `main`
- **Needle:** hard-fix #50 · `detachDomainFromVercel` production fail-closed · `deleteProject` / domain clear await detach · clear `custom_domain_verified_at`
- **Native verify:**
  - `npm test` — **411 passed** EXIT 0
  - `npm run check:controls` — **39 ok · 0 fail** EXIT 0
- **UI:** untouched · **NO PAY**
- **Residual:** Soft-delete keeps `custom_domain` for restore; Domains API detach still depends on live Vercel credentials in production
