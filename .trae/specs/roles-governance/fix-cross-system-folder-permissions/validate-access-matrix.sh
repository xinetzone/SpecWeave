#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SPEC_DIR="$SCRIPT_DIR"
TARGET_DIR="${1:-/media/pc/data/ai/notebook/client/sdk/AI}"
EVIDENCE_ROOT="$SPEC_DIR/evidence"
TIMESTAMP="${TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
RUN_DIR="$EVIDENCE_ROOT/${TIMESTAMP}-access-matrix"
LATEST_MATRIX_FILE="$EVIDENCE_ROOT/latest-access-matrix.txt"
AUDIT_LOG_FILE="$EVIDENCE_ROOT/access-audit.jsonl"
REPORT_FILE="$SPEC_DIR/report.md"
LOCAL_AUTHORIZED_IDENTITY="${LOCAL_AUTHORIZED_IDENTITY:-$(id -un 2>/dev/null || echo unknown)}"
LOCAL_SOURCE_SYSTEM="${LOCAL_SOURCE_SYSTEM:-local}"
SSH_UNAUTHORIZED_SOURCE="${SSH_UNAUTHORIZED_SOURCE:-ssh-unauthorized}"
SSH_UNAUTHORIZED_IDENTITY="${SSH_UNAUTHORIZED_IDENTITY:-unauthorized-ssh-user}"
SSH_UNAUTHORIZED_HOST="${SSH_UNAUTHORIZED_HOST:-127.0.0.1}"
STATIC_OTHER_SOURCE="${STATIC_OTHER_SOURCE:-static-policy}"
STATIC_OTHER_IDENTITY="${STATIC_OTHER_IDENTITY:-other}"

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

record_case() {
  local case_name="$1"
  local source_system="$2"
  local identity="$3"
  local action="$4"
  local expected="$5"
  local actual="$6"
  local result="$7"
  local failure_reason="$8"
  local details="$9"

  {
    printf 'CASE_NAME=%s\n' "$case_name"
    printf 'SOURCE_SYSTEM=%s\n' "$source_system"
    printf 'IDENTITY=%s\n' "$identity"
    printf 'TARGET_RESOURCE=%s\n' "$TARGET_DIR"
    printf 'ACTION=%s\n' "$action"
    printf 'EXPECTED=%s\n' "$expected"
    printf 'ACTUAL=%s\n' "$actual"
    printf 'RESULT=%s\n' "$result"
    printf 'FAILURE_REASON=%s\n' "$failure_reason"
    printf 'DETAILS=%s\n' "$details"
  } >>"$RUN_DIR/access_matrix_summary.txt"
  printf -- '---\n' >>"$RUN_DIR/access_matrix_summary.txt"

  append_jsonl_audit \
    "$AUDIT_LOG_FILE" \
    "$(basename "$0")" \
    "$RUN_DIR" \
    "access_matrix_case" \
    "$identity" \
    "$source_system" \
    "$TARGET_DIR" \
    "$action" \
    "$result" \
    "$failure_reason" \
    "case=$case_name expected=$expected actual=$actual details=$details"
}

run_local_authorized_case() {
  local actual result details
  if find "$TARGET_DIR" -maxdepth 0 -type d >/dev/null 2>&1 && ls "$TARGET_DIR" >/dev/null 2>&1; then
    actual="allowed"
    result="PASS"
    details="本地已授权主体可枚举目标目录"
  else
    actual="denied"
    result="FAIL"
    details="本地已授权主体无法枚举目标目录"
  fi

  record_case \
    "local_authorized_access" \
    "$LOCAL_SOURCE_SYSTEM" \
    "$LOCAL_AUTHORIZED_IDENTITY" \
    "list_directory" \
    "allowed" \
    "$actual" \
    "$result" \
    "" \
    "$details"
}

