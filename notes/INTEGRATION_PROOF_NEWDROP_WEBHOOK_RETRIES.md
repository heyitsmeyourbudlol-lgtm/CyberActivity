# Integration proof — Newdrop webhook retries honesty (#78)

- **Assignment:** `[top10] Newdrop production — next meaningful non-UI merge` (after #79 → #78)
- **Branch:** `peer/factory-billing-stripe-types-71`
- **PR:** [#78](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/78) **MERGED** `607d5ac` · product `7ade862`
- **Verify:** `npm test` 440 PASS · `check:controls` 62ok · `npx tsc --noEmit` EXIT 0
- **Scope:** ops — export `WEBHOOK_RETRIES`; Hard-fix #58 notes Slack/Discord/Teams share `postJsonWebhook` retries; billing reconcile Stripe status typing; **UI untouched** · NO PAY
- **Same wave:** [#79](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/79) AI draft kill · [#75](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/75) CHANGELOG scrub · [#71](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/71) CI tsc
- **Next step:** closed — leave Active after #78 open
