# Integration proof — SaaS Health Dashboard (OSS registry target)

- **When:** 2026-09-04T21:27Z
- **Role:** integration_architect (peer-5)
- **Registry SoT (this worktree):** `repos/registry.json` SaaS Health Dashboard `status=offline-mac` (write + JSON readback)
- **Target path (Mac):** `/Users/togi/SaaS Health Dashboard`
- **Prior lie:** peer-5 worktree still `unaudited` / hub Terminal notes called remaining Mac offline “stale” — path is ON_DISK but **not** git-backed
- **Live probes this cycle:**
  - `test ! -d …/.git` — CONFIRMED_NO_GIT
  - `test ! -f …/automation.config.json` — CONFIRMED_NO_KIT
  - `npm run typecheck` (`tsc --noEmit`) — EXIT 0
  - `package.json` scripts include `typecheck`; `lint`=`next lint` (interactive ESLint — **not** a verify gate)
- **Sibling leftovers (same probes):**
  - F.I.R.E. Project / Marketplace — empty-git husks (`children=1` `.git` only; `rev-list --count HEAD` fatal no commits) → stay `offline-mac`
  - deepseek-cursor-proxy — HAS_GIT + NO_KIT → stay `adapted` (proof `notes/INTEGRATION_PROOF_DEEPSEEK_MAC.md`)
- **Adapt / worktree:** **BLOCK** — no `.git` → `peer_worktree` / `automation_adapt --install` not applicable until git import
- **factory_meter_mode:** `self_sufficient` — do **not** claim `adapt-verified-mac` or `external-proof-adapted`; defer to `notes/CREATIVE_BACKLOG.md` `[output-research] Mac native verify: SaaS Health Dashboard`; **do not** Active-enqueue
- **Next irreversible (when meter=`external_proof`):** git import → kit install → `verify_commands=["npm run typecheck"]` in target tree → `adapt-verified-mac` + this proof upgraded
- **Falsifier passed:** registry readback `status == offline-mac`; typecheck EXIT 0; no Active queue line added; hub leftover git/unaudited/needs-kit-install=NONE
