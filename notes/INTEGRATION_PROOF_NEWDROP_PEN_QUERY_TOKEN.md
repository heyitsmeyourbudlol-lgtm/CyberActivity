# Integration proof — Newdrop pen-test query-token

- **When:** 2026-09-07T12:45Z (Mac hub agent)
- **Repo:** Newdrop (CaaS) @ `/Users/togi/CaaS` (registry DGX path `/home/arnavrastogi/CaaS`; Mac mirror preferred this cycle)
- **Irreversible artifact:** merged PR https://github.com/heyitsmeyourbudlol-lgtm/caas-changelog/pull/16
  - branch `peer/pen-team-invite-qs`
  - product commit `a1f6be4`
  - merge commit `06a543bae23a335c3e9baaec6ea8bac3ff3acd14` on `main` @ 2026-09-07T12:45:16Z
- **Change:** team invite accept URL uses path segment `/dashboard/team/accept/[token]` (not `?token=` query); legacy query redirects into path form
- **Adapt:** `python3 scripts/automation_adapt.py --heal --write` in `/Users/togi/CaaS` — kit present; audit `ok=False` only because verify entry `NODE_OPTIONS=--max-old-space-size=8192 npm run build` is mis-parsed as argv0 (`Errno 2`); other verify cmds OK in adapt audit (`npm test`, `check:controls`, lint, `npm ci`, audit)
- **Native verify (Mac, product cwd):**
  - `npm test` — 53 files / **303 passed** EXIT 0
  - `npm run check:controls` — **13 ok · 0 fail** EXIT 0
  - registry `bash scripts/with-node.sh npm test` — **MISSING** `scripts/with-node.sh` on this Mac checkout (ran `npm test` directly)
- **Push:** HTTPS via `gh` OK (not SSH BLOCK this cycle)
- **Registry status:** remains `adapt-verified-dgx` — do **not** claim `external-proof-adapted` (Rekor/pin rules in `notes/EXTERNAL_PROOF.md` unmet)
- **Prior (2026-09-04 DGX):** worktree commit `7658dfd7` push BLOCK (ssh); this cycle lands the same harden on public `main`
