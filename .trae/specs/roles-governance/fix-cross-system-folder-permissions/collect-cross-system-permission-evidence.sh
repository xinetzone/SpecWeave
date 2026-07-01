#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SPEC_DIR="$SCRIPT_DIR"
TARGET_DIR="${1:-/media/pc/data/ai/notebook/client/sdk/AI}"
LABEL="${2:-manual}"
EVIDENCE_ROOT="$SPEC_DIR/evidence"
TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
RUN_DIR="$EVIDENCE_ROOT/${TIMESTAMP}-collect-${LABEL}"
LATEST_COLLECT_FILE="$EVIDENCE_ROOT/latest-collect.txt"
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

list_dirs_missing_default_acl() {
  find "$TARGET_DIR" -type d -print0 |
    xargs -0 -I{} sh -c 'getfacl -cp "$1" | grep -q "^default:" || printf "%s\n" "$1"' _ "{}"
}

main() {
  require_cmd find
  require_cmd getfacl
  require_cmd stat
  require_cmd sort
  require_cmd xargs
  ensure_target

  mkdir -p "$RUN_DIR"

  {
    printf 'TARGET_DIR=%s\n' "$TARGET_DIR"
    printf 'LABEL=%s\n' "$LABEL"
    printf 'COLLECTED_AT=%s\n' "$(date '+%F %T %z')"
    printf 'DIR_COUNT=%s\n' "$(find "$TARGET_DIR" -type d | wc -l)"
    printf 'WITHOUT_SETGID=%s\n' "$(find "$TARGET_DIR" -type d ! -perm -2000 | wc -l)"
    printf 'WITH_OTHER_ACCESS=%s\n' "$(find "$TARGET_DIR" -type d -perm /0007 | wc -l)"
    printf 'WITHOUT_DEFAULT_ACL=%s\n' "$(list_dirs_missing_default_acl | wc -l)"
  } >"$RUN_DIR/summary.txt"

  stat -f -c 'fstype=%T fsid=%i target=%n' "$TARGET_DIR" >"$RUN_DIR/fs.txt"
  stat -c 'mode=%A perm=%a owner=%U group=%G path=%n' "$TARGET_DIR" >"$RUN_DIR/root_stat.txt"
  getfacl -cp "$TARGET_DIR" >"$RUN_DIR/root_acl.txt"
  find "$TARGET_DIR" -type d -printf '%m\t%u\t%g\t%p\n' | sort >"$RUN_DIR/dir_modes.tsv"
  find "$TARGET_DIR" -type d -printf '%u:%g\n' | sort | uniq -c | awk '{print $2 "\t" $1}' >"$RUN_DIR/owner_group_histogram.tsv"
  find "$TARGET_DIR" -type d ! -perm -2000 | sort >"$RUN_DIR/dirs_without_setgid.txt"
  find "$TARGET_DIR" -type d -perm /0007 | sort >"$RUN_DIR/dirs_with_other_access.txt"
  list_dirs_missing_default_acl | sort >"$RUN_DIR/dirs_without_default_acl.txt"
  find "$TARGET_DIR" -type d | awk 'NR <= 50 { print }' >"$RUN_DIR/dir_sample.txt"

  append_jsonl_audit \
    "$AUDIT_LOG_FILE" \
    "$(basename "$0")" \
    "$RUN_DIR" \
    "collect_snapshot" \
    "local-admin" \
    "local" \
    "$TARGET_DIR" \
    "collect" \
    "PASS" \
    "" \
    "label=$LABEL dir_count=$(summary_value DIR_COUNT "$RUN_DIR/summary.txt") without_setgid=$(summary_value WITHOUT_SETGID "$RUN_DIR/summary.txt") with_other=$(summary_value WITH_OTHER_ACCESS "$RUN_DIR/summary.txt") without_default_acl=$(summary_value WITHOUT_DEFAULT_ACL "$RUN_DIR/summary.txt")"

  printf '%s\n' "$RUN_DIR" >"$LATEST_COLLECT_FILE"
  echo "[done] 证据已采集: $RUN_DIR"
}

main "$@"
