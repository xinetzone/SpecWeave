#!/usr/bin/env bash
# triage.sh — Remote-SSH 远端 IDE server 安装卡死：只读取证采集
#
# 用法：
#   bash scripts/triage.sh <host> [--server-root ~/.trae-cn-server|~/.vscode-server]
#                                [--sample-seconds 10] [--dry-run]
#
# 本脚本全程只读：不 kill、不删除、不写远端任何文件。
# --dry-run 与默认行为等价（保留该开关以对齐 SKILL.md 的 <host> [--dry-run] 参数契约），
# 脚本只把建议的 kill 命令打印出来，由使用者确认后手工执行。
#
# 退出码：
#   0  采集完成，未命中已知故障特征
#   2  SSH 通道不可用（应退出本技能，改走 ssh 排障）
#   3  server-main 已在运行（不是下载问题，改看扩展宿主日志）
#   4  判定为僵死下载（三判据同时成立，建议方案A）
#   5  下载仍在推进（只是慢，不要 kill）
#   6  未发现存活下载进程（方案B 或检查安装脚本是否启动）

set -uo pipefail

HOST=""
SERVER_ROOT=""
SAMPLE_SECONDS=10

usage() {
  sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --server-root)   SERVER_ROOT="${2:-}"; shift 2 ;;
    --sample-seconds) SAMPLE_SECONDS="${2:-10}"; shift 2 ;;
    --dry-run)       shift ;;
    -h|--help)       usage; exit 0 ;;
    *)               HOST="$1"; shift ;;
  esac
done

if [ -z "$HOST" ]; then
  echo "ERROR: 缺少 <host> 参数" >&2
  usage >&2
  exit 2
fi

SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=10)
r() { ssh "${SSH_OPTS[@]}" "$HOST" "$1" 2>&1; }

sec() { printf '\n===== %s =====\n' "$1"; }

# ---------- 1. 通道基线 ----------
sec "1. 通道基线"
if ! ssh "${SSH_OPTS[@]}" "$HOST" 'echo ok' >/dev/null 2>&1; then
  echo "FAIL: ssh $HOST 'echo ok' 未返回 ok"
  echo "结论：SSH 通道不可用，退出本技能，改走 ssh 排障（端口/密钥/认证）。"
  exit 2
fi
echo "OK: SSH 通道可用"

if [ -z "$SERVER_ROOT" ]; then
  for cand in '~/.trae-cn-server' '~/.vscode-server'; do
    if r "test -d $cand && echo present" | grep -q present; then
      SERVER_ROOT="$cand"
      break
    fi
  done
fi

if [ -z "$SERVER_ROOT" ]; then
  echo "WARN: 未找到 ~/.trae-cn-server 或 ~/.vscode-server，安装可能尚未开始"
  SERVER_ROOT='~/.trae-cn-server'
else
  echo "server-root = $SERVER_ROOT"
fi

echo "-- df -h ~"
r 'df -h ~ | tail -1'
echo "-- du -sh server-root"
r "du -sh $SERVER_ROOT 2>/dev/null"

# ---------- 2. 进程链与锁 ----------
sec "2. 进程链与锁"
echo "-- 相关进程（pid ppid etime stat wchan args）"
r "ps -eo pid,ppid,etime,stat,wchan:24,args | grep -E 'fetch|curl|server-main' | grep -v grep"
echo "-- resolve-lock 目录"
r "ls -la $SERVER_ROOT/ 2>/dev/null | grep resolve-lock"
echo "-- lock pid"
r "cat $SERVER_ROOT/.resolve-lock-*/pid 2>/dev/null"
echo "-- lock heartbeat mtime"
r "stat -c '%y %n' $SERVER_ROOT/.resolve-lock-*/heartbeat 2>/dev/null"

# ---------- 3. 卡死三判据 ----------
sec "3. 卡死三判据"
SERVER_PID=$(r "ps -eo pid,comm,args | grep -E '^ *[0-9]+ +node( |$)' | grep server-main" | tr -s ' ' | cut -d' ' -f2 | head -n1)
DL_PID=$(r "ps -eo pid,comm,args | grep -E '^ *[0-9]+ +(fetch|curl)( |$)'" | tr -s ' ' | cut -d' ' -f2 | head -n1)

