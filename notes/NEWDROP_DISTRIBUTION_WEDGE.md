# Newdrop distribution wedge (Top 10 phase 2)

_Gravity product: Newdrop (CaaS)_ · Policy: [TOP10_PRODUCTION_POWER.md](TOP10_PRODUCTION_POWER.md)

## Chosen wedge

**Changelog-as-SEO + founder channel.**

Newdrop already ships a public changelog surface (`caas-changelog`). Every meaningful merge must:

1. Land with a user-visible changelog entry (what changed, why it matters).
2. Be linkable from the public proof page ([FACTORY_PROOF.md](FACTORY_PROOF.md)).
3. Get one founder mention (X/LinkedIn/email) the same week — no paid ads required.

## Why this wedge

- Zero new product surface — uses existing CHANGELOG / PR habit.
- Matches free-desktop factory: production merges *are* the distribution content.
- Compounds: weekly ≥3 merges → weekly public narrative without a separate marketing stack.

## Public SEO surface (non-UI)

| URL | Role |
|-----|------|
| `https://getnewdrop.com/c/getnewdrop` | First-party dogfood What’s New (homepage widget) |
| `https://getnewdrop.com/c/getnewdrop/rss.xml` | First-party What’s New RSS (aggregators / crawl) |
| `https://getnewdrop.com/sitemap.xml` | Marketing crawl map — dogfood HTML + RSS only (never auto-index customer `/c/{slug}`) |
| Repo `CHANGELOG.md` | Keep-a-Changelog sections per merge (source for PR narrative) |

Needle land 2026-09-08: sitemap HTML [#33](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/33) + RSS [#35](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/35) · `SITE_DOGFOOD_SLUG` · `check:controls` CHANGELOG/sitemap/RSS gates — **UI untouched**.

## Checklist (week of 2026-09-07)

- [x] After each Newdrop merge: confirm changelog row exists (PRs #16–#35)
- [x] Update FACTORY_PROOF.md merge table through [#35](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/35)
- [x] SEO: index first-party `/c/getnewdrop` in `/sitemap.xml` — [#33](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/33) merge `3871765` · **UI untouched**
- [x] SEO: index first-party `/c/getnewdrop/rss.xml` in `/sitemap.xml` — [#35](https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/35) merge `293e1ae` · npm test 373 · check:controls 16ok · **UI untouched**
- [x] Scoreboard `--write` (run after land)
- [ ] One founder post linking the public What’s New or a FACTORY_PROOF merge (human — draft below)

## Founder post draft (human — copy/paste)

> Shipped a week of Newdrop hardening in public: Stripe fail-closed paths, webhook SSRF pin, idempotent customer create — and the live What’s New page + RSS are now in our sitemap so the product narrative compounds.  
> What’s New: https://getnewdrop.com/c/getnewdrop  
> RSS: https://getnewdrop.com/c/getnewdrop/rss.xml  
> Proof table: hub `notes/FACTORY_PROOF.md`

## Next week (non-UI)

- [x] After each merge ≥#33: CHANGELOG section + FACTORY_PROOF row same day (through #35)
- [ ] Batch one site-dogfood publish (`node scripts/publish-site-changelog.mjs`) if the week had user-visible ships (max 1/week) — deferred: most ships backend/ops; human may batch after founder post
- [ ] Human: post the draft above (or refresh) once this week
- [x] Keep customer `/c/{slug}` out of marketing sitemap (consent-only; controls grep dogfood HTML + RSS only)

## Non-goals

- Paid ads, agency retainers, multi-channel spray before retention is real.
- Auto-indexing customer changelogs without owner consent.
- UI polish as distribution theater.
