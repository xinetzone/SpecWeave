#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SPEC_DIR="$SCRIPT_DIR"
TARGET_DIR="${1:-/media/pc/data/ai/notebook/client/sdk/AI}"
EVIDENCE_ROOT="$SPEC_DIR/evidence"
TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
RUN_DIR="$EVIDENCE_ROOT/${TIMESTAMP}-apply"
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

write_counts() {
  {
    printf 'TARGET_DIR=%s\n' "$TARGET_DIR"
    printf 'DIR_COUNT=%s\n' "$(find "$TARGET_DIR" -type d | wc -l)"
    printf 'WITHOUT_SETGID=%s\n' "$(find "$TARGET_DIR" -type d ! -perm -2000 | wc -l)"
    printf 'WITH_OTHER_ACCESS=%s\n' "$(find "$TARGET_DIR" -type d -perm /0007 | wc -l)"
    printf 'WITHOUT_DEFAULT_ACL=%s\n' "$(count_dirs_missing_default_acl)"
  } | tee "$1"
}

write_owner_group_histogram() {
  find "$TARGET_DIR" -type d -printf '%u:%g\n' |
    sort |
    uniq -c |
    awk '{print $2 "\t" $1}'
}

capture_snapshot() {
  local stage="$1"

  write_counts "$RUN_DIR/${stage}_counts.txt"
  stat -f -c 'fstype=%T fsid=%i target=%n' "$TARGET_DIR" >"$RUN_DIR/${stage}_fs.txt"
  stat -c 'mode=%A perm=%a owner=%U group=%G path=%n' "$TARGET_DIR" >"$RUN_DIR/${stage}_root_stat.txt"
  getfacl -cp "$TARGET_DIR" >"$RUN_DIR/${stage}_root_acl.txt"
  find "$TARGET_DIR" -type d -printf '%m\t%u\t%g\t%p\n' | sort >"$RUN_DIR/${stage}_dir_modes.tsv"
  find "$TARGET_DIR" -type d ! -perm -2000 | sort >"$RUN_DIR/${stage}_dirs_without_setgid.txt"
  find "$TARGET_DIR" -type d -perm /0007 | sort >"$RUN_DIR/${stage}_dirs_with_other_access.txt"
  find "$TARGET_DIR" -type d -print0 |
    xargs -0 -I{} sh -c 'getfacl -cp "$1" | grep -q "^default:" || printf "%s\n" "$1"' _ "{}" |
    sort >"$RUN_DIR/${stage}_dirs_without_default_acl.txt"
  write_owner_group_histogram >"$RUN_DIR/${stage}_owner_group_histogram.tsv"
}

main() {
  require_cmd find
  require_cmd chmod
  require_cmd setfacl
  require_cmd getfacl
  require_cmd stat
  require_cmd sort
  require_cmd uniq
  require_cmd awk
  require_cmd xargs
  ensure_target

  mkdir -p "$RUN_DIR"

  echo "[info] 目标目录: $TARGET_DIR"
  echo "[info] 证据目录: $RUN_DIR"
  echo "[step] 采集修复前快照"
  capture_snapshot pre

  echo "[step] 递归补目录 setgid 并移除 other 访问"
  find "$TARGET_DIR" -type d -exec chmod g+s,o-rwx {} +

  echo "[step] 递归补目录默认 ACL，保持后续新建内容继承 owner/group 协作权限"
  find "$TARGET_DIR" -type d -exec setfacl -m d:u::rwx,d:g::rwx,d:o::---,d:m::rwx {} +

  echo "[step] 采集修复后快照"
  capture_snapshot post

  append_jsonl_audit \
    "$AUDIT_LOG_FILE" \
    "$(basename "$0")" \
    "$RUN_DIR" \
    "permission_fix_applied" \
    "local-admin" \
    "local" \
    "$TARGET_DIR" \
    "chmod+setfacl" \
    "PASS" \
    "" \
    "pre_without_setgid=$(summary_value WITHOUT_SETGID "$RUN_DIR/pre_counts.txt") pre_with_other=$(summary_value WITH_OTHER_ACCESS "$RUN_DIR/pre_counts.txt") pre_without_default_acl=$(summary_value WITHOUT_DEFAULT_ACL "$RUN_DIR/pre_counts.txt") post_without_setgid=$(summary_value WITHOUT_SETGID "$RUN_DIR/post_counts.txt") post_with_other=$(summary_value WITH_OTHER_ACCESS "$RUN_DIR/post_counts.txt") post_without_default_acl=$(summary_value WITHOUT_DEFAULT_ACL "$RUN_DIR/post_counts.txt")"

  printf '%s\n' "$RUN_DIR" >"$LATEST_APPLY_FILE"
  echo "[done] 修复完成，最近一次 apply 快照: $RUN_DIR"
}

main "$@"
