#!/usr/bin/env bash
# p1-storage-guard.sh —— 反模式 P1 门禁与修复计划（在网络盘/SMB 放容器存储或 VHDX）
#
# 依据：docs/retrospective/reports/project-reports/retrospective-openkylin-podman-ai-20261111/
#       actionable-items.md §1（识别信号 1.1 / 立即修复 1.2 / 门禁 1.3 / 验收 1.4）
#
# 行为约定（与 §0 变更审批条款一致）：
#   - 默认只读：不写配置、不改 podman 运行状态、不迁移数据。
#   - --apply 只做两件事：备份已存在的 storage.conf、打印人工执行步骤；随后退出码 78。
#     迁移数据、删除软链、podman system migrate 一律留给人类批准后手工执行。
#   - Windows 侧 vhdx 的卷类型判定无法在服务器执行，见文件末尾提示。
#
# 用法：
#   ./p1-storage-guard.sh [--strict] [--apply] [--json]
#
# 退出码：0=PASS  1=FAIL  2=用法或依赖缺失  78=需人工批准执行修复

set -uo pipefail

PROG=${0##*/}
STRICT=0
APPLY=0
JSON=0
FAILS=0
WARNS=0
PASSES=0
ITEMS=()

usage() {
  cat <<'EOF'
用法: p1-storage-guard.sh [选项]

  (无选项)    只读审计，逐项输出 PASS/FAIL/WARN/SKIP，退出码 0=PASS 1=FAIL
  --strict    保留严格口径开关（当前 S7 恒记 WARN，本开关不改变判定与退出码）
  --apply     有 FAIL 时备份 storage.conf 并打印人工修复步骤，退出码 78
  --json      机器可读输出（键序固定，便于 diff）
  -h, --help  显示本帮助

判定项：
  S1  podman 可用且为 rootless
  S2  graphRoot 可解析为存在的真实路径
  S3  真实路径底层文件系统 ∈ {xfs, ext4, btrfs}
  S4  graphStatus["Supports d_type"] == true
  S5  graphStatus["Native Overlay Diff"] == true（graphDriver=overlay 时）
  S6  graphRoot 与 volumePath 设备号一致（同一文件系统）
  S7  graphRoot 字面值不含软链层（仅提示，恒记 WARN）
  W1  storage.conf 存在性与 rootless 生效性提示

Windows 侧（在 PowerShell 中单独执行，DriveType=3 为允许的本地固定盘）：
  Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID,DriveType,FileSystem
EOF
}

for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    --apply) APPLY=1 ;;
    --json) JSON=1 ;;
    -h | --help) usage; exit 0 ;;
    *)
      echo "未知参数: $arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done

record() { # kind key label [detail]
  local kind=$1 key=$2 label=$3 detail=${4:-}
  case "$kind" in
    PASS) PASSES=$((PASSES + 1)) ;;
    FAIL) FAILS=$((FAILS + 1)) ;;
    WARN) WARNS=$((WARNS + 1)) ;;
  esac
  if [ "$JSON" = 1 ]; then
    ITEMS+=("$(jq -cn --arg k "$key" --arg s "$kind" --arg l "$label" --arg d "$detail" \
      '{key:$k,status:$s,label:$l,detail:$d}')")
  else
    printf '[%s] %-2s %s\n' "$kind" "$key" "$label"
    [ -n "$detail" ] && printf '          %s\n' "$detail"
  fi
}

die() {
  echo "$PROG: $*" >&2
  exit 2
}

for c in podman jq stat findmnt readlink; do
  command -v "$c" >/dev/null 2>&1 || die "缺少依赖: $c"
done

STORE=$(podman info --format json 2>/dev/null) || die "podman info 执行失败（检查 rootless 会话与 XDG_RUNTIME_DIR）"

GRAPH_LITERAL=$(jq -r '.store.graphRoot' <<<"$STORE")
VOL_PATH=$(jq -r '.store.volumePath' <<<"$STORE")
DRIVER=$(jq -r '.store.graphDriverName' <<<"$STORE")
ROOTLESS=$(jq -r '.host.security.rootless' <<<"$STORE")
if [ "$ROOTLESS" = "null" ] || [ -z "$ROOTLESS" ]; then
  if [ "$(id -u)" -ne 0 ]; then ROOTLESS=true; else ROOTLESS=false; fi
fi

