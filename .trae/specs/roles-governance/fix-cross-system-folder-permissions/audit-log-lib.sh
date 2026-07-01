#!/usr/bin/env bash

json_escape() {
  local value="${1-}"
  value=${value//\\/\\\\}
  value=${value//\"/\\\"}
  value=${value//$'\n'/\\n}
  value=${value//$'\r'/\\r}
  value=${value//$'\t'/\\t}
  printf '%s' "$value"
}

append_jsonl_audit() {
  local log_file="$1"
  local script_name="$2"
  local run_dir="$3"
  local event="$4"
  local identity="$5"
  local source_system="$6"
  local target_resource="$7"
  local action="$8"
  local result="$9"
  local failure_reason="${10-}"
  local details="${11-}"

  mkdir -p "$(dirname "$log_file")"
  printf '{"timestamp":"%s","script":"%s","run_dir":"%s","event":"%s","identity":"%s","source":"%s","target":"%s","action":"%s","result":"%s","failure_reason":"%s","details":"%s"}\n' \
    "$(json_escape "$(date '+%F %T %z')")" \
    "$(json_escape "$script_name")" \
    "$(json_escape "$run_dir")" \
    "$(json_escape "$event")" \
    "$(json_escape "$identity")" \
    "$(json_escape "$source_system")" \
    "$(json_escape "$target_resource")" \
    "$(json_escape "$action")" \
    "$(json_escape "$result")" \
    "$(json_escape "$failure_reason")" \
    "$(json_escape "$details")" >>"$log_file"
}

summary_value() {
  local key="$1"
  local summary_file="$2"
  local line

  line=$(grep -m1 "^${key}=" "$summary_file" 2>/dev/null || true)
  printf '%s' "${line#*=}"
}

replace_markdown_block() {
  local target_file="$1"
  local begin_marker="$2"
  local end_marker="$3"
  local content_file="$4"
  local tmp_file

  tmp_file=$(mktemp)
  awk \
    -v begin_marker="$begin_marker" \
    -v end_marker="$end_marker" \
    -v content_file="$content_file" \
    '
      $0 == begin_marker {
        print
        while ((getline line < content_file) > 0) {
          print line
        }
        close(content_file)
        in_block = 1
        next
      }
      $0 == end_marker {
        in_block = 0
        print
        next
      }
      !in_block {
        print
      }
    ' "$target_file" >"$tmp_file"
  mv "$tmp_file" "$target_file"
}
