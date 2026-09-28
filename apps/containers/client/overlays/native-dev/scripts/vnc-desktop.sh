#!/bin/bash
# ==============================================================================
# vnc-desktop.sh — 宿主用户态「虚拟显示 + 浏览器 VNC」配套（无 sudo、无守护进程）
#
# 适用场景：SSH 远程开发机（无本地桌面、无 ssh -X 条件，如办公机无 X server），
# 但需要看容器里的 GUI 窗口（tkinter/Qt/matplotlib 等）。在宿主起一块内存虚拟
# 显示 Xvfb，x11vnc 把它转成 VNC，websockify/noVNC 再转成浏览器页面；native-dev
# 容器以现有 X11 unix 透传形态（up --gui + GUI_DISPLAY=:<n>）把窗口画进同一块
# Xvfb——本脚本不碰容器编排，只提供「显示终点」。
#
#   办公机浏览器 ──ssh -L 隧道──> 127.0.0.1:6080(noVNC/websockify)
#                                       │ 127.0.0.1:5900
#                                       ▼
#                                    x11vnc ──> Xvfb :99（/tmp/.X11-unix/X99）
#                                       ▲ bind mount（compose.passthrough.gui.x11）
#                                     容器 GUI 进程（DISPLAY=:99）
#
# 前置（一次性，需管理员）：
#   sudo apt-get update && sudo apt-get install -y x11vnc novnc websockify openbox
#   （Xvfb 本机已预装；openbox 可选——提供窗口标题栏/拖动，缺失时单窗口仍可用）
#
# 用法：
#   scripts/vnc-desktop.sh start     # 幂等启动（已运行的进程复用）
#   scripts/vnc-desktop.sh status    # 进程/端口/密码/办公机侧访问命令
#   scripts/vnc-desktop.sh stop      # 停止（只杀本脚本记录的 PID）
#
# 安全边界（勿放宽）：
#   ① x11vnc 与 websockify 只绑 127.0.0.1——办公网其他主机不可直达，必须经
#      SSH 本地转发（-L）进入，复用 SSH 凭据，VNC 端口零暴露；
#   ② VNC 密码首次启动随机生成，存状态目录、0600，status 才显示，不入脚本；
#   ③ Xvfb 用 -ac（关闭 X 授权）：unix socket 经 bind 给 rootless 容器、容器内
#      无 xauth/cookie，故只能免授权；socket 目录权限与「本机单用户开发机」为
#      风险前提，多用户共享主机不应使用本方案；
#   ④ 屏幕内容（含可能的涉密画面）可被能 SSH 登录本机者经隧道看到，用完即 stop。
# ==============================================================================
set -euo pipefail

VNC_DISPLAY="${VNC_DISPLAY:-99}"                 # X 显示号 :99 → 容器 GUI_DISPLAY=:99
VNC_RESOLUTION="${VNC_RESOLUTION:-1920x1080x24}"
VNC_RFB_PORT="${VNC_RFB_PORT:-5900}"             # x11vnc
VNC_WEB_PORT="${VNC_WEB_PORT:-6080}"             # noVNC/websockify
VNC_SOCKET_DIR="${VNC_SOCKET_DIR:-/tmp/.X11-unix}"

STATE_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/native-vnc"
XVFB_PID="$STATE_DIR/$(id -un)-xvfb-${VNC_DISPLAY}.pid"
WM_PID="$STATE_DIR/openbox.pid"
X11VNC_PID="$STATE_DIR/x11vnc.pid"
WS_PID="$STATE_DIR/websockify.pid"
VNC_AUTH="$STATE_DIR/passwd"
VNC_PASS_TXT="$STATE_DIR/passwd.txt"

log() { printf '[vnc-desktop] %s\n' "$*"; }
die() { printf '[vnc-desktop] ERROR: %s\n' "$*" >&2; exit 1; }

require_bin() {
    command -v "$1" >/dev/null 2>&1 || die "缺少 $1——请执行：sudo apt-get install -y $2"
}

