# Agent preferences

**SEQUENCING LOCK (non-negotiable):** Never jump to the next ladder rung (distribution, Newdrop polish, Automations migration, “ship product”) until the **current** factory capability can run **A→Z without human oversight** — adapt → native verify → worktree/PR → irreversible artifact, with commands/niches as co-pilot only. Incomplete “full automation kit in factory” = stay on that loop; do not skip ahead because niches/commands look shiny. Needle: `OVERSEER_NO_JUMP_UNTIL_A_TO_Z_2026_09_07`.

**Green lock (2026-09-08):** stamped — CLEAN CPT A→E + [PR #2](https://github.com/heyitsmeyourbudlol-lgtm/CPT/pull/2) · origin `peer/kit-a-to-z-20260908T023609` @ `e60fddd` · `green_lock_eligible=pr`; SoT `notes/FACTORY_A_TO_Z_PROOF.md` Status=**green**. Ladder may advance; still prefer kit-run for new registry targets.

**TIME BOMB (early–mid 2027):** Custom orchestration crown expires when Cursor-native loops become top 5–15% norm. Prefer **shipping products + distribution** over kit polish — **only after** the sequencing lock clears. Read `notes/LOOP_STRATEGY.md`.

**Investment thesis:** this kit is **capex** for an OSS-monster factory — adapt → native verify → worktree/PR → irreversible artifact on top-tier open source. `automation_improve` must enqueue executable factory work only (not ASI/strategy theater).

**Full strategy (stress all of it — not just the deadline):**
- Ladder: intelligence → speed → distribution → ecosystem (hub with gravity; 10 apps ≠ ecosystem)
- Keep after commoditization: queue semantics, verify gates, product constraints — not the daemon
- Meta-skill: **exit each loop** when it becomes table stakes; migrate the brain, murder the boilerplate
- Moat: users + shared primitives + habits + willingness to kill the kit

**Peer orchestration:** Read `notes/AUTOMATION.md` and `notes/PEER_ORCHESTRATION.md` before multi-file changes.
**On-demand niche:** If work reveals a repeated closed-world job a tiny local model could speed up: `./scripts/peer niche-mint --propose` then `--start` (dedupe first; not mass bank expansion).
**Commands:** Prefer `./scripts/peer <id>` for repetitive work — read `notes/AGENT_COMMANDS.md` + `notes/HUB_PEER_VERBS.md`. Missing recipe → wake **Command Builder** (`./scripts/peer commands-cycle`). Ecosystem: `notes/COMMAND_ECOSYSTEM_PLAN.md`. Do not retype `python3 scripts/…` chains.
**GitHub / IDE DX (hub):** `./scripts/peer github-feedback-fetch|list|render` (sanitized Issues inbox) · `./scripts/peer production-power` (or `scoreboard-write`) for `notes/PRODUCTION_POWER_SCOREBOARD.md`. Newdrop GitHub/IDE track (no UI): `notes/GITHUB_IDE_SUPPORT.md`.
**Dual path:** Local forever loop default; Cursor Automations optional — verb map in `notes/CURSOR_AUTOMATIONS_MIGRATION.md`.
**Survival:** Read `notes/AGENT_SURVIVAL.md` — hazard map for stalls, chicken-eggs, false labels (plan-gate, adapt_stale, queue junk, namespace flip). Playbook: `notes/AGENT_ERROR_PLAYBOOK.md`.
**Never solo:** maximize parallel Task peers when scopes allow — prefer launching the full implementation peer set in ONE message; never collapse independent scopes into one hero agent.
**No monetary payment:** free Cursor desktop / local / CLEAN only — never paid API spend, Stripe/billing enablement, or purchasing credits (`force_free_desktop_auth`).
**Do not rely on chat memory:** open `notes/AGENT_WORKING_MEMORY.md` every turn. Domain SMEs + Fact Librarian: `./scripts/peer fact-query [--domain ID] "…"` (`notes/SOP_AGENT_REMEMBRANCE.md`, `notes/REPO_DOMAIN_SMES.md`). Lossless pack is additive — `./scripts/peer memory-compress`.

```bash
./scripts/peer bootstrap                    # cold start: daemons + heal + verify + digest
./scripts/peer heal-all                     # mechanical heal + compact + verify gate
./scripts/peer pre-dispatch                 # before cursor-agent (compact + check + pool)
./scripts/peer commands-list --pivotal      # all pivotal agent commands → notes/AGENT_COMMANDS.md
python3 scripts/peer_orchestrate.py --self-check
python3 scripts/automation_adapt.py --heal --write   # adapt kit to this repo
python3 scripts/automation_adapt.py --audit          # self-audit script + outputs
python3 scripts/automation_improve.py --write --research  # plan + industry trends
python3 scripts/automation_research.py --refresh --write # update notes/AUTOMATION_TRENDS.md
python3 scripts/peer_orchestrate.py --dry-run
python3 scripts/cursor_self_improve.py --peer
python3 scripts/peer_loop.py --forever --background
./scripts/peer-loop-run
```

**Working memory:** `notes/README.md` · queue: `notes/WORK_QUEUE.md` (sync with `scripts/self_improve_context.md`) · errors: `notes/AGENT_ERROR_PLAYBOOK.md` (`./scripts/peer playbook-lookup "<error>"`)

**Config:** Edit `automation.config.json` for project name, test command, optional RSS budget, post-cycle hook.
