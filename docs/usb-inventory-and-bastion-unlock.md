# GWAY Bastion Unlock

GWAY uses host-local bastion helpers during rebuild and operation:

- `usb-unlock-on` mounts the bastion unlock USB read-only at
  `/mnt/bastion-unlock` when a valid bastion marker directory is found.
- `bastion-key-present` verifies the mounted key by decrypting the local
  encrypted SSH key and comparing the derived public key.
- `usb-git` and the guarded `gh` wrapper require the verified key for
  destructive GitHub and protected-branch operations.

USB inventory and claim matching live in `/home/arthe/gway-field-usb`.

## Repository Files

| Source path | Install target |
| --- | --- |
| `bin/usb-unlock-on` | `/usr/local/bin/usb-unlock-on` |
| `bin/usb-unlock-off` | `/usr/local/bin/usb-unlock-off` |
| `bin/usb-ssh` | `/home/arthe/.local/bin/usb-ssh` |
| `scripts/gway/bastion-key-present` | `/usr/local/libexec/bastion-key-present` |
| `scripts/gway/bastion-require` | `/usr/local/libexec/bastion-require` |
| `scripts/gway/bastion-usb-refresh` | `/usr/local/bin/bastion-usb-refresh` |
| `scripts/gway/usb-git/usb-git` | `/home/arthe/.local/bin/usb-git` |
| `lib/usb-git/common.sh` | `/home/arthe/.local/lib/usb-git/common.sh` |
| `lib/usb-git/pre-push-main-guard.sh` | `/home/arthe/.local/lib/usb-git/pre-push-main-guard.sh` |

## Install

From the repository root:

```bash
sudo install -d -m 0755 /usr/local/bin /usr/local/libexec /etc/systemd/system
sudo install -m 0755 bin/usb-unlock-on /usr/local/bin/usb-unlock-on
sudo install -m 0755 bin/usb-unlock-off /usr/local/bin/usb-unlock-off
install -d -m 0755 "$HOME/.local/bin" "$HOME/.local/lib/usb-git"
install -m 0755 bin/usb-ssh "$HOME/.local/bin/usb-ssh"
install -m 0755 bin/usb-git "$HOME/.local/bin/usb-git"
install -m 0755 lib/usb-git/common.sh "$HOME/.local/lib/usb-git/common.sh"
install -m 0755 lib/usb-git/pre-push-main-guard.sh "$HOME/.local/lib/usb-git/pre-push-main-guard.sh"
sudo install -m 0755 scripts/gway/bastion-key-present /usr/local/libexec/bastion-key-present
sudo install -m 0755 scripts/gway/bastion-require /usr/local/libexec/bastion-require
sudo install -m 0755 scripts/gway/bastion-usb-refresh /usr/local/bin/bastion-usb-refresh
sudo systemctl daemon-reload
```

## Validation

Verify the inventory claim in `/home/arthe/gway-field-usb` first when the
bastion helper should use a claimed partition.

Mount and unmount bastion unlock storage:

```bash
sudo usb-unlock-on
findmnt /mnt/bastion-unlock
sudo usb-unlock-off
```

Expected mount behavior:

- `usb-unlock-on` checks claimed `bastion-unlock` partitions first.
- If no claim resolves, it scans unmounted USB partitions.
- It skips mounted partitions and known SD-card burner partitions.
- It mounts the target read-only with `nosuid,nodev,noexec`.
- It accepts either the current `bastion/` marker directory or the legacy
  `bastion-ssh/` marker directory on the USB.
- It exits without changing state when `/run/bastion-ssh/refresh.disabled`
  exists.

## Safety Notes

- Do not publish live bastion mount output when it exposes private labels,
  serials, filesystem UUIDs, or mount paths that identify private devices.
- Do not let `usb-unlock-on` unmount arbitrary mounted USB partitions while SD
  burns, recordings, or file transfers are active.
- Do not copy, print, or commit `unlock.pass`, private keys, encrypted token
  blobs, or GitHub tokens.
