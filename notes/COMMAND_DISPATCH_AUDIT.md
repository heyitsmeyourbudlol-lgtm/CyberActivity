# Command dispatch audit

_Generated 2026-09-08T02:54:51Z_ · Needle `OVERSEER_COMMAND_ECOSYSTEM_PLAN_2026_09_07`

**Status:** `ok` · peer/(peer+raw) ratio = **1.0**

| Signal | Hits |
|--------|------|
| pre-dispatch / plan-gate | 158 |
| post-cycle / done-gate | 0 |
| `./scripts/peer …` | 32 |
| raw `python3 scripts/` | 0 |

Dispatch/command mix looks healthy in recent log tails.

```bash
./scripts/peer command-dispatch-audit
./scripts/peer pre-dispatch
./scripts/peer post-cycle
```

