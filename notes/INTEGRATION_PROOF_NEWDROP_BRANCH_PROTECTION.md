# Integration proof — Newdrop branch-protection soft gate (#97)

- **When:** 2026-09-08T04:18Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #70 → tip advanced; landed #97 after #92)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/97
  - branch `peer/factory-hf83-branch-protection-residual`
  - product commit `49574f0`
  - merge commit `151ae074d03ac45ef1f4d3b6a68f319f9fa60d78` on `main`
- **Needle:** AGENT_WORKFLOW `Branch protection (Hard-Fix #83)` · SECURITY_AUDIT §21.3 Pro residual · Actions job `test` soft gate · never open repo public
- **Hard-Fix:** #83 (soft gate documented; classic branch protection remains Pro residual)
- **Native verify:**
  - `npm test` — **452 passed** EXIT 0
  - `npm run check:controls` — **81 ok · 0 fail** EXIT 0
  - GitHub Actions `test` SUCCESS (Vercel rate-limit fail OK)
- **UI:** untouched · **NO PAY**
- **Residual:** Enable required checks on `main` when GitHub Pro/Team is available