echo "server-main pid = ${SERVER_PID:-<none>}"
echo "download   pid = ${DL_PID:-<none>}"

if [ -n "${SERVER_PID:-}" ]; then
  echo
  echo "结论：server-main 已在运行（pid=$SERVER_PID），这不是下载卡死问题。"
  echo "退出本技能，改看远端扩展宿主日志（$SERVER_ROOT/.stable-*.log 与 out/vsServer 日志）。"
  exit 3
fi

if [ -z "${DL_PID:-}" ]; then
  echo
  echo "结论：未发现存活的 fetch/curl 下载进程。"
  echo "下一步：确认客户端安装脚本是否根本没启动；或直接走方案B（异机下载 + 手工解压）。"
  exit 6
fi

echo "-- ss -tnp（只看该 pid）"
r "ss -tnp 2>/dev/null | grep 'pid=$DL_PID'"
echo "-- wchan"
r "cat /proc/$DL_PID/wchan 2>/dev/null; echo"
echo "-- 落盘 fd"
r "ls -l /proc/$DL_PID/fd 2>/dev/null | grep -E 'tar|tmp|xz'"

echo "-- /proc/$DL_PID/io 两次采样（间隔 ${SAMPLE_SECONDS}s）"
IO1=$(r "cat /proc/$DL_PID/io 2>/dev/null")
sleep "$SAMPLE_SECONDS"
IO2=$(r "cat /proc/$DL_PID/io 2>/dev/null")

R1=$(printf '%s\n' "$IO1" | awk '/^rchar:/{print $2}')
R2=$(printf '%s\n' "$IO2" | awk '/^rchar:/{print $2}')

if [ -z "${R1:-}" ] || [ -z "${R2:-}" ]; then
  echo "WARN: 无法读取 /proc/$DL_PID/io（权限或进程已退出）"
  DELTA="unknown"
else
  DELTA=$(( R2 - R1 ))
  echo "rchar: $R1 -> $R2  (delta=$DELTA bytes in ${SAMPLE_SECONDS}s)"
fi

# ---------- 4. 落盘目标 ----------
sec "4. 落盘目标是否为空"
r "ls -la $SERVER_ROOT/bin/ 2>/dev/null"
r "ls -la $SERVER_ROOT/bin/stable-*-debian10/ 2>/dev/null | head"

# ---------- 5. CDN 多节点 ----------
sec "5. CDN 多节点探测"
echo "-- A 记录（IPv4）"
r "getent ahostsv4 lf-cdn.trae.com.cn | awk '{print \$1}' | sort -u"
echo "-- HEAD 探测"
r "curl -sS -I -m 8 -o /dev/null -w '%{http_code} ip=%{remote_ip} t=%{time_total}\n' https://lf-cdn.trae.com.cn/"

# ---------- 6. 判定 ----------
sec "6. 判定与建议"
if [ "${DELTA:-unknown}" = "unknown" ]; then
  echo "结论：字节增量无法采样，证据不足，不得执行 kill。"
  echo "建议：延长采样窗口重跑（--sample-seconds 30），或人工核对 /proc/$DL_PID/io。"
  exit 0
fi

if [ "$DELTA" -lt 4096 ]; then
  echo "结论：三判据命中（连接已建立 + 字节停滞 ${DELTA}B/${SAMPLE_SECONDS}s + 进程存活）。"
  echo "建议（方案A，单条写操作，需人工确认后执行）："
  echo
  echo "    ssh $HOST 'kill -TERM $DL_PID'"
  echo
  echo "执行后不要重启 IDE，等安装脚本自行重试；随后用 §10 四项对账验收。"
  exit 4
else
  echo "结论：字节仍在增长（${DELTA}B/${SAMPLE_SECONDS}s），只是慢，不要 kill。"
  echo "建议：继续等待，同时确认 df -h ~ 剩余空间大于 2GB。"
  exit 5
fi