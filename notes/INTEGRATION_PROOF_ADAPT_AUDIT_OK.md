# Integration proof — adapt audit ok≠usable

_Date: 2026-09-04 05:01_

## Found
`_audit_verify_commands` set `ok=_command_usable` → failing unittest marked PASS.

## Landed
- `ok = proc.returncode == 0`; separate `usable`
- lean verify includes `tests.test_adapt_audit_returncode`
- vault: `~/.config/automation-hub/hub-protect/automation_adapt.py`

## Verify
`python3 -m unittest tests.test_adapt_audit_returncode -q` → OK
