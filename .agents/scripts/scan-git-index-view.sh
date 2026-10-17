#!/usr/bin/env bash
# 只读诊断：采样 git status / ls-files / .git/index，判定工作视图是否振荡
#
# 背景：并行会话共享工作区时，同一路径的 `git status --porcelain` 与 `git ls-files`
#       可能给出不一致视图，且 .git/index 的 mtime 在无本方操作时被第三方改写。
#       本工具用于复现与取证该现象（配套规则：.agents/rules/commit-staging-integrity.md）。
#
# ⚠️ 纯只读：不写入工作区、不修改索引、不创建任何文件。

set -u

usage() {
  cat <<'EOF'
用法: bash .agents/scripts/scan-git-index-view.sh [PATH] [-n 采样次数] [-i 间隔秒]
  PATH  采样目标目录（相对仓库根或绝对路径），缺省为仓库根
  -n    采样次数，默认 12
  -i    采样间隔秒，默认 0.5
  -h    显示本帮助
退出码: 0=采样期内视图稳定  1=观察到视图振荡  2=参数或环境错误
本工具纯只读，不写入工作区、不修改索引、不创建文件。
EOF
  exit 2
}

target=''; samples=12; interval=0.5
while [ $# -gt 0 ]; do
  case "$1" in
    -n) samples=${2:-}; shift 2 ;;
    -i) interval=${2:-}; shift 2 ;;
    -h|--help) usage ;;
    -*) echo "未知参数: $1" >&2; usage ;;
    *) target=$1; shift ;;
  esac
done
case "$samples" in ''|*[!0-9]*) echo "非法 -n: $samples" >&2; exit 2 ;; esac
case "$interval" in ''|*[!0-9.]*) echo "非法 -i: $interval" >&2; exit 2 ;; esac

root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "错误：不在 git 仓库内" >&2; exit 2; }
case "$target" in
  '')  target="$root" ;;
  /*)  : ;;
  *)   target="$root/$target" ;;
esac
[ -d "$target" ] || { echo "错误：路径不存在: $target" >&2; exit 2; }
rel=${target#"$root"/}; [ -n "$rel" ] || rel='.'

echo "仓库根: $root"
echo "采样目标: $rel   采样次数: $samples   采样间隔: ${interval}s"
echo

prev=''; seen=''; osc=0; i=0
while [ "$i" -lt "$samples" ]; do
  i=$((i + 1))
  ts=$(date +%H:%M:%S.%N | cut -c1-12)
  s=$(git -C "$root" status --porcelain=v1 -- "$rel/" | tr '\n' ';')
  n=$(git -C "$root" ls-files -- "$rel/" | wc -l | tr -d ' ')
  im=$(stat -c %Y "$root/.git/index" 2>/dev/null || echo '?')
  cur="lsfiles=$n status=[$s]"
  echo "$ts idx_mtime=$im $cur"
  case "$seen" in *"|$cur|"*) : ;; *) seen="$seen|$cur|" ;; esac
  [ -n "$prev" ] && [ "$cur" != "$prev" ] && osc=1
  prev=$cur
  [ "$i" -lt "$samples" ] && sleep "$interval"
done

echo
echo "=== 视图集合（去重）==="
echo "$seen" | tr '|' '\n' | sed '/^$/d'
echo
echo "=== 相关 git 进程 ==="
ps -eo pid,etime,args 2>/dev/null | grep -E '[g]it' | grep -v -E '[g]rep|scan-git-index-view' | head -10
echo
if [ "$osc" -eq 1 ]; then
  echo "结果：观察到视图振荡（${samples} 次采样中出现不一致视图）"
  exit 1
fi
echo "结果：采样期内视图稳定"
exit 0
