# Integration proof — Newdrop second Hobby publish nest (#91)

- **When:** 2026-09-08T04:12Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #89 → #91; tip raced past #70/#75)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/91
  - branch `peer/factory-sched-nest-purge-52`
  - product commit `89a5aafb95a9e00c890b1c6a651499dad69b1563`
  - merge commit `dc42aff0379b4749546811c405c5b8cfa210963e` on `main`
- **Needle:** Hard-Fix #52 residual · `/api/cron/purge-abuse` nests multi-round `publishDueScheduledUpdates` (100×5) for second Hobby daily publish tick (03:30 UTC + 05:00 publish-scheduled) · fail-soft nested publish · paid hourly residual
- **Native verify (pre-merge tip):**
  - `npm test` — **452 passed** EXIT 0
  - `npm run check:controls` — **77 ok · 0 fail** EXIT 0
  - `npx tsc --noEmit` EXIT 0
- **UI:** untouched · **NO PAY**
- **Same wave:** [#92](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/92) embed hotfix · [#89](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/89) CodeQL · [#88](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/88) soft budget
- **Next step:** closed — leave Active after #92 open
