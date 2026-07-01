#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SPEC_DIR="$SCRIPT_DIR"
TARGET_DIR="${1:-/media/pc/data/ai/notebook/client/sdk/AI}"
EVIDENCE_ROOT="$SPEC_DIR/evidence"
TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
RUN_DIR="$EVIDENCE_ROOT/${TIMESTAMP}-verify"
LATEST_VERIFY_FILE="$EVIDENCE_ROOT/latest-verify.txt"
LATEST_APPLY_FILE="$EVIDENCE_ROOT/latest-apply.txt"
AUDIT_LOG_FILE="$EVIDENCE_ROOT/access-audit.jsonl"

# shellcheck source=./audit-log-lib.sh
source "$SCRIPT_DIR/audit-log-lib.sh"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[error] 缺少命令: $cmd" >&2
    exit 1
  fi
}

ensure_target() {
  if [[ ! -d "$TARGET_DIR" ]]; then
    echo "[error] 目标目录不存在: $TARGET_DIR" >&2
    exit 1
  fi
}

count_dirs_missing_default_acl() {
  find "$TARGET_DIR" -type d -print0 |
    xargs -0 -I{} sh -c 'getfacl -cp "$1" | grep -q "^default:" || printf "%s\n" "$1"' _ "{}" |
    wc -l
}

check_owner_group_preserved() {
  local latest_apply_dir
  if [[ ! -f "$LATEST_APPLY_FILE" ]]; then
    echo "SKIP (缺少 apply 快照)"
    return
  fi

  latest_apply_dir=$(<"$LATEST_APPLY_FILE")
  if [[ ! -f "$latest_apply_dir/pre_owner_group_histogram.tsv" ]] || [[ ! -f "$latest_apply_dir/post_owner_group_histogram.tsv" ]]; then
    echo "SKIP (apply 快照不完整)"
    return
  fi

  if diff -u "$latest_apply_dir/pre_owner_group_histogram.tsv" "$latest_apply_dir/post_owner_group_histogram.tsv" >/dev/null; then
    echo "PASS"
  else
    echo "FAIL"
  fi
}

main() {
  require_cmd find
  require_cmd getfacl
  require_cmd stat
  require_cmd grep
  require_cmd xargs
  require_cmd diff
  ensure_target

  mkdir -p "$RUN_DIR"

  local dir_count without_setgid with_other without_default root_perm owner_group_result
  dir_count=$(find "$TARGET_DIR" -type d | wc -l)
  without_setgid=$(find "$TARGET_DIR" -type d ! -perm -2000 | wc -l)
  with_other=$(find "$TARGET_DIR" -type d -perm /0007 | wc -l)
  without_default=$(count_dirs_missing_default_acl)
  root_perm=$(stat -c '%a' "$TARGET_DIR")
  owner_group_result=$(check_owner_group_preserved)

  {
    printf 'TARGET_DIR=%s\n' "$TARGET_DIR"
    printf 'VERIFIED_AT=%s\n' "$(date '+%F %T %z')"
    printf 'DIR_COUNT=%s\n' "$dir_count"
    printf 'WITHOUT_SETGID=%s\n' "$without_setgid"
    printf 'WITH_OTHER_ACCESS=%s\n' "$with_other"
    printf 'WITHOUT_DEFAULT_ACL=%s\n' "$without_default"
    printf 'ROOT_PERM=%s\n' "$root_perm"
    printf 'ROOT_SETGID=%s\n' "$([[ -g "$TARGET_DIR" ]] && echo PASS || echo FAIL)"
    printf 'ROOT_DEFAULT_ACL_USER=%s\n' "$([[ $(getfacl -cp "$TARGET_DIR" | grep -c '^default:user::rwx$') -ge 1 ]] && echo PASS || echo FAIL)"
    printf 'ROOT_DEFAULT_ACL_GROUP=%s\n' "$([[ $(getfacl -cp "$TARGET_DIR" | grep -c '^default:group::rwx$') -ge 1 ]] && echo PASS || echo FAIL)"
    printf 'ROOT_DEFAULT_ACL_OTHER=%s\n' "$([[ $(getfacl -cp "$TARGET_DIR" | grep -c '^default:other::---$') -ge 1 ]] && echo PASS || echo FAIL)"
    printf 'OWNER_GROUP_PRESERVED=%s\n' "$owner_group_result"
    printf 'VERIFY_RESULT=%s\n' "$([[ "$without_setgid" -eq 0 && "$with_other" -eq 0 && "$without_default" -eq 0 ]] && echo PASS || echo FAIL)"
  } | tee "$RUN_DIR/verify_summary.txt"

  stat -c 'mode=%A perm=%a owner=%U group=%G path=%n' "$TARGET_DIR" >"$RUN_DIR/root_stat.txt"
  getfacl -cp "$TARGET_DIR" >"$RUN_DIR/root_acl.txt"
  find "$TARGET_DIR" -type d ! -perm -2000 | sort >"$RUN_DIR/dirs_without_setgid.txt"
  find "$TARGET_DIR" -type d -perm /0007 | sort >"$RUN_DIR/dirs_with_other_access.txt"
  find "$TARGET_DIR" -type d -print0 |
    xargs -0 -I{} sh -c 'getfacl -cp "$1" | grep -q "^default:" || printf "%s\n" "$1"' _ "{}" |
    sort >"$RUN_DIR/dirs_without_default_acl.txt"

  append_jsonl_audit \
    "$AUDIT_LOG_FILE" \
    "$(basename "$0")" \
    "$RUN_DIR" \
    "permission_fix_verified" \
    "local-admin" \
    "local" \
    "$TARGET_DIR" \
    "verify" \
    "$(summary_value VERIFY_RESULT "$RUN_DIR/verify_summary.txt")" \
    "" \
    "dir_count=$(summary_value DIR_COUNT "$RUN_DIR/verify_summary.txt") without_setgid=$(summary_value WITHOUT_SETGID "$RUN_DIR/verify_summary.txt") with_other=$(summary_value WITH_OTHER_ACCESS "$RUN_DIR/verify_summary.txt") without_default_acl=$(summary_value WITHOUT_DEFAULT_ACL "$RUN_DIR/verify_summary.txt") root_perm=$(summary_value ROOT_PERM "$RUN_DIR/verify_summary.txt") owner_group_preserved=$(summary_value OWNER_GROUP_PRESERVED "$RUN_DIR/verify_summary.txt")"

  printf '%s\n' "$RUN_DIR" >"$LATEST_VERIFY_FILE"
  echo "[done] 校验完成: $RUN_DIR"
}

main "$@"
