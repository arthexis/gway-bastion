# GWAY Bastion Unlock

GWAY uses host-local bastion helpers during rebuild and operation:

- `usb-unlock-on` mounts the bastion unlock USB read-only at
  `/mnt/bastion-unlock` when a valid bastion marker directory is found.
- `bastion-key-present` verifies the mounted key by decrypting the local
  encrypted SSH key and comparing the derived public key.
- `bastion-usb-refresh` normally treats an already-mounted key as read-only
  verification input. It only rewrites the USB README/payload layout when
  `BASTION_USB_REFRESH_CLEANUP_LAYOUT=1` is set for an explicit cleanup run.
- Routine admin-email refresh uses `gway-admin-email-sync --service-prestart`,
  which avoids remounting the USB read-write. Use the admin email helper's
  `--apply` mode only when intentionally updating encrypted USB/local copies.
- GitHub publication and branch policy are enforced by GitHub rulesets. The Pi
  does not gate GitHub CLI calls or install local Git push guards.

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

## Install

From the repository root:

```bash
sudo install -d -m 0755 /usr/local/bin /usr/local/libexec /etc/systemd/system
sudo install -m 0755 bin/usb-unlock-on /usr/local/bin/usb-unlock-on
sudo install -m 0755 bin/usb-unlock-off /usr/local/bin/usb-unlock-off
install -m 0755 bin/usb-ssh "$HOME/.local/bin/usb-ssh"
sudo install -m 0755 scripts/gway/bastion-key-present /usr/local/libexec/bastion-key-present
sudo install -m 0755 scripts/gway/bastion-require /usr/local/libexec/bastion-require
sudo install -m 0755 scripts/gway/bastion-usb-refresh /usr/local/bin/bastion-usb-refresh
sudo systemctl daemon-reload
```

## Upgrade Cleanup

The retired GitHub gate is not used by this release. On an existing host,
remove only these exact legacy artifacts after installing the direct `gh`
wrapper:

```bash
rm -f "$HOME/.local/bin/usb-git"
rm -f "$HOME/.local/lib/usb-git/common.sh" "$HOME/.local/lib/usb-git/pre-push-main-guard.sh"
rmdir "$HOME/.local/lib/usb-git" 2>/dev/null || true
```

Do not remove `usb-ssh`, `bastion-key-present`, or the Bastion SSH-agent
services: they remain the supported access-control surface for Bastion SSH.

USB removal does not run a Bastion refresh action or alter RFID work. The
periodic refresh timer only maintains the optional Bastion agent cache.

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
- Routine refresh should not remount the key read-write. Use
  `BASTION_USB_REFRESH_CLEANUP_LAYOUT=1 sudo bastion-usb-refresh` only when the
  USB layout itself needs repair.

## Safety Notes

- Do not publish live bastion mount output when it exposes private labels,
  serials, filesystem UUIDs, or mount paths that identify private devices.
- Do not let `usb-unlock-on` unmount arbitrary mounted USB partitions while SD
  burns, recordings, or file transfers are active.
- Do not copy, print, or commit `unlock.pass`, private keys, encrypted token
  blobs, or GitHub tokens.