alive() { local pidfile=$1; [[ -s $pidfile ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; }

cmd_start() {
    require_bin Xvfb xvfb
    require_bin x11vnc x11vnc
    require_bin websockify novnc
    [[ -d /usr/share/novnc ]] || die "缺少 /usr/share/novnc（由 novnc 包提供）"
    mkdir -p "$STATE_DIR" "$VNC_SOCKET_DIR"
    chmod 700 "$STATE_DIR"

    # ① Xvfb 虚拟显示（幂等：socket 已在则复用；PID 与现状不符则报错不抢显示号）
    if [[ -S "$VNC_SOCKET_DIR/X$VNC_DISPLAY" ]] || alive "$XVFB_PID"; then
        log "Xvfb :$VNC_DISPLAY 已在运行，复用"
    else
        /usr/bin/Xvfb ":$VNC_DISPLAY" -ac -nolisten tcp -screen 0 "$VNC_RESOLUTION" \
            >>"$STATE_DIR/xvfb.log" 2>&1 &
        echo $! >"$XVFB_PID"
        for _ in $(seq 1 50); do
            [[ -S "$VNC_SOCKET_DIR/X$VNC_DISPLAY" ]] && break
            sleep 0.1
        done
        [[ -S "$VNC_SOCKET_DIR/X$VNC_DISPLAY" ]] \
            || die "Xvfb :$VNC_DISPLAY 启动失败（见 $STATE_DIR/xvfb.log）"
        log "Xvfb :$VNC_DISPLAY 已启动（$VNC_RESOLUTION）"
    fi

    # ② 窗口管理器（可选；openbox 缺失不阻断）
    if command -v openbox >/dev/null 2>&1 && ! alive "$WM_PID"; then
        DISPLAY=":$VNC_DISPLAY" openbox --sm-disable >>"$STATE_DIR/openbox.log" 2>&1 &
        echo $! >"$WM_PID"
        log "openbox 窗口管理器已启动"
    fi

    # ③ 随机 VNC 密码（8 字符，VNC 协议上限；0600）
    if [[ ! -s $VNC_AUTH ]]; then
        local_pw="$(tr -dc 'A-HJ-NP-Za-km-z2-9' </dev/urandom | head -c 8)"
        x11vnc -storepasswd "$local_pw" "$VNC_AUTH" >>"$STATE_DIR/x11vnc.log" 2>&1
        printf '%s\n' "$local_pw" >"$VNC_PASS_TXT"
        chmod 600 "$VNC_AUTH" "$VNC_PASS_TXT"
        log "已生成随机 VNC 密码（仅本次及 status 可见）"
    fi

    # ④ x11vnc：仅 loopback、循环接受、允许重连共享
    if alive "$X11VNC_PID"; then
        log "x11vnc 已在运行，复用"
    else
        x11vnc -display ":$VNC_DISPLAY" -localhost -rfbport "$VNC_RFB_PORT" \
            -rfbauth "$VNC_AUTH" -forever -shared -bg \
            -o "$STATE_DIR/x11vnc.log" >/dev/null
        pgrep -f "x11vnc .*:$VNC_DISPLAY" | head -1 >"$X11VNC_PID"
        sleep 1
        alive "$X11VNC_PID" || die "x11vnc 启动失败（见 $STATE_DIR/x11vnc.log）"
        log "x11vnc 已启动（127.0.0.1:$VNC_RFB_PORT，仅 loopback）"
    fi

    # ⑤ websockify + noVNC 静态资源
    if alive "$WS_PID"; then
        log "websockify 已在运行，复用"
    else
        websockify --web=/usr/share/novnc "127.0.0.1:$VNC_WEB_PORT" \
            "127.0.0.1:$VNC_RFB_PORT" >>"$STATE_DIR/websockify.log" 2>&1 &
        echo $! >"$WS_PID"
        sleep 1
        alive "$WS_PID" || die "websockify 启动失败（见 $STATE_DIR/websockify.log）"
        log "noVNC 网关已启动（127.0.0.1:$VNC_WEB_PORT）"
    fi

    cmd_status
}

cmd_status() {
    local any=0
    alive "$XVFB_PID"   && { log "Xvfb      : 运行中 PID $(cat "$XVFB_PID")   显示 :$VNC_DISPLAY"; any=1; } || log "Xvfb      : 未运行"
    alive "$X11VNC_PID" && { log "x11vnc    : 运行中 PID $(cat "$X11VNC_PID") 127.0.0.1:$VNC_RFB_PORT"; any=1; } || log "x11vnc    : 未运行"
    alive "$WS_PID"     && { log "noVNC     : 运行中 PID $(cat "$WS_PID") 127.0.0.1:$VNC_WEB_PORT"; any=1; } || log "noVNC     : 未运行"
    [[ $any -eq 0 ]] && return 0
    [[ -s $VNC_PASS_TXT ]] && log "VNC 密码  : $(cat "$VNC_PASS_TXT")"
    local host; host="$(hostname -I 2>/dev/null | awk '{print $1}')"
    cat <<EOF

  ① 办公机开 SSH 本地转发（保持窗口不关；Windows 10+ 自带 ssh，PowerShell 执行）：
       ssh -L ${VNC_WEB_PORT}:localhost:${VNC_WEB_PORT} ai@${host}
  ② 办公机浏览器打开：
       http://localhost:${VNC_WEB_PORT}/vnc.html
     点 Connect，输入上面的 VNC 密码。
  ③ 容器接入这块虚拟显示（X11 unix 透传，现有形态，无需 host 网络）：
       GUI_DISPLAY=:${VNC_DISPLAY} invoke native.up --gui
     （重建叠加；--passthrough/--gpu/--usb/--offline 可照常组合）
EOF
}

cmd_stop() {
    for pidfile in "$WS_PID" "$X11VNC_PID" "$WM_PID" "$XVFB_PID"; do
        if alive "$pidfile"; then
            kill "$(cat "$pidfile")" 2>/dev/null || true
            log "已停止 $(basename "$pidfile" .pid)（PID $(cat "$pidfile")）"
        fi
        rm -f "$pidfile"
    done
    log "虚拟桌面已停止（状态目录保留：$STATE_DIR）"
}

case "${1:-}" in
    start)  cmd_start ;;
    status) cmd_status ;;
    stop)   cmd_stop ;;
    *) echo "用法: $0 {start|status|stop}" >&2; exit 2 ;;
esac
