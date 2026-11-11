#!/usr/bin/env bash
# p2-du-census.sh —— 反模式 P2 容量取证（用软链拼存储后依赖 du 报数）
#
# 依据：docs/retrospective/reports/project-reports/retrospective-openkylin-podman-ai-20261111/
#       actionable-items.md §2（识别信号 2.1 / 口径修正 2.2 / 门禁 2.3 / 验收 2.4）
#
# 三条口径（A6 快照脚本的直接复用件）：
#   ① 取数前 readlink -f，绝不对软链字面值 du；
#   ② 取数用 podman unshare，落在用户命名空间内读小写层；
#   ③ 必须带 -x，并同时记录挂载点与设备号。
#
# df/du 交叉校验的口径修正：
#   actionable-items.md §2.3 写「df 与 du 差异超 10% 即非零退出」，该判据只在目标挂载点
#   被 podman 独占时成立。本例 /media/pc/data 为 15T 共享盘（df used ≈15.67 TB，
#   du 约 80 GB），等值比较必然假 FAIL。故默认只做「du ≤ df.used」必要条件校验；
#   需要 10% 等值判据时显式传 --exclusive-mount。
#
# 用法：
#   ./p2-du-census.sh [--check] [--json] [--exclusive-mount] [--no-timestamp] [--dir <真实路径>]
#
# 退出码：0=PASS  1=FAIL  2=用法或依赖缺失

set -uo pipefail

PROG=${0##*/}
MODE=snapshot # snapshot | check | json
EXCLUSIVE=0
TIMESTAMP=1
TARGET_ROOT=""
FAILS=0
WARNS=0
PASSES=0

usage() {
  cat <<'EOF'
用法: p2-du-census.sh [选项]

  (无选项)            人读快照：三口径取数 + df/du 交叉校验 + 逐项判定
  --check             只输出最终 PASS/FAIL 与关键数字，退出码 0=PASS 1=FAIL
  --json              结构化输出（键序固定）；配合 --no-timestamp 可连跑两次直接 diff
  --exclusive-mount   声明目标挂载点由 podman 独占，启用 df/du 10% 等值判据
  --no-timestamp      输出中省略采集时间，便于 diff
  --dir <真实路径>    覆盖取数根目录（默认取 podman graphRoot 解析后的真实路径）
  -h, --help          显示本帮助

判定项：
  D1 取数根目录可解析为存在的真实路径
  D2 软链陷阱：对 graphRoot 字面值 du 是否返回 0/4.0K
  D3 userns 口径取数成功，且 stderr 无 Permission denied
  D4 graphRoot 与 volumePath 同设备（否则 -x 会漏计跨挂载部分）
  D5 du 总量 ≤ df.used（必要条件，违反即漏计或重复计）
  D6 |du - df.used| / df.used ≤ 10%（仅 --exclusive-mount）
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --check) MODE=check ;;
    --json) MODE=json ;;
    --exclusive-mount) EXCLUSIVE=1 ;;
    --no-timestamp) TIMESTAMP=0 ;;
    --dir)
      [ $# -ge 2 ] || { echo "缺少 --dir 的参数" >&2; exit 2; }
      TARGET_ROOT=$2
      shift
      ;;
    -h | --help) usage; exit 0 ;;
    *)
      echo "未知参数: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

die() {
  echo "$PROG: $*" >&2
  exit 2
}

for c in podman jq stat findmnt readlink du df awk grep; do
  command -v "$c" >/dev/null 2>&1 || die "缺少依赖: $c"
done

record() { # kind key label detail —— 人类可读时直接打印，--check 时静默
  local kind=$1 key=$2 label=$3 detail=${4:-}
  case "$kind" in
    PASS) PASSES=$((PASSES + 1)) ;;
    FAIL) FAILS=$((FAILS + 1)) ;;
    WARN) WARNS=$((WARNS + 1)) ;;
  esac
  if [ "$MODE" = snapshot ]; then
    printf '[%s] %-2s %s\n' "$kind" "$key" "$label"
    [ -n "$detail" ] && printf '          %s\n' "$detail"
  fi
}

