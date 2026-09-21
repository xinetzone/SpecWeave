# ==============================================================================
# log.sh — relpack 日志片段（由 bin/relpack source；非 TTY 自动降级无色）
#
# 前缀惯例与客户交付骨架 xmnnctl 一致：[ OK ] 成功 / [WARN] 提醒 / [ERR ] 失败。
# 所有消息写 stdout，仅 die/err 写 stderr（便于管道分拣）。
# ==============================================================================

if [ -t 1 ]; then
    _C_OK=$'\033[1;32m'; _C_WARN=$'\033[1;33m'
    _C_ERR=$'\033[1;31m'; _C_INFO=$'\033[1;34m'; _C_END=$'\033[0m'
else
    _C_OK=''; _C_WARN=''; _C_ERR=''; _C_INFO=''; _C_END=''
fi

ok()   { printf '%s[ OK ]%s %s\n' "$_C_OK" "$_C_END" "$*"; }
warn() { printf '%s[WARN]%s %s\n' "$_C_WARN" "$_C_END" "$*"; }
err()  { printf '%s[ERR ]%s %s\n' "$_C_ERR" "$_C_END" "$*" >&2; }
info() { printf '%s[info]%s %s\n' "$_C_INFO" "$_C_END" "$*"; }
die()  { err "$*"; exit 1; }