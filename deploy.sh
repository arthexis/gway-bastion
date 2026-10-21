#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v ansible-playbook >/dev/null || { echo "ansible-playbook is required" >&2; exit 1; }
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
sha="$(git rev-parse HEAD)"
[[ "$sha" =~ ^[a-f0-9]{40}$ ]] || { echo "invalid revision" >&2; exit 1; }
# Stage immutable source snapshots only. Never install over active Bastion helpers,
# touch SSH/USB secrets, alter sudoers/udev, or restart services.
root="${BASTION_INSTALL_ROOT:-/opt/gway-bastion}"
case "$root" in
  /*) ;;
  *) echo "BASTION_INSTALL_ROOT must be absolute" >&2; exit 1 ;;
esac
[[ "$root" != "/" && "$root" != "/home" && "$root" != "/etc" && "$root" != "/usr" ]] || { echo "unsafe installation root" >&2; exit 1; }
args=()
if [[ "$root" == "/opt/gway-bastion" ]]; then args+=(--become); fi
ansible-playbook -i localhost, -c local "${args[@]}" ansible/install.yml \
  -e "bastion_install_root=$root" -e "bastion_revision=$sha"
echo "Bastion staged at $root/releases/$sha (NOT activated)"
