#!/usr/bin/env bash
# p1p2-remediate.sh —— 反模式 P1/P2 的可执行修复脚本
#
# 依据：docs/retrospective/reports/project-reports/retrospective-openkylin-podman-ai-20261111/
#       actionable-items.md §1（P1）、§2（P2）、§6.1（同批次落地）
#
# 修复对象：rootless podman 的 graphRoot/volumePath 依赖软链层，导致
#           ① 存储路径不唯一（P1 A1）；② 对字面值 du 得到 0 的假数（P2）。
#
# 两种模式：
#   config（默认）  零拷贝：仅写 ~/.config/containers/storage.conf，令 podman 直接使用
#                   graphRoot 的真实路径；数据原地不动，软链退为兼容别名（可选 --drop-symlink 改名）。
#   move（--target）真实搬迁：podman unshare rsync 到新目录，校验字节数与文件数后再切换配置；
#                   旧数据保留不动，清理须人类批准。
#
# 安全边界：
#   - 默认 dry-run，只打印计划，不写任何文件；
#   - --execute 必须在交互式终端输入确认串 MIGRATE 才执行；
#   - move 模式在存在运行中容器时直接拒绝（退出 78）；
#   - config 模式在存在运行中容器时告警，须显式 --allow-running；
#   - 任何一步切换后校验失败即自动回滚 storage.conf。
#
# 口径订正（本轮实测）：
#   rootless 下 ~/.config/containers/storage.conf 的 graphroot 是生效的（受控实验：HOME 指向
#   临时目录并写入 storage.conf，podman info 返回该目录）。此前「rootless 下不生效、只有全局
#   --root 可改写」的结论不成立，仅 --root 为单次覆盖手段，不能持久化。
#   同 inode 归一回退（二次实测）：当 graphroot 与 ~/.local/share/containers/storage 为同一
#   目录（软链同源）时，podman 输出 graphRoot 仍为默认字面值，storage.conf 无效。此时本脚本
#   判定为「设计性别名、无需变更」并以 0 退出；要摆脱别名只能 move 到新目录。
#
# 用法：
#   ./p1p2-remediate.sh                               # dry-run，config 模式计划
#   ./p1p2-remediate.sh --execute                     # 执行 config 模式（同盘零拷贝）
#   ./p1p2-remediate.sh --target /path --execute      # 执行 move 模式（真实搬迁）
#   ./p1p2-remediate.sh --execute --drop-symlink      # 切换成功后把 $HOME 别名软链改名退役
#
# 退出码：0=成功或 dry-run  1=校验失败（已回滚）  2=用法或依赖缺失  78=前提不满足需人工处理

set -uo pipefail

