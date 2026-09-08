# Integration proof — Newdrop markdown XSS allowlist (#70)

- **When:** 2026-09-08T03:53Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #65 → #70)
- **Branch:** `peer/factory-markdown-xss-61-land`
- **PR:** [#70](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/70) **MERGED** `ce12588`
- **Product commit:** `e603cd8` — Harden markdown XSS allowlist + fixtures (#61)
- **Needle:** Hard-fix #61 · `CHANGELOG_ALLOWED_TAGS` · svg/math/iframe/cached `body_html` XSS fixtures · `check:controls` pins
- **Diff scope (UI untouched):**
  - `src/lib/changelog/markdown.ts` · `markdown.test.ts`
  - `scripts/check-compliance-controls.sh` · `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md`
- **Verify (merge tip):**
  - `npm test` — **439 passed** / 75 files · EXIT 0
  - `npm run check:controls` — **60 ok · 0 fail** · EXIT 0
- **Policy:** Server sanitize remains source of truth for embed Shadow DOM XSS; allowlist + fixtures pin regressions.
- **Prior tips stamped:** [#59](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/59) SSL · [#58](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/58) PSL · [#56](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/56) backlog
- **Next step:** closed — Active after #70 left open
- **NO PAY**