[ "$MODE" = snapshot ] && printf '== P2 容量取证 ==\n'

# ---- 取数根目录 ----
GRAPH_LITERAL=$(podman info --format '{{.Store.GraphRoot}}' 2>/dev/null) || die "podman info 执行失败"
VOL_PATH=$(podman info --format '{{.Store.VolumePath}}' 2>/dev/null) || die "podman info 执行失败"

if [ -n "$TARGET_ROOT" ]; then
  GRAPH_LITERAL=$TARGET_ROOT
fi

REAL=$(readlink -f "$GRAPH_LITERAL" 2>/dev/null)
if [ -z "$REAL" ] || [ ! -d "$REAL" ]; then
  record FAIL D1 "取数根目录无法解析为存在的目录" "字面值=$GRAPH_LITERAL"
  REAL=${REAL:-$GRAPH_LITERAL}
else
  record PASS D1 "取数根目录为存在的真实路径" "字面值=$GRAPH_LITERAL 真实路径=$REAL"
fi

DEV_REAL=$(stat -c %d "$REAL" 2>/dev/null || echo "?")
DEV_VOL=$(stat -c %d "$VOL_PATH" 2>/dev/null || echo "?")
FSTYPE=$(findmnt -no FSTYPE --target "$REAL" 2>/dev/null || echo "?")
MOUNT_TARGET=$(findmnt -no TARGET --target "$REAL" 2>/dev/null || echo "?")
MOUNT_SRC=$(findmnt -no SOURCE --target "$REAL" 2>/dev/null || echo "?")

# ---- D2 软链陷阱 ----
LITERAL_SIZE=$(du -sh "$GRAPH_LITERAL" 2>/dev/null | awk '{print $1}')
LITERAL_BYTES=$(du -sB1 "$GRAPH_LITERAL" 2>/dev/null | awk '{print $1}')
if [ -z "$LITERAL_BYTES" ]; then
  record WARN D2 "字面值路径 du 无输出" "path=$GRAPH_LITERAL"
elif [ "$LITERAL_BYTES" -le 4096 ]; then
  record WARN D2 "软链字面值 du 返回近似 0，属假数" \
    "du -sh 得 ${LITERAL_SIZE:-0}；该值不得进入任何容量结论，取数必须走 readlink -f"
else
  record PASS D2 "字面值路径 du 非零，未命中软链陷阱" "du -sh=$LITERAL_SIZE"
fi

# ---- 取数目标 ----
TARGETS=()
for d in overlay volumes; do
  [ -d "$REAL/$d" ] && TARGETS+=("$REAL/$d")
