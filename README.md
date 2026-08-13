# GWAY Bastion Security

Physical bastion-key verification and guarded GitHub/repo helper scripts for
GWAY boxes.

This repository packages the guard surface that should remain outside the
Arthexis application repository: verified USB-key presence checks, guarded `gh`
and `usb-git` flows, token bootstrap helpers, SSH agent refresh units, and
redacted udev/systemd templates.

## Contents

- `scripts/gway/bastion-*`: verifier, require wrapper, remote auth, token repo,
  and USB refresh helpers.
- `scripts/gway/usb-git/`: source copy of the guarded GitHub helper.
- `bin/`: installed command snapshots used on this host.
- `lib/usb-git/`: installed library snapshots used by `bin/usb-git`.
- `config/systemd/gway/bastion/`: SSH agent and USB refresh units.
- `config/udev/rules.d/`: redacted bastion USB refresh rule.
- `config/templates/`: non-secret `usb-git` environment template.
- `docs/`: operations notes and man pages.
- `tests/`: syntax and redaction checks.

The dead-man/recording-retention feature was a candidate for this split, but no
current source or installed unit was present on this host during the split. Keep
that as a later import only if the source is found and can be redacted.

## Validation

```bash
bash -n scripts/gway/bastion-key-present scripts/gway/bastion-require scripts/gway/bastion-usb-refresh scripts/gway/usb-git/usb-git scripts/gway/usb-git/common.sh scripts/gway/usb-git/pre-push-main-guard.sh bin/gh bin/usb-git bin/usb-unlock-on bin/usb-unlock-off lib/usb-git/common.sh lib/usb-git/pre-push-main-guard.sh
PYTHONPATH=. python3 -m pytest tests
```

Do not commit `unlock.pass`, encrypted or plaintext private keys, GitHub tokens,
USB mount payloads, or machine-specific serial selectors.
