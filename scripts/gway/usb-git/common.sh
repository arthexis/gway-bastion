#!/usr/bin/env bash
set -euo pipefail

readonly USB_GIT_OWNER_USER="${USB_GIT_OWNER_USER:-arthe}"
readonly USB_GIT_OWNER_HOME="${USB_GIT_OWNER_HOME:-/home/$USB_GIT_OWNER_USER}"
readonly USB_GIT_FIXED_DIR="${USB_GIT_FIXED_DIR:-/mnt/bastion-unlock/bastion}"
readonly USB_GIT_LEGACY_FIXED_DIR="${USB_GIT_LEGACY_FIXED_DIR:-/mnt/bastion-unlock/bastion-ssh}"
readonly USB_GIT_CONFIG_DIR="${USB_GIT_CONFIG_DIR:-$USB_GIT_OWNER_HOME/.config/usb-git}"
readonly USB_GIT_ADMIN_TOKEN_ENC="${USB_GIT_ADMIN_TOKEN_ENC:-$USB_GIT_CONFIG_DIR/admin-token.enc}"
readonly USB_GIT_MAIN_MARKER_ENC="${USB_GIT_MAIN_MARKER_ENC:-$USB_GIT_CONFIG_DIR/main-guard.marker.enc}"
readonly USB_GIT_MAIN_MARKER_TEXT="usb-git-main-guard-v1"
readonly USB_GIT_GIT_CREDENTIALS="${USB_GIT_GIT_CREDENTIALS:-$USB_GIT_OWNER_HOME/.git-credentials}"
readonly USB_GIT_BASTION_CHECK="${USB_GIT_BASTION_CHECK:-/usr/local/libexec/bastion-key-present}"

usb_git_die() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

usb_git_need_cmd() {
    command -v "$1" >/dev/null 2>&1 || usb_git_die "Required command not found: $1"
}

usb_git_find_usb_dir() {
    local base dir user_name

    user_name="${USER:-$(id -un)}"

    if [[ -f "$USB_GIT_FIXED_DIR/unlock.pass" ]]; then
        printf '%s\n' "$USB_GIT_FIXED_DIR"
        return 0
    fi
    if [[ -f "$USB_GIT_LEGACY_FIXED_DIR/unlock.pass" ]]; then
        printf '%s\n' "$USB_GIT_LEGACY_FIXED_DIR"
        return 0
    fi

    for base in "/media/$user_name" "/run/media/$user_name"; do
        [[ -d "$base" ]] || continue

        while IFS= read -r -d '' dir; do
            if [[ -f "$dir/unlock.pass" ]]; then
                printf '%s\n' "$dir"
                return 0
            fi
        done < <(find "$base" -mindepth 2 -maxdepth 2 -type d \( -name bastion -o -name bastion-ssh \) -print0 2>/dev/null)
    done

    return 1
}

usb_git_unlock_file() {
    local usb_dir

    if [[ -x "$USB_GIT_BASTION_CHECK" ]]; then
        "$USB_GIT_BASTION_CHECK" --unlock-file
        return $?
    fi

    usb_dir="$(usb_git_find_usb_dir)" || return 1
    [[ -f "$usb_dir/unlock.pass" ]] || return 1
    printf '%s\n' "$usb_dir/unlock.pass"
}

usb_git_require_bastion() {
    if [[ -x "$USB_GIT_BASTION_CHECK" ]]; then
        "$USB_GIT_BASTION_CHECK" --quiet
        return $?
    fi
    usb_git_marker_ok
}

usb_git_with_temp_file() {
    local tmpfile

    tmpfile="$(mktemp "${TMPDIR:-/tmp}/usb-git.XXXXXX")"
    chmod 600 "$tmpfile"
    printf '%s\n' "$tmpfile"
}

usb_git_decrypt_to_file() {
    local enc_file="$1"
    local out_file="$2"
    local unlock_file

    if [[ ! -f "$enc_file" ]]; then
        usb_git_die "Encrypted file not found: $enc_file"
        return 1
    fi

    if ! unlock_file="$(usb_git_unlock_file)"; then
        usb_git_die "Insert the USB key containing bastion/unlock.pass and retry."
        return 1
    fi

    openssl enc -d -aes-256-cbc -pbkdf2 \
        -in "$enc_file" \
        -out "$out_file" \
        -pass file:"$unlock_file"
}

usb_git_read_secret() {
    local enc_file="$1"
    local tmpfile

    tmpfile="$(usb_git_with_temp_file)"
    if ! usb_git_decrypt_to_file "$enc_file" "$tmpfile"; then
        rm -f "$tmpfile"
        return 1
    fi
    cat "$tmpfile"
    rm -f "$tmpfile"
}

usb_git_marker_ok() {
    local marker

    [[ -f "$USB_GIT_MAIN_MARKER_ENC" ]] || return 1

    if ! marker="$(usb_git_read_secret "$USB_GIT_MAIN_MARKER_ENC" 2>/dev/null)"; then
        return 1
    fi

    [[ "$marker" == "$USB_GIT_MAIN_MARKER_TEXT" ]]
}

usb_git_extract_git_token() {
    local line creds user token

    [[ -f "$USB_GIT_GIT_CREDENTIALS" ]] || return 1
    line="$(grep -E -m1 '^https://[^:[:space:]]+:[^@[:space:]]+@github\.com' "$USB_GIT_GIT_CREDENTIALS" || true)"
    [[ -n "$line" ]] || return 1

    creds="${line#https://}"
    creds="${creds%@github.com}"
    user="${creds%%:*}"
    token="${creds#*:}"

    [[ -n "$user" && -n "$token" ]] || return 1
    printf '%s\n' "$token"
}

usb_git_is_auth_passthrough() {
    local subcommand="${1:-}"

    case "$subcommand" in
        login|logout|refresh|switch|setup-git)
            return 0
            ;;
    esac

    return 1
}