done
if [ ${#TARGETS[@]} -eq 0 ]; then
  TARGETS=("$REAL")
fi

# ---- userns 口径 ----
if podman unshare true >/dev/null 2>&1; then
  DU_CMD="podman unshare du"
  DU_MODE=userns
else
  DU_CMD="du"
  DU_MODE=host
  record WARN D3 "podman unshare 不可用，退回宿主 du" "宿主 du 读到子 uid 目录会报 Permission denied，结果为下限"
fi

OUT_FILE=$(mktemp)
ERR_FILE=$(mktemp)
# shellcheck disable=SC2086
$DU_CMD -sxB1 "${TARGETS[@]}" >"$OUT_FILE" 2>"$ERR_FILE"
DU_RC=$?

DENY=$(grep -c 'Permission denied' "$ERR_FILE" 2>/dev/null || true)
DENY=${DENY:-0}
ERR_LINES=$(wc -l <"$ERR_FILE" | tr -d ' ')

DU_TOTAL=0
DU_ITEMS=""
DU_LINES=()
while IFS=$'\t' read -r bytes path; do
  case "$bytes" in
    '' | *[!0-9]*) continue ;;
  esac
  DU_TOTAL=$((DU_TOTAL + bytes))
  DU_LINES+=("$bytes|$path")
  [ -n "$DU_ITEMS" ] && DU_ITEMS="$DU_ITEMS,"
  DU_ITEMS="$DU_ITEMS{\"path\":$(jq -cn --arg p "$path" '$p'),\"bytes\":$bytes}"
done <"$OUT_FILE"

if [ "$DU_RC" -ne 0 ] || [ "$DU_TOTAL" -eq 0 ]; then
  record FAIL D3 "userns 口径取数失败或结果为零" "rc=$DU_RC mode=$DU_MODE stderr_lines=$ERR_LINES"
elif [ "$DENY" -gt 0 ]; then
  record FAIL D3 "userns 口径仍出现权限拒绝，结果为下限" \
    "Permission denied=$DENY 行；用 stat -c '%U:%G %a' 查归属，禁止 sudo chmod -R 777"
else
  record PASS D3 "userns 口径取数成功且无权限拒绝" "mode=$DU_MODE elapsed_ok targets=${#TARGETS[@]}"
fi
rm -f "$OUT_FILE" "$ERR_FILE"

# ---- D4 同一文件系统 ----
if [ "$DEV_REAL" = "?" ] || [ "$DEV_VOL" = "?" ]; then
  record FAIL D4 "无法取得设备号" "devGraphRoot=$DEV_REAL devVolumePath=$DEV_VOL"
elif [ "$DEV_REAL" = "$DEV_VOL" ]; then
  record PASS D4 "graphRoot 与 volumePath 同设备，-x 不会漏计" "dev=$DEV_REAL"
else
  record FAIL D4 "graphRoot 与 volumePath 跨设备，-x 会漏计" \
    "devGraphRoot=$DEV_REAL devVolumePath=$DEV_VOL；须先按 P1 收敛到同一挂载点"
fi

# ---- df 口径 ----
DF_LINE=$(df -B1 --output=source,fstype,size,used,avail,target "$REAL" 2>/dev/null | tail -1)
DF_SRC=$(awk '{print $1}' <<<"$DF_LINE")
DF_TYPE=$(awk '{print $2}' <<<"$DF_LINE")
DF_SIZE=$(awk '{print $3}' <<<"$DF_LINE")
DF_USED=$(awk '{print $4}' <<<"$DF_LINE")
DF_AVAIL=$(awk '{print $5}' <<<"$DF_LINE")
DF_TARGET=$(awk '{for (i = 6; i <= NF; i++) printf "%s%s", $i, (i < NF ? " " : "")}' <<<"$DF_LINE")
case "$DF_USED" in
  '' | *[!0-9]*)
    record FAIL D5 "df 取数失败" "line=$DF_LINE"
    DF_USED=0
    ;;
  *) ;;
esac

# ---- D5 必要条件：du ≤ df.used ----
if [ "$DF_USED" -gt 0 ]; then
  if [ "$DU_TOTAL" -le "$DF_USED" ]; then
    PCT=$(awk -v a="$DU_TOTAL" -v b="$DF_USED" 'BEGIN{printf "%.4f", (b > 0 ? a / b * 100 : 0)}')
    record PASS D5 "du 总量不超过 df.used（无重复计）" \
      "du=${DU_TOTAL}B df.used=${DF_USED}B 占挂载点已用 ${PCT}%"
  else
    record FAIL D5 "du 总量大于 df.used，存在重复计或跨挂载混入" \
      "du=${DU_TOTAL}B df.used=${DF_USED}B"
  fi
fi

# ---- D6 仅在独占挂载点下启用 10% 等值判据 ----
if [ "$EXCLUSIVE" = 1 ] && [ "$DF_USED" -gt 0 ]; then
  DIFF_PCT=$(awk -v a="$DU_TOTAL" -v b="$DF_USED" 'BEGIN{d=(a>b?a-b:b-a); printf "%.2f", (b > 0 ? d / b * 100 : 100)}')
  if awk -v p="$DIFF_PCT" 'BEGIN{exit !(p <= 10)}'; then
    record PASS D6 "df/du 差异在 10% 以内" "差异 ${DIFF_PCT}%"
  else
    record FAIL D6 "df/du 差异超过 10%" "差异 ${DIFF_PCT}%；检查跨挂载点或稀疏文件"
  fi
