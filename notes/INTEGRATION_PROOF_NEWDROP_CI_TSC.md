# Integration proof — Newdrop CI typecheck accountHasFullAccess mock (#71)

- **When:** 2026-09-08T03:54Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #65 → raced past #70; land on tip after #70)
- **Branch:** `peer/factory-ci-tsc-after65`
- **PR:** [#71](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/71) **MERGED** `c0bd331`
- **Product commit:** `4eab303` — Fix CI typecheck for publish-scheduled accountHasFullAccess mock
- **Needle:** TS2556 `unknown[]` spread into typed `accountHasFullAccess` vitest mock after #65 multi-round drain; `npx tsc --noEmit` green
- **Diff scope (UI untouched):**
  - `src/lib/changelog/publish-scheduled.test.ts`
  - `CHANGELOG.md` · `AGENT_MEMORY.md`
- **Follow-up:** [#75](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/75) `7966e3a` scrubbed leftover CHANGELOG conflict markers from rebase onto #70
- **Verify (tip after #75 `7966e3a`):**
  - `npx tsc --noEmit` — EXIT 0
  - `npm test` — **439 passed** / 75 files · EXIT 0
  - `npm run check:controls` — **61 ok · 0 fail** · EXIT 0
- **Policy:** Keep `next build` / CI typecheck green without UI churn; NO PAY
- **Next step:** closed — Active after #75 left open
- **NO PAY**
