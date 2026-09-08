# Integration proof — Newdrop scheduled-publish Hobby cron drain (#65)

- **When:** 2026-09-08T03:49Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #64 → #65)
- **Branch:** `peer/factory-sched-publish-drain-v2`
- **PR:** [#65](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/65) **MERGED** `7f320cf`
- **Product commit:** `48a4ca9` — Drain scheduled-publish backlog under Hobby cron (#52/#55)
- **Needle:** Hard-fix #52/#55 · cron `{ limit: 100, maxRounds: 5 }` FIFO `scheduled_for` · `backlogRemaining` + `drained` · dashboard single-round
- **Diff scope (no redesign):**
  - `src/lib/changelog/publish-scheduled.ts` · `.test.ts`
  - `src/app/api/cron/publish-scheduled/route.ts` · `.test.ts`
  - `scripts/check-compliance-controls.sh` · `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md`
- **Verify (merge tip worktree):**
  - `npm test` — **432 passed** / 75 files · EXIT 0
  - `npm run check:controls` — **56 ok · 0 fail** · EXIT 0
- **Policy:** Hobby daily cron drains backlog without widget traffic; **UI untouched**.
- **Next step:** closed — Active after #65 left open
- **NO PAY**
