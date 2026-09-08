# Integration proof — Newdrop PSL-aware apex hostname (#58)

- **When:** 2026-09-08T03:31Z
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #54 → #58)
- **Branch:** `peer/factory-psl-apex-hostname`
- **PR:** [#58](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/58) **MERGED** `1decadd`
- **Product commit:** `a7f5756` — PSL-aware apex hostname check for multi-part TLDs (#45)
- **Needle:** `MULTI_PART_PUBLIC_SUFFIXES` · `isApexHostname` · `foo.co.uk` apex · `updates.foo.co.uk` allowed · Hard-fix #45
- **Diff scope (UI untouched):**
  - `src/lib/changelog/custom-domain.ts` (+ `custom-domain.test.ts`)
  - `CHANGELOG.md` · `AGENT_MEMORY.md` · `docs/playbooks/HARD_FIXES_PLAN.md` · `scripts/check-compliance-controls.sh`
- **Verify (merge tip):**
  - `npm test` — **415 passed** / 73 files · EXIT 0
  - `npm run check:controls` — **41 ok · 0 fail** · EXIT 0
- **Policy:** Multi-part public suffixes must not misclassify customer subdomains as apex.
- **Next step:** closed — Active after #58 left open
