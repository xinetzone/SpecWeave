#!/bin/bash

if [ -t 1 ]; then
    C_RESET=$'\033[0m'
    C_RED=$'\033[31m'
    C_GREEN=$'\033[32m'
    C_YELLOW=$'\033[33m'
    C_BLUE=$'\033[34m'
else
    C_RESET=""
    C_RED=""
    C_GREEN=""
    C_YELLOW=""
    C_BLUE=""
fi

_log_ts() {
    date '+%Y-%m-%d %H:%M:%S'
}

log_info() {
    echo -e "${C_BLUE}[$(_log_ts)] [INFO]${C_RESET} $*"
}

log_ok() {
    echo -e "${C_GREEN}[$(_log_ts)] [OK]${C_RESET} $*"
}

log_warn() {
    echo -e "${C_YELLOW}[$(_log_ts)] [WARN]${C_RESET} $*"
}

log_error() {
    echo -e "${C_RED}[$(_log_ts)] [ERROR]${C_RESET} $*" >&2
}