gs() { # 取 graphStatus 单值；键不存在时返回 missing（注意不能用 jq 的 // ，false 会被吞）
  jq -r --arg k "$1" '.store.graphStatus
    | if has($k) then (.[$k] | tostring) else "missing" end' <<<"$STORE"
}

[ "$JSON" = 1 ] || printf '== P1 存储门禁 ==\n'

# S1 rootless
if [ "$ROOTLESS" = "true" ]; then
  record PASS S1 "podman 为 rootless 模式" "uid=$(id -u) podman=$(podman --version | awk '{print $3}')"
else
  record WARN S1 "podman 非 rootless 模式" "rootful 下 storage.conf 的 graphroot 才生效，判定口径需相应调整"
fi

# S2 graphRoot 真实路径
REAL=$(readlink -f "$GRAPH_LITERAL" 2>/dev/null)
if [ -n "$REAL" ] && [ -d "$REAL" ]; then
  record PASS S2 "graphRoot 可解析为存在的真实路径" "字面值=$GRAPH_LITERAL 真实路径=$REAL"
else
  record FAIL S2 "graphRoot 无法解析为存在的目录" "字面值=$GRAPH_LITERAL"
  REAL=${REAL:-$GRAPH_LITERAL}
fi

# S3 底层文件系统白名单
FSTYPE=$(findmnt -no FSTYPE --target "$REAL" 2>/dev/null || true)
case "$FSTYPE" in
  xfs | ext4 | btrfs)
    record PASS S3 "底层文件系统为本地块设备类型" "fstype=$FSTYPE driver=$DRIVER"
    ;;
  "")
    record FAIL S3 "无法取得底层文件系统类型" "findmnt --target $REAL 无输出"
    ;;
  *)
    if [ "$DRIVER" = "overlay" ]; then
      record FAIL S3 "底层文件系统不满足 overlay 语义要求" \
        "fstype=$FSTYPE（白名单 xfs/ext4/btrfs）；网络盘与 NTFS/9p/fuse 均不满足 F1"
    else
      record WARN S3 "底层文件系统非本地块设备类型" \
        "fstype=$FSTYPE，driver=$DRIVER；非 overlay 驱动可继续，但须在交付文档标注性能与体积代价"
    fi
    ;;
esac

# S4 d_type
DTYPE=$(gs "Supports d_type")
if [ "$DTYPE" = "true" ]; then
  record PASS S4 'graphStatus["Supports d_type"] 为 true' "Supports d_type=$DTYPE"
else
  record FAIL S4 'graphStatus["Supports d_type"] 不为 true' \
    "Supports d_type=$DTYPE；overlay 依赖 d_type，缺失时目录合并会静默错乱（F1）"
fi

# S5 Native Overlay Diff
NODIFF=$(gs "Native Overlay Diff")
if [ "$DRIVER" = "overlay" ]; then
  if [ "$NODIFF" = "true" ]; then
    record PASS S5 'graphStatus["Native Overlay Diff"] 为 true' "Native Overlay Diff=$NODIFF"
  else
    record FAIL S5 'graphStatus["Native Overlay Diff"] 不为 true' \
      "Native Overlay Diff=$NODIFF；退化为 slow/naive diff，镜像层复用失效"
  fi
else
  record SKIP S5 'Native Overlay Diff 判定不适用' "graphDriverName=$DRIVER"
fi

# S6 同一文件系统
DEV_REAL=$(stat -c %d "$REAL" 2>/dev/null || echo "?")
DEV_VOL=$(stat -c %d "$VOL_PATH" 2>/dev/null || echo "?")
if [ "$DEV_REAL" = "?" ] || [ "$DEV_VOL" = "?" ]; then
  record FAIL S6 "无法取得 graphRoot/volumePath 设备号" "devGraphRoot=$DEV_REAL devVolumePath=$DEV_VOL"
elif [ "$DEV_REAL" = "$DEV_VOL" ]; then
  record PASS S6 "graphRoot 与 volumePath 在同一文件系统" "dev=$DEV_REAL volumePath=$VOL_PATH"
else
  record FAIL S6 "graphRoot 与 volumePath 跨文件系统" \
    "devGraphRoot=$DEV_REAL devVolumePath=$DEV_VOL；du -x 会漏计，且卷与镜像分处两盘"
fi

# S7 软链层（同 inode 别名属设计性，--strict 下亦只记 WARN）
if [ "$GRAPH_LITERAL" = "$REAL" ]; then
  record PASS S7 "graphRoot 字面值即真实路径，无软链层" "path=$REAL"
