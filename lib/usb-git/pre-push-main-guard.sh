#!/usr/bin/env bash
set -euo pipefail

source /home/arthe/.local/lib/usb-git/common.sh
source /home/arthe/.local/lib/operator-log.sh

hook_detail="no-refs"
hook_status=0
readonly ZERO_SHA="0000000000000000000000000000000000000000"

operator_log_event "usb-git-hook" "start" "pre-push" "$hook_detail"

while read -r _local_ref _local_sha remote_ref _remote_sha; do
    hook_detail="${remote_ref:-no-refs}"
    require_bastion=0
    reason=""

    if [[ "$remote_ref" == "refs/heads/main" ]]; then
        require_bastion=1
        reason="direct push to main"
    elif [[ "$remote_ref" == refs/tags/* ]]; then
        require_bastion=1
        reason="tag publication or mutation"
    elif [[ "${_local_sha:-}" == "$ZERO_SHA" ]]; then
        require_bastion=1
        reason="remote ref deletion"
    elif [[ "${_remote_sha:-}" != "$ZERO_SHA" && "${_local_sha:-}" != "$ZERO_SHA" ]]; then
        if ! git merge-base --is-ancestor "$_remote_sha" "$_local_sha" 2>/dev/null; then
            require_bastion=1
            reason="non-fast-forward push"
        fi
    fi

    if [[ "$require_bastion" -eq 1 ]]; then
        if ! usb_git_require_bastion; then
            hook_status=1
            operator_log_event "usb-git-hook" "finish" "pre-push" "$hook_detail" "$hook_status"
            printf 'Blocked action: %s requires the verified bastion USB key.\n' "$reason" >&2
            printf '%s\n' "Insert the key containing bastion/unlock.pass and retry the push." >&2
            exit 1
        fi
    fi
done

operator_log_event "usb-git-hook" "finish" "pre-push" "$hook_detail" "$hook_status"
exit 0
