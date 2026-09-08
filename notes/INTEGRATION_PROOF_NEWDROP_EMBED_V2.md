# Integration proof — Newdrop versioned embed.v2.js dual-serve (#104)

- **When:** 2026-09-08T04:24Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS`
- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #97/#100 tip → #104)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/104
  - branch `peer/factory-hf62-embed-v2`
  - product commit `ceb73cc`
  - merge commit `0e993dd63d69df8fc2b760665f7f7f130c8270e9` on `main`
- **Needle:** Hard-Fix #62 · `/embed.v2.js` rewrite → `/embed.js` · matching `s-maxage=5` headers · AGENT_WORKFLOW cutover note · `check:controls` pins
- **Native verify (tip after merge):**
  - `npm test` — **452 passed** EXIT 0
  - `npm run check:controls` — **86 ok · 0 fail** EXIT 0
- **UI:** untouched · **NO PAY**
- **Supersedes:** open duplicate [#99](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/99) closed
- **Next step:** closed — tip after #104; Active after #104 open