PROG=${0##*/}
EXECUTE=0
DROP_SYMLINK=0
ALLOW_RUNNING=0
DEEP_CHECK=0
TARGET_DIR=""
BACKUP_ROOT="$HOME/.local/state/podman-remediation"
CONF="$HOME/.config/containers/storage.conf"
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR=""

usage() {
  cat <<'EOF'
用法: p1p2-remediate.sh [选项]

  (无选项)               dry-run，输出 config 模式完整计划
  --execute              真正执行（交互式输入 MIGRATE 确认）
  --target <目录>        使用 move 模式，把存储搬迁到该目录后再切换
  --drop-symlink         切换成功后把 graphRoot 字面值的软链改名为 .symlink-bak-<时间>
  --allow-running        config 模式下允许存在运行中容器（move 模式始终拒绝）
  --deep-check           切换后追加 podman system check（全量扫描，耗时可达分钟级）
  -h, --help             显示本帮助

模式对比：
  config  零拷贝，只改配置；仅当目标与 rootless 默认路径不同源时才会改变 graphRoot
          （本机两者同 inode，故 config 模式会直接判「无需变更」并退出 0）
  move    真实搬迁，含 rsync + 字节数/文件数双重校验；适用于数据需换盘或换目录的场景

判定项（执行前全部通过才动手）：
  C1 podman 为 rootless
  C2 目标挂载点文件系统属 xfs/ext4/btrfs（cifs/smb3/nfs/9p/fuse/NTFS 直接拒绝）
  C3 目标与源不同路径（否则已唯一，无需修复）
  C4 move 模式目标目录为空且可用空间 ≥ 数据量 × 1.05
  C5 move 模式无运行中容器；config 模式默认也要求无运行中容器
  C6 目标与 rootless 默认路径（~/.local/share/containers/storage）非同一 inode；
     config 模式下同源即视为设计性别名，输出「无需变更」并以 0 退出
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --execute) EXECUTE=1 ;;
    --drop-symlink) DROP_SYMLINK=1 ;;
    --allow-running) ALLOW_RUNNING=1 ;;
    --deep-check) DEEP_CHECK=1 ;;
    --target)
      [ $# -ge 2 ] || { echo "缺少 --target 的参数" >&2; exit 2; }
      TARGET_DIR=$2
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

say() { printf '%s\n' "$*"; }

# 显示宽度：ASCII 与 2 字节字符计 1，3/4 字节 UTF-8（CJK、全角标点）计 2。
# 不用 printf 的 %-Ns：那按字节补齐，中文标签会参差不齐。
disp_width() {
  local LC_ALL=C s=$1 i b w=0
  for ((i = 0; i < ${#s}; i++)); do
    b=$(printf '%d' "'${s:i:1}")
    if [ "$b" -lt 128 ]; then
      w=$((w + 1))
    elif [ "$b" -lt 192 ]; then
      w=$((w + 0))
    elif [ "$b" -lt 224 ]; then
      w=$((w + 1))
    else
      w=$((w + 2))
    fi
  done
  printf '%s' "$w"
}

KV_WIDTH=22
kv() {
  local pad
  pad=$((KV_WIDTH - $(disp_width "$1")))
  [ "$pad" -lt 1 ] && pad=1
  printf '  %s%*s%s\n' "$1" "$pad" '' "$2"
}

for c in podman jq readlink stat findmnt df awk; do
  command -v "$c" >/dev/null 2>&1 || die "缺少依赖: $c"
done
if [ -n "$TARGET_DIR" ] && ! command -v rsync >/dev/null 2>&1; then
  die "move 模式缺少依赖: rsync"
fi

# ---- 现状取数 ----
LITERAL=$(podman info --format '{{.Store.GraphRoot}}' 2>/dev/null) || die "podman info 执行失败"
REAL=$(readlink -f "$LITERAL" 2>/dev/null)
[ -n "$REAL" ] || die "无法解析 graphRoot 字面值: $LITERAL"
RUNROOT=$(podman info --format '{{.Store.RunRoot}}' 2>/dev/null)
CUR_VOL=$(podman info --format '{{.Store.VolumePath}}' 2>/dev/null)
CUR_DRIVER=$(podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null)

if [ -n "$TARGET_DIR" ]; then
  MODE=move
  TARGET=$(realpath -m "$TARGET_DIR" 2>/dev/null || echo "$TARGET_DIR")
else
  MODE=config
  TARGET=$REAL
fi

# 同 inode 判定：podman 5.6 在 graphroot 与 rootless 默认路径指向同一目录（软链同源）时，
# 会把 graphRoot 归一回退为默认字面值，写 storage.conf 也不会改变输出。故须先判同源。
DEFAULT_ROOTLESS="$HOME/.local/share/containers/storage"
SAME_INODE=0
if [ -e "$TARGET" ] && [ -e "$DEFAULT_ROOTLESS" ]; then
  # 必须 -L：不带 -L 的 stat 取的是软链自身 inode，会漏判同源
  if [ "$(stat -Lc %d:%i "$TARGET" 2>/dev/null)" = "$(stat -Lc %d:%i "$DEFAULT_ROOTLESS" 2>/dev/null)" ]; then
    SAME_INODE=1
  fi
fi

# 逐级向上找到第一个存在的祖先，取其挂载信息
probe_existing() {
  local p=$1
  while [ ! -e "$p" ] && [ "$p" != "/" ]; do p=$(dirname "$p"); done
  printf '%s' "$p"
}
PROBE=$(probe_existing "$TARGET")
FSTYPE=$(findmnt -no FSTYPE --target "$PROBE" 2>/dev/null || echo "?")
MOUNT_SRC=$(findmnt -no SOURCE --target "$PROBE" 2>/dev/null || echo "?")
MOUNT_TGT=$(findmnt -no TARGET --target "$PROBE" 2>/dev/null || echo "?")
DEV_REAL=$(stat -c %d "$REAL" 2>/dev/null || echo "?")
DEV_TGT=$(stat -c %d "$PROBE" 2>/dev/null || echo "?")

RUNNING=$(podman ps -q 2>/dev/null | wc -l | tr -d ' ')
IMG_BASE=$(podman images -q 2>/dev/null | wc -l | tr -d ' ')
VOL_BASE=$(podman volume ls -q 2>/dev/null | wc -l | tr -d ' ')

# 数据量：必须走 userns，且对真实路径取数。
# 用 printf "%.0f" 输出整数：部分 awk（mawk）的 print 会走 OFMT %.6g，98G 级数值会变成 8.00876e+10。
du_bytes() {
  podman unshare du -sxB1 "$@" 2>/dev/null | awk '{s += $1} END {printf "%.0f\n", s + 0}'
}
SRC_BYTES=$(du_bytes "$REAL")
AVAIL_BYTES=$(df -B1 --output=avail "$PROBE" 2>/dev/null | tail -1 | tr -d ' ')

# ---- 判定 ----
FAILS=0
CHECKS=()
check() { # id label status detail
  local id=$1 label=$2 st=$3 detail=${4:-}
  CHECKS+=("$id|$label|$st|$detail")
  [ "$st" = FAIL ] && FAILS=$((FAILS + 1))
}

IS_ROOTLESS=$(podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null)
if [ "$IS_ROOTLESS" = "true" ]; then
  check C1 "podman 为 rootless" PASS "uid=$(id -u)"
else
  check C1 "podman 为 rootless" WARN "非 rootless（rootful），存储口径与本文不符，脚本仍可执行但请人工复核"
fi

case "$FSTYPE" in
  xfs | ext4 | btrfs) check C2 "目标底层文件系统满足 overlay 要求" PASS "fstype=$FSTYPE src=$MOUNT_SRC target=$MOUNT_TGT" ;;
  '?') check C2 "目标底层文件系统" FAIL "无法取得 fstype（probe=$PROBE）" ;;
  *) check C2 "目标底层文件系统满足 overlay 要求" FAIL "fstype=$FSTYPE 属网络/非块设备，overlay 不可用；只能改 vfs 或更换位置" ;;
esac

if [ "$TARGET" = "$REAL" ]; then
  if [ "$MODE" = config ]; then
    check C3 "目标路径与真实路径不同" PASS "两者相同，将只写配置不改数据（目标即现状）"
  else
    check C3 "目标路径与真实路径不同" FAIL "target 与当前真实路径相同，无需搬迁"
  fi
else
  check C3 "目标路径与真实路径不同" PASS "real=$REAL target=$TARGET"
fi

if [ "$MODE" = move ]; then
  if [ -d "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
    check C4 "目标目录为空且空间充足" FAIL "目标目录非空：$TARGET"
  else
    NEED=$((SRC_BYTES + SRC_BYTES / 20))
    if [ "${AVAIL_BYTES:-0}" -ge "$NEED" ]; then
      check C4 "目标目录为空且空间充足" PASS "需要≈$NEED B（含 5% 余量）可用=$AVAIL_BYTES B"
    else
      check C4 "目标目录为空且空间充足" FAIL "需要≈$NEED B 可用=$AVAIL_BYTES B"
    fi
  fi
else
  check C4 "目标目录为空且空间充足" SKIP "config 模式零拷贝，不适用"
fi

if [ "$RUNNING" -eq 0 ]; then
  check C5 "无运行中容器" PASS "运行中=0"
elif [ "$MODE" = move ]; then
  check C5 "无运行中容器" FAIL "运行中=$RUNNING；move 模式必须先停容器（须人类批准）"
elif [ "$ALLOW_RUNNING" = 1 ]; then
  check C5 "无运行中容器" WARN "运行中=$RUNNING，已按 --allow-running 放行"
else
  check C5 "无运行中容器" FAIL "运行中=$RUNNING；停容器或加 --allow-running（config 模式为同盘改配置）"
fi

if [ "$MODE" = config ]; then
  if [ "$SAME_INODE" = 1 ]; then
    check C6 "目标与 rootless 默认路径非同源" WARN \
      "同 inode 别名：$TARGET ≡ $DEFAULT_ROOTLESS；podman 会把 graphRoot 归一回退为默认字面值，config 模式无法改变输出"
  else
    check C6 "目标与 rootless 默认路径非同源" PASS "target=$TARGET default=$DEFAULT_ROOTLESS"
  fi
else
  check C6 "目标与 rootless 默认路径非同源" PASS "move 模式目标为新目录，不受同源归一影响"
fi

# ---- 输出：现状 + 判定 ----
say "== P1/P2 存储路径修复 =="
kv "模式" "$MODE"
kv "graphRoot 字面值" "$LITERAL"
kv "graphRoot 真实路径" "$REAL"
kv "volumePath" "$CUR_VOL"
kv "驱动 / runRoot" "$CUR_DRIVER / $RUNROOT"
kv "目标路径" "$TARGET"
kv "目标挂载点" "$MOUNT_SRC ($FSTYPE) -> $MOUNT_TGT"
kv "设备号 real/target" "$DEV_REAL / $DEV_TGT"
kv "数据量（userns）" "$SRC_BYTES B"
kv "基线 images/volumes" "$IMG_BASE / $VOL_BASE"
kv "storage.conf" "$([ -f "$CONF" ] && echo "$CONF（已存在，将被备份）" || echo "$CONF（不存在，将新建）")"
say ""
for item in "${CHECKS[@]}"; do
  IFS='|' read -r id label st detail <<<"$item"
  printf '[%s] %-2s %s\n' "$st" "$id" "$label"
  [ -n "$detail" ] && printf '          %s\n' "$detail"
done
say ""

if [ "$FAILS" -gt 0 ]; then
  say "== 结论: 前提不满足（FAIL $FAILS），不执行任何变更 =="
  exit 78
fi

# ---- 同源别名短路：无需任何变更 ----
if [ "$MODE" = config ] && [ "$SAME_INODE" = 1 ]; then
  say "-- 结论 --"
  say "目标路径与 rootless 默认路径 $DEFAULT_ROOTLESS 是同一 inode（同源别名）。"
  say "podman 5.6 此时把 graphRoot 归一回退为默认字面值，写 storage.conf 不会生效（已实测两次）。"
  say "数据本身已在本地块设备的真实路径 $REAL 上；P1 的路径不唯一只是字面值层面的别名，"
  say "P2 的 du 假数已由 readlink -f 口径消除（p2-du-census.sh 实测 PASS）。"
  say "因此本次无需任何变更：不写 storage.conf，不改动软链。"
  say ""
  say "若确需让 graphRoot 字面值摆脱别名，只能换目录（move 模式）："
  say "  ./p1p2-remediate.sh --target /media/pc/data/<新目录> --execute"
  say ""
  say "验收: ./p1-storage-guard.sh --strict && ./p2-du-census.sh --check"
  exit 0
fi

# ---- 计划 ----
CONF_TMP_CONTENT() {
  cat <<EOF
# 由 $PROG 生成于 $(date -Iseconds)
# 依据：actionable-items.md §1（P1 路径唯一化）/ §2（P2 容量口径）
# 注意：podman 5.6 的 storage.conf 不接受 [storage] volume_path 键，写入会导致
#       "Failed to decode the keys [\"storage.volume_path\"]" 并使整份配置被丢弃。
#       volumePath 默认随 graphRoot 派生为 <graphroot>/volumes，无需显式声明。
[storage]
driver = "overlay"
graphroot = "$1"
runroot = "$RUNROOT"

[storage.options]
EOF
}

print_plan() {
  local n=0
  say "-- 执行计划（$MODE）--"
  n=$((n + 1)); say "$n. 备份元数据到 $BACKUP_ROOT/$STAMP/"
  say "     podman info --format json > info.json；images/volumes 清单同理"
  if [ -f "$CONF" ]; then
    say "     cp -p $CONF $BACKUP_ROOT/$STAMP/storage.conf.before"
  fi
  if [ "$MODE" = move ]; then
    n=$((n + 1)); say "$n. 创建目标目录并搬迁（userns 内保留属主/ACL/xattr）"
    say "     mkdir -p $TARGET"
    say "     podman unshare rsync -aHAX --numeric-ids $REAL/ $TARGET/"
  fi
  n=$((n + 1)); say "$n. 写配置（原子替换）"
  say "     graphroot = \"$TARGET\"，runroot = \"$RUNROOT\"（volumePath 随 graphroot 派生为 $TARGET/volumes）"
  n=$((n + 1)); say "$n. 切换后校验"
  say "     podman info 三字段 == 期望；images/volumes 计数 == 基线 $IMG_BASE/$VOL_BASE"
  [ "$MODE" = move ] && say "     du 字节数差异 ≤1%，find 文件数一致"
  [ "$DEEP_CHECK" = 1 ] && say "     podman system check（--deep-check）"
  n=$((n + 1)); say "$n. 任一步校验失败 → 还原 storage.conf 并退出 1"
  if [ "$DROP_SYMLINK" = 1 ] && [ "$LITERAL" != "$REAL" ]; then
    n=$((n + 1)); say "$n. 校验通过后把软链退役：mv $LITERAL $LITERAL.symlink-bak-$STAMP"
    say "     仅改 \$HOME 侧别名，不触碰 .agents/podman-storage/（工作区红线 6）"
  fi
  if [ "$MODE" = move ]; then
    n=$((n + 1)); say "$n. 旧数据（$REAL）保持原样，清理须人类批准，脚本不自动删除"
  fi
  say ""
  say "-- 验收（修复后手动执行）--"
  say "  ./p1-storage-guard.sh --strict     # 期望 FAIL 0"
  say "  ./p2-du-census.sh --check          # 期望 PASS 且 deny=0"
  say ""
}

if [ "$EXECUTE" -ne 1 ]; then
  print_plan
  say "== DRY-RUN：未做任何变更。确认后加 --execute 执行 =="
  exit 0
fi

# ---- 执行前二次确认 ----
[ -t 0 ] || die "--execute 需要交互式终端以完成二次确认（非 TTY 环境拒绝执行）"
say "即将执行 $MODE 模式变更，涉及 podman 存储配置。"
printf '请输入 MIGRATE 确认执行: '
read -r ANSWER
[ "$ANSWER" = "MIGRATE" ] || { say "已取消，未做任何变更。"; exit 0; }
say ""

# ---- 备份 ----
BACKUP_DIR="$BACKUP_ROOT/$STAMP"
mkdir -p "$BACKUP_DIR" || die "无法创建备份目录: $BACKUP_DIR"
podman info --format json >"$BACKUP_DIR/info.json" 2>/dev/null || true
podman images --format json >"$BACKUP_DIR/images.json" 2>/dev/null || true
podman volume ls --format json >"$BACKUP_DIR/volumes.json" 2>/dev/null || true
ls -ld "$LITERAL" "$REAL" >"$BACKUP_DIR/paths.txt" 2>&1 || true
HAD_CONF=0
if [ -f "$CONF" ]; then
  cp -p "$CONF" "$BACKUP_DIR/storage.conf.before" || die "备份 storage.conf 失败"
  HAD_CONF=1
fi
say "已备份到 $BACKUP_DIR"

rollback_conf() {
  if [ "$HAD_CONF" = 1 ]; then
    cp -p "$BACKUP_DIR/storage.conf.before" "$CONF"
    say "已回滚 storage.conf 到变更前版本"
  else
    rm -f "$CONF"
    say "已移除本次新建的 storage.conf"
  fi
}

write_conf() {
  local root=$1
  mkdir -p "$(dirname "$CONF")" || return 1
  local tmp="$CONF.tmp.$$"
  CONF_TMP_CONTENT "$root" >"$tmp" || return 1
  mv -f "$tmp" "$CONF"
}

verify_switch() {
  local expect=$1
  local got vol drv img volc
  got=$(podman info --format '{{.Store.GraphRoot}}' 2>/dev/null)
  vol=$(podman info --format '{{.Store.VolumePath}}' 2>/dev/null)
  drv=$(podman info --format '{{.Store.GraphDriverName}}' 2>/dev/null)
  img=$(podman images -q 2>/dev/null | wc -l | tr -d ' ')
  volc=$(podman volume ls -q 2>/dev/null | wc -l | tr -d ' ')
  say "  校验 graphRoot : $got"
  say "  校验 volumePath: $vol"
  say "  校验 driver    : $drv"
  say "  校验计数       : images=$img/$IMG_BASE volumes=$volc/$VOL_BASE"
  [ "$got" = "$expect" ] || { say "  失败：graphRoot 未切换到期望值"; return 1; }
  [ "$vol" = "$expect/volumes" ] || { say "  失败：volumePath 未随 graphroot 收敛"; return 1; }
  [ "$drv" = "overlay" ] || { say "  失败：驱动不再是 overlay"; return 1; }
  [ "$img" = "$IMG_BASE" ] || { say "  失败：镜像计数与基线不一致，存储可能不可见"; return 1; }
  [ "$volc" = "$VOL_BASE" ] || { say "  失败：卷计数与基线不一致"; return 1; }
  return 0
}

# ---- move 模式：先搬迁，后切换 ----
if [ "$MODE" = move ]; then
  say "== 步骤 1/3: 搬迁数据 =="
  mkdir -p "$TARGET" || { say "无法创建目标目录"; exit 1; }
  if ! podman unshare rsync -aHAX --numeric-ids "$REAL"/ "$TARGET"/; then
    say "rsync 失败，未改动配置，源数据保持原样。"
    exit 1
  fi
  DST_BYTES=$(du_bytes "$TARGET")
  say "  源字节数 : $SRC_BYTES"
  say "  目标字节数: $DST_BYTES"
  if [ "$SRC_BYTES" -gt 0 ]; then
    DIFF=$((SRC_BYTES > DST_BYTES ? SRC_BYTES - DST_BYTES : DST_BYTES - SRC_BYTES))
    LIMIT=$((SRC_BYTES / 100))
    if [ "$DIFF" -gt "$LIMIT" ]; then
      say "  字节数差异超过 1%，视为搬迁不完整；未改动配置，源数据保持原样。"
      exit 1
    fi
  fi
  SRC_FILES=$(podman unshare find "$REAL" 2>/dev/null | wc -l | tr -d ' ')
  DST_FILES=$(podman unshare find "$TARGET" 2>/dev/null | wc -l | tr -d ' ')
  say "  源文件数 : $SRC_FILES"
  say "  目标文件数: $DST_FILES"
  if [ "$SRC_FILES" != "$DST_FILES" ]; then
    say "  文件数不一致，视为搬迁不完整；未改动配置，源数据保持原样。"
    exit 1
  fi
fi

# ---- 切换配置 ----
say "== 步骤 2/3: 切换配置 =="
if ! write_conf "$TARGET"; then
  say "写配置失败"; rollback_conf; exit 1
fi
say "  已写入 $CONF"

if ! verify_switch "$TARGET"; then
  rollback_conf
  say "== 校验失败，已回滚；存储维持原状 =="
  exit 1
fi

if [ "$DEEP_CHECK" = 1 ]; then
  say "  执行 podman system check …"
  if ! podman system check >/dev/null 2>&1; then
    say "  system check 报错，详见 podman system check 输出；配置已切换，可人工决定是否回滚"
    say "  回滚命令: cp -p $BACKUP_DIR/storage.conf.before $CONF"
    exit 1
  fi
fi

# ---- 软链退役（可选） ----
if [ "$DROP_SYMLINK" = 1 ] && [ "$LITERAL" != "$REAL" ]; then
  say "== 步骤 3/3: 退役 \$HOME 侧软链 =="
  if [ -L "$LITERAL" ]; then
    mv "$LITERAL" "$LITERAL.symlink-bak-$STAMP" || say "  软链改名失败，可稍后人工处理"
    say "  已改名: $LITERAL -> $LITERAL.symlink-bak-$STAMP"
    say "  确认无其它脚本依赖该别名后可删除该备份软链（须人类批准）"
  else
    say "  字面值不是软链，跳过"
  fi
else
  say "== 步骤 3/3: 软链保持原状（兼容别名，不加 --drop-symlink 不改动）=="
fi

say ""
say "== 完成：存储已指向真实路径 $TARGET =="
say "备份目录: $BACKUP_DIR"
[ "$MODE" = move ] && say "旧数据仍在 $REAL，清理须人类批准，脚本未删除任何数据"
say "验收: ./p1-storage-guard.sh --strict && ./p2-du-census.sh --check"
exit 0