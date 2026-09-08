# Hub peer verbs (product gravity)

_Needle `OVERSEER_COMMAND_ECOSYSTEM_PLAN_2026_09_07`_ · Gravity product: **Newdrop (CaaS)** — `notes/HUB_GRAVITY_CHOICE.md`

External / product agents should **not** reinvent Automation kit loops.
Run these from the **Automation hub** checkout (or document SSH to CLEAN):

## Life / dispatch

| Verb | When |
|------|------|
| `./scripts/peer pre-dispatch` | Before any product agent spawn from hub |
| `./scripts/peer post-cycle` | After land / before DONE claim |
| `./scripts/peer green` | Health gate |
| `./scripts/peer heal-all` | Verify red / mechanical heal |

## Product / proof

| Verb | When |
|------|------|
| `./scripts/peer a-to-z` | Sequencing lock — next open kit A→Z phase |
| `./scripts/peer kit-run --repo CPT` | Unsupervised adapt→verify→worktree receipt |
| `./scripts/peer product` | External-proof sprint + registry fanout |
| `./scripts/peer product-status` | Cooldown + queue |
| `./scripts/peer factory-sprint` | Launch external-repo cursor-agent lanes |
| `./scripts/peer progress` | Factory readiness (real outcomes) |
| `./scripts/peer github-feedback-fetch` | Pull sanitized GitHub feedback/bug inbox |
| `./scripts/peer github-feedback-list` | Inbox summary |
| `./scripts/peer github-feedback-render` | Markdown for peer review |
| `./scripts/peer production-power` | Refresh PRODUCTION_POWER_SCOREBOARD (`scoreboard-write` alias) |
| `./scripts/peer top10` | Print ranked TOP10_NEXT list |
| `./scripts/peer top10-next` | Highest-rank open TOP10_NEXT item |
| `./scripts/peer top10-refresh` | Re-rank open-first after a land (not while T10-04 GAP) |
| GitHub/IDE track | `notes/GITHUB_IDE_SUPPORT.md` (no Newdrop UI) |

## Factory AI (local specialists)

| Verb | When |
|------|------|
| `./scripts/peer niche-mint …` | New closed-world specialist from work gap |
| `./scripts/peer agent-build …` | Provision role+template+match (Agent Builder) |
| `./scripts/peer agent-who "…"` | Task→worker: which role/template would run |
| `./scripts/peer niche-assist-once` | One assist pass on Active head |
| `./scripts/peer factory-dynamics` | CPU/GPU niche balance snapshot |
| `./scripts/peer niche-bank-status` | Bank ready counts |
| `./scripts/peer niche-bank-eval` | Heldout + WQ smoke |
| `./scripts/peer niche-retrieval` | Retrieve over niche bank index |
| `./scripts/peer niche-n01-practice` | N01 practice eval-only |
| `./scripts/peer kit-progress` | Kit progress JSON snapshot |
| `./scripts/peer dgx-utilization` | DGX util snapshot |
| `./scripts/peer land-hold` | Land-hold age/pause status |

## Commands ecosystem

| Verb | When |
|------|------|
| `./scripts/peer commands-list --pivotal` | Discover verbs |
| `./scripts/peer commands-cycle` | Wake Command Builder |
| `./scripts/peer command-coverage` | Coverage matrix |

## Newdrop note

Product UI/verify stays **native** (`npm test`, `check:controls`) on the Newdrop repo.
Hub verbs cover factory orchestration + proof lanes — not a second product CLI.

Link from product AGENTS / AGENT_WORKFLOW: run hub verbs for factory/proof; keep elegant-statue product work in-repo.

