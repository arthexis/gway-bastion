# Bastion deployment: stage-only contract

`bash deploy.sh` uses Ansible to stage a versioned, immutable-by-convention
snapshot at `/opt/gway-bastion/releases/<commit SHA>`. This increment **does not
activate** Bastion: it does not replace /usr/local commands, edit systemd or
udev rules, touch USB media, keys, tokens or SSH agents, or restart anything.

Set `BASTION_INSTALL_ROOT` to an isolated absolute path for CI/tests. The default
production location requires noninteractive privilege escalation through Ansible.
A repeat invocation stages the same source bytes idempotently. The `REVISION`
file identifies the staged revision; it **does not prove** that active security
services run that revision.

Before an activation increment, gather redacted GWAY-001 inventory, define
managed file ownership and runtime health checks, verify compatibility with
existing services, and require explicit operator approval. Never infer successful
Bastion deployment from stage-only completion. The Remote deploy adapter must
not claim an installed/healthy release until activation is implemented and
validated. No post-merge CI or automatic deployments are configured here.
