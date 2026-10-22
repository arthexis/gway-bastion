# GWAY Bastion Security

Physical bastion-key verification and SSH/USB helper scripts for GWAY boxes.

This repository packages the guard surface that should remain outside the
Arthexis application repository: verified USB-key presence checks, SSH agent
refresh units, and redacted udev/systemd templates. GitHub rulesets, rather
than this Pi, enforce repository publication policy.

## Contents

- `scripts/gway/bastion-*`: verifier, require wrapper, remote auth, token repo,
  and USB refresh helpers.
- `bin/`: installed command snapshots used on this host.
- `config/systemd/gway/bastion/`: SSH agent and USB refresh units.
- `config/pam.d/`: opt-in SSH PAM integration templates; they are staged but
  never installed or activated by `deploy.sh`.
- `config/udev/rules.d/`: redacted bastion USB refresh rule.
- `docs/`: operations notes and man pages.
- `tests/`: syntax and redaction checks.

The dead-man/recording-retention feature was a candidate for this split, but no
current source or installed unit was present on this host during the split. Keep
that as a later import only if the source is found and can be redacted.

## Validation

```bash
bash -n scripts/gway/bastion-key-present scripts/gway/bastion-require scripts/gway/bastion-usb-refresh bin/gh bin/usb-unlock-on bin/usb-unlock-off
PYTHONPATH=. python3 -m pytest tests
```

Do not commit `unlock.pass`, encrypted or plaintext private keys, GitHub tokens,
USB mount payloads, or machine-specific serial selectors.