else
  record SKIP D6 "跳过 df/du 10% 等值判据" \
    "挂载点 $DF_TARGET 为共享盘，df.used=${DF_USED}B 含非容器数据；需要等值判据时加 --exclusive-mount"
fi

if [ "$FAILS" -eq 0 ]; then STATUS=PASS; RC=0; else STATUS=FAIL; RC=1; fi

# ---- 输出 ----
if [ "$MODE" = json ]; then
  TS=""
  [ "$TIMESTAMP" = 1 ] && TS=$(date -Iseconds)
  jq -n \
    --arg ts "$TS" \
    --arg status "$STATUS" \
    --arg real "$REAL" \
    --arg literal "$GRAPH_LITERAL" \
    --arg vol "$VOL_PATH" \
    --arg fstype "$FSTYPE" \
    --arg mnt "$MOUNT_TARGET" \
    --arg src "$MOUNT_SRC" \
    --arg devG "$DEV_REAL" \
    --arg devV "$DEV_VOL" \
    --arg du_mode "$DU_MODE" \
    --argjson du_bytes "$DU_TOTAL" \
    --argjson du_items "[$DU_ITEMS]" \
    --argjson deny "$DENY" \
    --arg df_src "$DF_SRC" \
    --arg df_type "$DF_TYPE" \
    --argjson df_size "${DF_SIZE:-0}" \
    --argjson df_used "${DF_USED:-0}" \
    --argjson df_avail "${DF_AVAIL:-0}" \
    --arg df_target "$DF_TARGET" \
    --argjson pass "$PASSES" \
    --argjson fail "$FAILS" \
    --argjson warn "$WARNS" \
    '{
      schema: "p2-du-census/1",
      collected_at: $ts,
      status: $status,
      storage: {
        graph_root_literal: $literal,
        real_path: $real,
        volume_path: $vol,
        fstype: $fstype,
        mount_source: $src,
        mount_target: $mnt,
        dev_graph_root: $devG,
        dev_volume_path: $devV
      },
      du: { mode: $du_mode, total_bytes: $du_bytes, permission_denied: $deny, items: $du_items },
      df: { source: $df_src, fstype: $df_type, size: $df_size, used: $df_used, avail: $df_avail, target: $df_target },
      summary: { pass: $pass, fail: $fail, warn: $warn }
    }'
  exit "$RC"
fi

if [ "$MODE" = check ]; then
  printf '%s du=%sB df.used=%sB deny=%s fail=%s\n' "$STATUS" "$DU_TOTAL" "$DF_USED" "$DENY" "$FAILS"
  exit "$RC"
fi

printf '\n-- 取数明细 --\n'
printf 'graphRoot 字面值 : %s\n' "$GRAPH_LITERAL"
printf '真实路径         : %s\n' "$REAL"
printf 'volumePath       : %s\n' "$VOL_PATH"
printf '挂载源/类型/挂载点: %s / %s / %s\n' "$MOUNT_SRC" "$FSTYPE" "$MOUNT_TARGET"
printf '设备号           : graphRoot=%s volumePath=%s\n' "$DEV_REAL" "$DEV_VOL"
printf 'du 口径          : %s\n' "$DU_MODE"
printf 'du 明细          :\n'
for item in "${DU_LINES[@]}"; do
  printf '  %s\t%s\n' "${item%%|*}" "${item#*|}"
done
[ ${#DU_LINES[@]} -eq 0 ] && printf '  (无)\n'
printf 'du 总量          : %s B\n' "$DU_TOTAL"
printf 'df 总量/已用/可用 : %s / %s / %s B\n' "$DF_SIZE" "$DF_USED" "$DF_AVAIL"
printf '== 汇总: %s（PASS %d / FAIL %d / WARN %d）==\n' "$STATUS" "$PASSES" "$FAILS" "$WARNS"

exit "$RC"