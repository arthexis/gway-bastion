# GWAY USB Inventory And Bastion Unlock

GWAY uses two host-local USB helpers during rebuild and operation:

- `arthexis-usb-inventory` records local USB block devices and applies local
  claim rules such as `bastion-unlock` and `kindle-postbox`.
- `usb-unlock-on` mounts the bastion unlock USB read-only at
  `/mnt/bastion-unlock` when a valid bastion marker directory is found.

The inventory state is operational state. USB claim files can identify private
hardware. Store public examples in the repository, but keep filled claim files
local or bastion-held.

## Repository Files

| Source path | Install target |
| --- | --- |
| `scripts/gway/arthexis_usb_inventory.py` | `/usr/local/bin/arthexis-usb-inventory` |
| `scripts/gway/usb-unlock-on` | `/usr/local/bin/usb-unlock-on` |
| `scripts/gway/usb-unlock-off` | `/usr/local/bin/usb-unlock-off` |
| `config/templates/arthexis-usb-claims.json.template` | `/etc/arthexis-usb/claims.json` after local edit |
| `config/systemd/gway/usb-inventory/arthexis-usb-inventory.service` | `/etc/systemd/system/arthexis-usb-inventory.service` |
| `config/systemd/gway/usb-inventory/arthexis-usb-inventory.timer` | `/etc/systemd/system/arthexis-usb-inventory.timer` |
| `config/systemd/gway/usb-inventory/arthexis-usb-inventory.service.d/10-runtime-directory.conf` | `/etc/systemd/system/arthexis-usb-inventory.service.d/10-runtime-directory.conf` |

## Drift Resolution

The 2026-07-28 rebuild inventory found that the staged USB folder was not fully
authoritative:

- `/usr/local/bin/arthexis-usb-inventory` matched
  `/home/arthe/usb-hub/bin/arthexis-usb-inventory`.
- `/usr/local/bin/usb-unlock-on` differed from
  `/home/arthe/usb-hub/bin/usb-unlock-on`.
- `/etc/systemd/system/arthexis-usb-inventory.service` differed from the staged
  service because the installed service runs as the `arthe` user.
- `/etc/systemd/system/arthexis-usb-inventory.timer` differed from the staged
  timer because the installed timer uses the slower Control-node cadence.

For rebuild purposes, the repository now follows the installed behavior for the
drifted files.

## Claims Template

Install the template, then replace example match selectors with values for the
local devices:

```bash
sudo install -d -m 0755 /etc/arthexis-usb
sudo install -m 0644 config/templates/arthexis-usb-claims.json.template \
  /etc/arthexis-usb/claims.json
sudo editor /etc/arthexis-usb/claims.json
```

Claim match keys are compared against inventory fields such as:

- `path_type`
- `fstype`
- `label`
- `fs_uuid`
- `vendor`
- `model`
- `serial`
- `kindle_shape`

Prefer non-secret selectors such as filesystem label and `kindle_shape` when
they are stable enough. Use serial or filesystem UUID selectors only when the
claim must bind to one physical device, and do not commit filled values.

## Install

From the repository root:

```bash
sudo install -d -m 0755 /usr/local/bin /etc/systemd/system \
  /etc/systemd/system/arthexis-usb-inventory.service.d
sudo install -m 0755 scripts/gway/arthexis_usb_inventory.py \
  /usr/local/bin/arthexis-usb-inventory
sudo install -m 0755 scripts/gway/usb-unlock-on /usr/local/bin/usb-unlock-on
sudo install -m 0755 scripts/gway/usb-unlock-off /usr/local/bin/usb-unlock-off
sudo install -m 0644 config/systemd/gway/usb-inventory/arthexis-usb-inventory.service \
  /etc/systemd/system/arthexis-usb-inventory.service
sudo install -m 0644 config/systemd/gway/usb-inventory/arthexis-usb-inventory.timer \
  /etc/systemd/system/arthexis-usb-inventory.timer
sudo install -m 0644 \
  config/systemd/gway/usb-inventory/arthexis-usb-inventory.service.d/10-runtime-directory.conf \
  /etc/systemd/system/arthexis-usb-inventory.service.d/10-runtime-directory.conf
sudo systemctl daemon-reload
sudo systemctl enable --now arthexis-usb-inventory.timer
```

## Validation

Refresh inventory and list state:

```bash
sudo systemctl start arthexis-usb-inventory.service
arthexis-usb-inventory list
```

Resolve the bastion claim:

```bash
arthexis-usb-inventory claimed-path --role bastion-unlock --refresh
```

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

Check timer cadence:

```bash
systemctl status arthexis-usb-inventory.timer --no-pager
systemctl list-timers arthexis-usb-inventory.timer --no-pager
journalctl -u arthexis-usb-inventory.service -n 50 --no-pager
```

## Safety Notes

- Do not publish live inventory output when it contains private labels, serials,
  filesystem UUIDs, or mount paths that identify private devices.
- Do not commit a filled `/etc/arthexis-usb/claims.json`.
- Do not let `usb-unlock-on` unmount arbitrary mounted USB partitions while SD
  burns, recordings, or file transfers are active.
- Before removing a USB Wi-Fi dongle, validate the current AP/uplink roles with
  `iw dev` and `nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status`.