else
  if [ "$STRICT" = 1 ]; then
    record WARN S7 "graphRoot 字面值含软链层（--strict 下仍记 WARN）" \
      "字面值=$GRAPH_LITERAL -> 真实=$REAL；与 rootless 默认路径同 inode，podman 会将 graphRoot 归一回退为默认字面值，去软链无法经 storage.conf 实现；数据已在本地真实路径，硬风险由 S3 判定"
  else
    record WARN S7 "graphRoot 字面值含软链层" \
      "字面值=$GRAPH_LITERAL -> 真实=$REAL；rootless 默认路径固定，软链是当前等效手段（A1 已用设备号+fstype 三入口一致性取证）"
  fi
fi

# W1 storage.conf
CONF_FOUND=0
for f in "$HOME/.config/containers/storage.conf" /etc/containers/storage.conf; do
  if [ -f "$f" ]; then
    CONF_FOUND=1
    record WARN W1 "发现 storage.conf" "$f（rootless 下 graphroot 项不生效，A1 实测；需用 --root 或封装脚本才能改写）"
  fi
done
if [ "$CONF_FOUND" = 0 ]; then
  record WARN W1 "未发现 storage.conf" \
    "~/.config/containers/storage.conf 与 /etc/containers/storage.conf 均不存在；rootless 的 graphRoot 由 podman 内置默认值决定"
fi

if [ "$FAILS" -eq 0 ]; then STATUS=PASS; RC=0; else STATUS=FAIL; RC=1; fi

if [ "$JSON" = 1 ]; then
  if [ ${#ITEMS[@]} -eq 0 ]; then
    ITEMS=('{}')
  fi
  printf '%s\n' "${ITEMS[@]}" | jq -s \
    --arg status "$STATUS" --argjson p "$PASSES" --argjson f "$FAILS" --argjson w "$WARNS" \
    '{checks: ., summary: {status: $status, pass: $p, fail: $f, warn: $w}}'
else
  printf '== 汇总: %s（PASS %d / FAIL %d / WARN %d）==\n' "$STATUS" "$PASSES" "$FAILS" "$WARNS"
fi

# ---- --apply：只备份与出计划，不执行 ----
if [ "$APPLY" = 1 ]; then
  if [ "$FAILS" -eq 0 ]; then
    [ "$JSON" = 1 ] || echo "无需修复：全部硬断言已通过。"
    exit 0
  fi

  [ "$JSON" = 1 ] || cat <<EOF

== 修复计划（未执行，需人类批准）==

第一步 备份配置（脚本已代为执行，仅备份已存在的文件）
EOF
  for f in "$HOME/.config/containers/storage.conf" /etc/containers/storage.conf; do
    if [ -f "$f" ]; then
      bak="$f.bak-$(date +%Y%m%d%H%M%S)"
      cp -p "$f" "$bak" && { [ "$JSON" = 1 ] || echo "  已备份 $f -> $bak"; }
    fi
  done

  [ "$JSON" = 1 ] || cat <<EOF

第二步 按情形分流（二者互斥）

  情形 A 有本地大容量盘：
    把 graphRoot 与 volumePath 指向同一挂载点内的实路径。
    rootless 下 storage.conf 的 graphroot 不生效（A1 实测），可用手段只有：
      podman --root <实路径> ...          # 每次调用带全局参数
    或在 shell 别名 / 封装脚本中固定 --root。迁移后执行：
      podman system migrate
      podman info --format '{{.Store.GraphRoot}} {{.Store.GraphDriverName}}'

  情形 B 只有网络盘：
    不得使用 overlay。改 driver = "vfs"（体积约为 overlay 的 2-3 倍、启动变慢），
    并在交付文档同步下调交付等级（A4）。此属主报告 F1 的「推翻条件」。

第三步 迁移前置检查
    现状数据量以 p2-du-census.sh 的 userns 口径为准；迁移期间 Podman 停机。
    回滚：还原上面备份的 storage.conf 后再执行一次 podman system migrate。

窗口侧（若 vhdx 落在网络盘）：须经人类批准后导出-注销-重导入到本地固定盘：
  wsl --export openkylin-test D:\\WSL\\backup\\openkylin-test-YYYYMMDD.tar
  wsl --unregister openkylin-test
  wsl --import openkylin-test D:\\WSL\\openkylin-test D:\\WSL\\backup\\openkylin-test-YYYYMMDD.tar --version 2
EOF
  exit 78
fi

exit "$RC"