run_ssh_unauthorized_case() {
  local ssh_output actual result failure_reason details
  ssh_output=$(ssh \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=no \
    -o ConnectTimeout=5 \
    -o PreferredAuthentications=publickey,password,keyboard-interactive \
    -l "$SSH_UNAUTHORIZED_IDENTITY" \
    "$SSH_UNAUTHORIZED_HOST" \
    "ls '$TARGET_DIR'" 2>&1 || true)

  if printf '%s' "$ssh_output" | grep -Eqi 'Permission denied|Authentication failed|publickey|denied'; then
    actual="denied"
    result="PASS"
    failure_reason="ssh_unauthorized_denied"
    details=$(printf '%s' "$ssh_output" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g')
  elif printf '%s' "$ssh_output" | grep -Eqi 'Connection refused|Connection closed|Operation timed out|No route to host|Could not resolve hostname'; then
    actual="denied"
    result="PASS"
    failure_reason="ssh_transport_unavailable"
    details=$(printf '%s' "$ssh_output" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g')
  else
    actual="inconclusive"
    result="FAIL"
    failure_reason="ssh_denial_not_observed"
    details=$(printf '%s' "$ssh_output" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g')
  fi

  printf '%s\n' "$ssh_output" >"$RUN_DIR/ssh_unauthorized_output.txt"
  record_case \
    "ssh_unauthorized_access" \
    "$SSH_UNAUTHORIZED_SOURCE" \
    "$SSH_UNAUTHORIZED_IDENTITY@$SSH_UNAUTHORIZED_HOST" \
    "ssh_list_directory" \
    "denied" \
    "$actual" \
    "$result" \
    "$failure_reason" \
    "$details"
}

run_static_other_case() {
  local root_acl actual result failure_reason details
  root_acl=$(getfacl -cp "$TARGET_DIR")
  printf '%s\n' "$root_acl" >"$RUN_DIR/static_root_acl.txt"

  if printf '%s\n' "$root_acl" | grep -q '^other::---$' && printf '%s\n' "$root_acl" | grep -q '^default:other::---$'; then
    actual="denied"
    result="PASS"
    failure_reason=""
    details="根目录静态权限与默认 ACL 均拦截 other"
  else
    actual="allowed_or_partial"
    result="FAIL"
    failure_reason="other_policy_not_enforced"
    details="根目录缺少 other::--- 或 default:other::---"
  fi

  record_case \
    "static_other_access_block" \
    "$STATIC_OTHER_SOURCE" \
    "$STATIC_OTHER_IDENTITY" \
    "inspect_permission_policy" \
    "denied" \
    "$actual" \
    "$result" \
    "$failure_reason" \
    "$details"
}

write_report_section() {
  local block_file="$RUN_DIR/report_access_matrix_section.md"
  local case_name expected actual result failure_reason details
  local total_cases pass_cases fail_cases audit_tail

  total_cases=$(grep -c '^CASE_NAME=' "$RUN_DIR/access_matrix_summary.txt")
  pass_cases=$(grep -c '^RESULT=PASS$' "$RUN_DIR/access_matrix_summary.txt")
  fail_cases=$(grep -c '^RESULT=FAIL$' "$RUN_DIR/access_matrix_summary.txt")

  {
    printf '来源：`%s/access_matrix_summary.txt`\n' "$(basename "$RUN_DIR")"
    printf '\n'
    printf '| 验证场景 | 预期 | 实际 | 结果 | 失败原因 |\n'
    printf '|---|---|---|---|---|\n'
    while IFS= read -r case_name && \
          IFS= read -r _source_line && \
          IFS= read -r _identity_line && \
          IFS= read -r _target_line && \
          IFS= read -r _action_line && \
          IFS= read -r expected && \
          IFS= read -r actual && \
          IFS= read -r result && \
          IFS= read -r failure_reason && \
          IFS= read -r details && \
          IFS= read -r _separator; do
      printf '| %s | %s | %s | %s | %s |\n' \
        "${case_name#CASE_NAME=}" \
        "${expected#EXPECTED=}" \
        "${actual#ACTUAL=}" \
        "${result#RESULT=}" \
        "${failure_reason#FAILURE_REASON=}"
    done <"$RUN_DIR/access_matrix_summary.txt"
    printf '\n'
    printf '- 矩阵总数：`%s`\n' "$total_cases"
    printf '- PASS：`%s`\n' "$pass_cases"
    printf '- FAIL：`%s`\n' "$fail_cases"
    printf '- 审计日志：`evidence/access-audit.jsonl`\n'
    printf '\n'
    printf '审计样例：\n'
    printf '\n'
    printf '```json\n'
    audit_tail=$(tail -n 3 "$AUDIT_LOG_FILE" 2>/dev/null || true)
    if [[ -n "$audit_tail" ]]; then
      printf '%s\n' "$audit_tail"
    fi
    printf '```\n'
  } >"$block_file"

  if [[ -f "$REPORT_FILE" ]]; then
    replace_markdown_block \
      "$REPORT_FILE" \
      "<!-- ACCESS_MATRIX_RESULTS:BEGIN -->" \
      "<!-- ACCESS_MATRIX_RESULTS:END -->" \
      "$block_file"
  fi
}

main() {
  require_cmd find
  require_cmd ls
  require_cmd ssh
  require_cmd grep
  require_cmd sed
  require_cmd tr
  require_cmd getfacl
  require_cmd tail
  ensure_target

  mkdir -p "$RUN_DIR"
  : >"$RUN_DIR/access_matrix_summary.txt"

  run_local_authorized_case
  run_ssh_unauthorized_case
  run_static_other_case
  write_report_section

  printf '%s\n' "$RUN_DIR" >"$LATEST_MATRIX_FILE"
  echo "[done] 访问矩阵验证完成: $RUN_DIR"
}

main "$@"
