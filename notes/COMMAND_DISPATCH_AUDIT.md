# Command dispatch audit

_Generated 2026-09-08T03:17:56Z_ · Needle `OVERSEER_COMMAND_ECOSYSTEM_PLAN_2026_09_07`

**Status:** `improve` · peer/(peer+raw) ratio = **0.111**

| Signal | Hits |
|--------|------|
| pre-dispatch / plan-gate | 55 |
| post-cycle / done-gate | 4 |
| `./scripts/peer …` | 1 |
| raw `python3 scripts/` | 8 |

Agents should call ./scripts/peer pre-dispatch before spawn and post-cycle after land; prefer peer verbs over raw python3 scripts/.

```bash
./scripts/peer command-dispatch-audit
./scripts/peer pre-dispatch
./scripts/peer post-cycle
```

