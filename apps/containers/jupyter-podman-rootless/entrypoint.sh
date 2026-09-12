#!/bin/bash
set -euo pipefail

if [ "${DEBUG:-0}" = "1" ]; then
    set -x
fi

if [ -n "${ENABLE_SUDO_NOPASSWD:-}" ] && [ "${GRANT_SUDO:-no}" = "no" ]; then
    if [ "${ENABLE_SUDO_NOPASSWD}" = "1" ] || [ "${ENABLE_SUDO_NOPASSWD}" = "yes" ] || [ "${ENABLE_SUDO_NOPASSWD}" = "true" ]; then
        export GRANT_SUDO=yes
    fi
fi

if [ -n "${JUPYTER_CORS_ORIGIN:-}" ] && [ -z "${JUPYTER_ALLOW_ORIGIN:-}" ]; then
    export JUPYTER_ALLOW_ORIGIN="${JUPYTER_CORS_ORIGIN}"
fi

CONDA_DIR="/opt/conda"
CONDA_ENV="main"
CONDA_ENV_PATH="${CONDA_DIR}/envs/${CONDA_ENV}"
CONDA_PYTHON="${CONDA_ENV_PATH}/bin/python"
CONDA_JUPYTER="${CONDA_ENV_PATH}/bin/jupyter"
NON_ROOT_USER="${NON_ROOT_USER:-devuser}"
NON_ROOT_HOME="/home/${NON_ROOT_USER}"
BUILD_INFO_FILE="/etc/jupyter-podman-build-info"
SUPERVISORD_CONF="/etc/supervisor/supervisord.conf"

log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }

run_as_user() {
    if command -v gosu >/dev/null 2>&1; then
        exec gosu "${NON_ROOT_USER}" "$@"
    else
        exec su - "${NON_ROOT_USER}" -c "exec \"\$@\"" -- "$@"
    fi
}

print_banner() {
    echo ""
    echo "============================================================"
    echo "  Jupyter Podman Rootless Container starting..."
    echo "  Time: $(date)"
    echo "  Host: $(hostname)"
    echo "============================================================"
    echo ""
}

diagnose_system() {
    log_info "========== System Diagnostics =========="
    log_info "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
    log_info "Kernel: $(uname -r)"
    log_info "Arch: $(uname -m)"
    log_info "Timezone: ${TZ:-not set} (now: $(date))"
    log_info "Locale: ${LANG:-not set}"
    log_info "User: $(id)"
    log_info "Non-root user: ${NON_ROOT_USER}"

    log_info "Python version: $("${CONDA_PYTHON}" --version 2>&1)"
    if "${CONDA_PYTHON}" -c "import sys, sysconfig; sys.exit(0 if sysconfig.get_config_var('Py_GIL_DISABLED') == 1 and not sys._is_gil_enabled() else 1)" 2>/dev/null; then
        log_info "Python build: cp314t (free-threading) confirmed"
    else
        log_warn "Python is NOT free-threading build"
    fi
    log_info "Conda version: $("${CONDA_DIR}/bin/conda" --version 2>&1)"
    if command -v podman >/dev/null 2>&1; then
        log_info "Podman version: $(podman --version 2>&1 | awk '{print $3}')"
    else
        log_warn "Podman not found in PATH"
    fi

    if [ -f "${BUILD_INFO_FILE}" ]; then
        log_info "Build info:"
        while IFS= read -r line; do log_info "  $line"; done < "${BUILD_INFO_FILE}"
    fi
    log_info "========================================"
    echo ""
}

setup_passwords() {
    log_info "[Step 1/7] Configuring user passwords..."
    local generated_password=0

    if [ -n "${ROOT_PASSWORD:-}" ] && [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        echo "root:${ROOT_PASSWORD}" | chpasswd
        log_info "Root password set from ROOT_PASSWORD env var"
    elif [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        ROOT_PASSWORD=$(pwgen -s 16 1)
        echo "root:${ROOT_PASSWORD}" | chpasswd
        log_warn "ROOT_PASSWORD not set, generated random password for root"
        generated_password=1
    fi

    if [ -n "${USER_PASSWORD:-}" ]; then
        echo "${NON_ROOT_USER}:${USER_PASSWORD}" | chpasswd
        log_info "${NON_ROOT_USER} password set from USER_PASSWORD env var"
    else
        USER_PASSWORD=$(pwgen -s 16 1)
        echo "${NON_ROOT_USER}:${USER_PASSWORD}" | chpasswd
        log_warn "USER_PASSWORD not set, generated random password for ${NON_ROOT_USER}"
        generated_password=1
    fi

    if [ "${GRANT_SUDO:-no}" = "yes" ]; then
        echo "${NON_ROOT_USER} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${NON_ROOT_USER}"
        chmod 0440 "/etc/sudoers.d/${NON_ROOT_USER}"
        log_info "Sudo NOPASSWD enabled for ${NON_ROOT_USER}"
    fi

    if [ "$generated_password" = "1" ]; then
        echo ""
        echo "    ************************************************"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            echo "    * [IMPORTANT] Root password:      ${ROOT_PASSWORD}"
        fi
        echo "    * [IMPORTANT] ${NON_ROOT_USER} password: ${USER_PASSWORD}"
        echo "    * SSH login: ssh ${NON_ROOT_USER}@<host> -p ${SSHD_PORT:-22}"
        echo "    ************************************************"
        echo ""
    fi
}

generate_host_keys() {
    log_info "[Step 2/7] Generating SSH host keys..."
    rm -f /etc/ssh/ssh_host_*_key /etc/ssh/ssh_host_*_key.pub 2>/dev/null || true
    ssh-keygen -A
    log_info "SSH host keys generated:"
    ls -la /etc/ssh/ssh_host_*_key.pub 2>/dev/null | while IFS= read -r line; do log_info "  $line"; done || true
    if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
        log_warn "ED25519 key not found, generating explicitly..."
        ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N "" -q
    fi
}

configure_sshd() {
    log_info "[Step 3/7] Configuring SSH daemon..."
    mkdir -p /run/sshd && chmod 755 /run/sshd
    # SSHD_PORT：覆盖 sshd 监听端口。host 网络模式下必需——rootless Podman 中容器 root
    # 映射为宿主非特权 UID，无法绑定特权端口 22（<1024），此时须改用 >=1024 的端口。
    local sshd_port="${SSHD_PORT:-22}"
    case "${sshd_port}" in
        '' | *[!0-9]*)
            log_error "Invalid SSHD_PORT: '${sshd_port}' (expect an integer in 1-65535)"
            exit 1
            ;;
    esac
    if [ "${sshd_port}" -lt 1 ] || [ "${sshd_port}" -gt 65535 ]; then
        log_error "Invalid SSHD_PORT: ${sshd_port} (expect an integer in 1-65535)"
        exit 1
    fi
    sed -i "s/^#*Port .*/Port ${sshd_port}/" /etc/ssh/sshd_config
    log_info "SSH daemon listening port: ${sshd_port}"
    if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        sed -i "s/^#*PermitRootLogin.*/PermitRootLogin yes/" /etc/ssh/sshd_config
        log_info "Root SSH login enabled (ALLOW_ROOT_SSH=yes)"
    else
        sed -i "s/^#*PermitRootLogin.*/PermitRootLogin no/" /etc/ssh/sshd_config
        log_info "Root SSH login disabled (ALLOW_ROOT_SSH=no)"
    fi
    log_info "Validating sshd_config..."
    if /usr/sbin/sshd -t; then
        log_info "[OK] sshd_config syntax valid"
    else
        log_error "sshd_config syntax error! Details:"
        /usr/sbin/sshd -T 2>&1 | head -20 | while IFS= read -r line; do log_error "  $line"; done
        exit 1
    fi
}

setup_podman() {
    log_info "[Step 4/7] Setting up Podman rootless environment..."

    if [ -c /dev/fuse ]; then
        chmod 666 /dev/fuse 2>/dev/null || true
        log_info "/dev/fuse device permissions set"
    else
        log_warn "/dev/fuse not found - FUSE may not be available; make sure to run container with --device /dev/fuse"
    fi

    local containers_config_dir="${NON_ROOT_HOME}/.config/containers"
    mkdir -p "${containers_config_dir}"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${containers_config_dir}" 2>/dev/null || true
    chmod 700 "${containers_config_dir}" 2>/dev/null || true
    log_info "User containers config dir ready: ${containers_config_dir}"

    local podman_storage_dir="${NON_ROOT_HOME}/.local/share/containers"
    mkdir -p "${podman_storage_dir}"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${NON_ROOT_HOME}/.local" 2>/dev/null || true
    log_info "Podman storage dir ready: ${podman_storage_dir}"

    local podman_run_dir="/run/user/$(id -u ${NON_ROOT_USER})"
    mkdir -p "${podman_run_dir}"
    # ⚠ 禁止对 ${podman_run_dir} 整体 chown -R：B-scheme 下宿主 podman.sock 以
    # 单文件 bind-mount 挂在 ${podman_run_dir}/podman/podman.sock，递归 chown 会穿透
    # 挂载点改写宿主 socket inode 属主（2026-09-11 事故：被改成 subuid 映射值
    # 525287:525287，宿主 sshd 转发连接即被拒，Windows podman CLI 全断）。
    # 只处理目录本身；子树（libpod）在下方按白名单显式 chown -R。
    chown "${NON_ROOT_USER}:${NON_ROOT_USER}" "${podman_run_dir}" 2>/dev/null || true
    chmod 700 "${podman_run_dir}" 2>/dev/null || true
    log_info "Podman run dir ready: ${podman_run_dir}"

    # rootless podman 需把管理进程 pause.pid 写入 ${XDG_RUNTIME_DIR}/libpod/tmp，
    # 目录缺失会触发 `open .../libpod/tmp/pause.pid: no such file or directory`
    # 与 `error creating temporary file: Permission denied`（见 README §5.4 C-I1 扩展）。
    # 属主必须与运行时用户一致（devuser 固定 UID 1000，但仍以用户名派生路径/属主，
    # 不在脚本中写死数值——路径统一由 id -u ${NON_ROOT_USER} 计算）。
    local podman_libpod="${podman_run_dir}/libpod"
    local podman_libpod_tmp="${podman_libpod}/tmp"
    mkdir -p "${podman_libpod_tmp}"
    # libpod 父目录同样必须属于运行时用户；否则 rootless podman 对 /run/user/<uid>/libpod
    # 设置 sticky bit 时会被拒绝（`set sticky bit on: chmod .../libpod: operation not permitted`）。
    # 必须先 chown 父目录再 chmod，避免镜像层或挂载导致目录残留非 devuser 属主。
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${podman_libpod}" 2>/dev/null || true
    chmod 700 "${podman_libpod}" 2>/dev/null || true
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${podman_libpod_tmp}" 2>/dev/null || true
    chmod 700 "${podman_libpod_tmp}" 2>/dev/null || true
    log_info "Podman libpod tmp dir ready: ${podman_libpod_tmp}"

    # ── 独立 shell 的注入式 XDG_RUNTIME_DIR 属主修复 ──
    # SSH / podman exec / Jupyter 终端等独立 shell 不继承下方导出的
    # XDG_RUNTIME_DIR=${podman_run_dir}，保留容器配置注入值（GUI 透传时为
    # /tmp/runtime-user）。该挂载点父目录由 podman 自动创建为 root:0755，
    # devuser 在其中 `mkdir libpod` 会被拒（实测：
    # "Failed to obtain podman configuration: mkdir /tmp/runtime-user/libpod:
    # permission denied"）。这里只 chown 目录本身：
    # 严禁 -R——内部含 wayland-0 单文件 bind-mount，与上文 podman.sock 穿透
    # 改宿主 inode 属主是同一条红线（2026-09-11 事故）。
    local inherited_xdg="${XDG_RUNTIME_DIR:-}"
    if [ -n "${inherited_xdg}" ] \
        && [ "${inherited_xdg}" != "${podman_run_dir}" ] \
        && [ -d "${inherited_xdg}" ]; then
        chown "${NON_ROOT_USER}:${NON_ROOT_USER}" "${inherited_xdg}" 2>/dev/null || true
        log_info "Inherited XDG_RUNTIME_DIR ownership aligned: ${inherited_xdg} -> ${NON_ROOT_USER}"
    fi

    export XDG_RUNTIME_DIR="${podman_run_dir}"

    # ── B-scheme: 宿主 rootless daemon socket 直连（绕过嵌套 userns）──
    # 若启动时已注入 HOST_PODMAN_SOCK（宿主 socket 已在同一绝对路径 bind-mount 进
    # 容器），则在 devuser 可控目录内为其建立符号链接，并显式设置 CONTAINER_HOST，
    # 使容器内 podman SDK/CLI 直接复用宿主 daemon。此后绝不再尝试容器内自建 daemon
    # （自建 daemon 在 WSL 三层 userns 嵌套下会触发 newuidmap Operation not permitted）。
    local host_sock="${HOST_PODMAN_SOCK:-}"
    if [ -n "${host_sock}" ] && [ -S "${host_sock}" ]; then
        # ── 独立 shell 事实文件（SSH 会话不继承容器 config env）──
        # sshd+PAM 派生的 SSH 会话拿不到 HOST_PODMAN_SOCK；镜像内桥接脚本
        # /etc/profile.d/80-podman-host-socket.sh 的第 3 级解析读此文件定位挂载路径，
        # 覆盖非标准挂载（宿主 UID≠1000 时容器内挂载点不是 /run/user/1000/...）。
        echo "${host_sock}" > /etc/podman-host-sock.path
        chmod 644 /etc/podman-host-sock.path 2>/dev/null || true

        # ── sshd SetEnv：覆盖 `ssh host "cmd"` 最外层非交互 bash ──
        # 该形态 bash -c 既不读 profile.d/.bashrc，也不读 BASH_ENV（实测 bash 仅在
        # 执行脚本文件时读 BASH_ENV，-c 命令字符串不读）。SetEnv 是唯一不经任何
        # shell 启动文件的注入点：sshd 直接把变量放进会话进程环境，podman/
        # podman-compose 子进程原样继承。运行时按解析路径写入（非标准挂载同样覆盖），
        # 回退分支无 socket 时不写，避免指向死路径。
        if ! grep -q '^SetEnv CONTAINER_HOST=' /etc/ssh/sshd_config 2>/dev/null; then
            echo "SetEnv CONTAINER_HOST=unix://${host_sock}" >> /etc/ssh/sshd_config
            if /usr/sbin/sshd -t 2>/dev/null; then
                log_info "[B-scheme] sshd SetEnv CONTAINER_HOST written (ssh cmd-form coverage)"
            else
                sed -i '/^SetEnv CONTAINER_HOST=/d' /etc/ssh/sshd_config
                log_warn "[B-scheme] sshd_config invalid after SetEnv, reverted"
            fi
        fi

        # ── devuser 路径（默认 XDG_RUNTIME_DIR）──
        local run_sock_dir="${podman_run_dir}/podman"
        mkdir -p "${run_sock_dir}"
        # ⚠ 禁止 chown -R：该目录内含【单文件 bind-mount 的宿主 socket】（podman.sock），
        # chown -R 会跟随挂载点穿透改宿主 inode 属主——2026-09-11 事故实证：宿主 socket
        # 被改成 subuid 映射值 525287:525287，sshd 转发以 user(1000) 连接即被拒
        # （"ssh: rejected: connect failed (open failed)"，Windows podman CLI 全断）。
        # 只 chown/chmod 目录本身（700 目录 + 挂载 socket 保持宿主 user:user 0660）。
        chown "${NON_ROOT_USER}:${NON_ROOT_USER}" "${run_sock_dir}" 2>/dev/null || true
        chmod 700 "${run_sock_dir}" 2>/dev/null || true
        # devuser 固定 UID 1000 后，宿主 socket 默认就挂载在 /run/user/1000/podman/，
        # 与运行时路径完全相同——GNU ln 对 source==target 即使 -f 也报
        # "are the same file" 并以非 0 退出（set -e 下会中止启动）。同一性幂等跳过。
        local run_sock="${run_sock_dir}/podman.sock"
        if [ "${run_sock}" = "${host_sock}" ] \
            || [ "$(readlink -f "${run_sock}" 2>/dev/null || true)" = "$(readlink -f "${host_sock}" 2>/dev/null || true)" ]; then
            log_info "[B-scheme] socket already at runtime path (UID-aligned mount), skip symlink: ${run_sock}"
        else
            ln -sf "${host_sock}" "${run_sock}"
        fi

        # ── root 路径（容错）──
        # root 用户下 XDG_RUNTIME_DIR 通常为 /run/user/0（不存在）或空，
        # podman-py SDK 会回落到 /tmp/podmanpy-runtime-dir-fallback-root/...。
        # 为避免 Notebook 以 root 身份启动时 from_env() 找不到 socket，
        # 在这里也建立一份根可写的链接（同宿 socket，不影响权限）。
        local root_sock_dir="/tmp/podman-runtime-dir"
        mkdir -p "${root_sock_dir}/podman"
        chmod 777 "${root_sock_dir}" 2>/dev/null || true
        chmod 777 "${root_sock_dir}/podman" 2>/dev/null || true
        ln -sf "${host_sock}" "${root_sock_dir}/podman/podman.sock"

        # ── SDK fallback 路径（容错）──
        # podman-py SDK 在 root 用户 + XDG_RUNTIME_DIR 为空时，自动回落到：
        # /tmp/podmanpy-runtime-dir-fallback-root/podman/podman.sock
        # 在此也建立符号链接，确保 from_env() 无论走哪条路径都能命中宿主 socket。
        local sdk_fallback_dir="/tmp/podmanpy-runtime-dir-fallback-root/podman"
        mkdir -p "${sdk_fallback_dir}"
        chmod 700 "${sdk_fallback_dir}" 2>/dev/null || true
        ln -sf "${host_sock}" "${sdk_fallback_dir}/podman.sock"

        # 显式覆盖两个关键 env：无论谁调用 from_env() 都命中宿主 socket
        export CONTAINER_HOST="unix://${run_sock_dir}/podman.sock"
        export XDG_RUNTIME_DIR="${podman_run_dir}"
        log_info "[B-scheme] Host podman socket linked: ${run_sock_dir}/podman.sock -> ${host_sock}"
        log_info "[B-scheme] root fallback socket: ${root_sock_dir}/podman/podman.sock -> ${host_sock}"
        log_info "[B-scheme] CONTAINER_HOST=${CONTAINER_HOST} (XDG_RUNTIME_DIR=${podman_run_dir})"

        # ── socket 属组衔接（EACCES 修复 · 见 client/README.md §5.4 C-I2）──
        # 宿主 socket（宿主 <uid>:<gid> 0660）经 bind-mount 进入 rootless 容器 userns 后，
        # 数值属主/属组被映射为容器 0，故容器内呈现为 root:root 0660。devuser 固定 UID 1000
        #（≠0）且镜像基线未把它加入 root 组 → connect() 抛 EACCES(13)：SDK 表现为
        # podman/api/uds.py `PermissionError: [Errno 13]`，CLI 表现为 `_ping ... permission denied`。
        # 属主/属组不可 chown/chmod（那会改到宿主 socket 本体，造成宿主侧权限回归，
        # 禁止 chmod 666 这类"捷径"）；唯一安全手段是让 devuser 与 socket 属组建立成员关系。
        # 时机要求：supervisord 的 drop_privileges() 在 spawn 子进程时用 grp.getgrall() 派生
        # 补充组，jupyter 子进程只能继承"exec supervisord 之前"已生效的组成员关系——
        # 本函数正是在 exec supervisord 之前被调用（见文件末尾主流程）。
        local sock_gid="" sock_group=""
        sock_gid="$(stat -Lc '%g' "${host_sock}" 2>/dev/null || true)"
        sock_group="$(stat -Lc '%G' "${host_sock}" 2>/dev/null || true)"
        if [ -z "${sock_group}" ] || [ "${sock_group}" = "UNKNOWN" ]; then
            sock_group="${sock_gid}"
        fi
        if [ -z "${sock_group}" ]; then
            log_warn "[B-scheme] Cannot resolve host socket group (stat failed on ${host_sock}); ${NON_ROOT_USER} may hit EACCES"
        elif id -nG "${NON_ROOT_USER}" 2>/dev/null | tr ' ' '\n' | grep -qx "${sock_group}"; then
            log_info "[B-scheme] ${NON_ROOT_USER} already in socket group '${sock_group}' (gid ${sock_gid})"
        elif usermod -aG "${sock_group}" "${NON_ROOT_USER}" 2>/dev/null; then
            log_info "[B-scheme] Added ${NON_ROOT_USER} to socket group '${sock_group}' (gid ${sock_gid})"
        else
            log_warn "[B-scheme] Failed to add ${NON_ROOT_USER} to socket group '${sock_group}' (gid ${sock_gid}); container-side podman may hit EACCES"
        fi

        # ── 自验证：以 devuser 身份实测 socket 可读写 ──
        # 仅告警不阻断：宿主 socket 属组若非"宿主主组→容器 gid 0"映射，加入 root 组仍会 EACCES，
        # 此时必须让用户看到明确的可操作提示，而不是等到 Notebook 里才报错。
        if su - "${NON_ROOT_USER}" -c "test -r '${run_sock_dir}/podman.sock' && test -w '${run_sock_dir}/podman.sock'"; then
            log_info "[B-scheme] [OK] ${NON_ROOT_USER} can read/write host podman socket"
        else
            log_warn "[B-scheme] ${NON_ROOT_USER} still cannot access ${run_sock_dir}/podman.sock (EACCES risk); expected socket group '${sock_group}' (gid ${sock_gid})"
        fi

        log_info "Podman rootless setup complete (host socket pass-through)"
        return 0
    fi

    # 回退模式不留 B-scheme 痕迹：事实文件与 sshd SetEnv 都移除（防御同一容器
    # 先 B-scheme 启动、后无 socket 重启的陈旧指向）。
    rm -f /etc/podman-host-sock.path 2>/dev/null || true
    sed -i '/^SetEnv CONTAINER_HOST=/d' /etc/ssh/sshd_config 2>/dev/null || true

    log_info "No host socket detected (HOST_PODMAN_SOCK unset/absent), falling back to in-container rootless daemon..."

    log_info "Triggering Podman rootless initialization (podman info)..."
    if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; podman info >/dev/null 2>&1"; then
        log_info "[OK] Podman rootless environment initialized successfully"
    else
        log_warn "Podman info command returned non-zero (this may be normal if subuid/subgid not fully configured on host)"
        log_info "Attempting podman system migrate..."
        su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; podman system migrate 2>/dev/null" || true
    fi

    log_info "Starting rootless podman system service (background)..."
    local podman_sock="${podman_run_dir}/podman/podman.sock"
    if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; test -S ${podman_sock}" 2>/dev/null; then
        log_info "[OK] rootless podman system service already online: ${podman_sock}"
    else
        su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; nohup podman system service --time=0 >/tmp/podman-service.log 2>&1 </dev/null &" || true
        for _i in $(seq 1 30); do
            if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; test -S ${podman_sock}" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        if su - "${NON_ROOT_USER}" -c "export XDG_RUNTIME_DIR=${podman_run_dir}; test -S ${podman_sock}" 2>/dev/null; then
            log_info "[OK] rootless podman system service online: ${podman_sock}"
        else
            log_warn "podman system service failed to start within 30s, last log lines:"
            tail -n 20 /tmp/podman-service.log 2>/dev/null || true
        fi
    fi

    # 与 B-scheme 分支保持同一契约：CONTAINER_HOST / XDG_RUNTIME_DIR 必须无条件导出。
    # 理由有二：① 让 jupyter.conf 可用 %(ENV_CONTAINER_HOST)s 继承动态路径（禁止硬编码 UID）；
    # ② supervisord 的 %(ENV_x)s 展开在变量缺失时会直接报错拒绝启动 jupyter 子进程。
    export CONTAINER_HOST="unix://${podman_run_dir}/podman/podman.sock"
    export XDG_RUNTIME_DIR="${podman_run_dir}"
    log_info "Podman rootless setup complete (in-container daemon, CONTAINER_HOST=${CONTAINER_HOST})"
}

setup_ssh_keys() {
    log_info "[Step 5/7] Configuring SSH public key auth..."
    local user="${NON_ROOT_USER}"
    if [ -n "${SSH_PUBLIC_KEY:-}" ]; then
        echo "$SSH_PUBLIC_KEY" >> "${NON_ROOT_HOME}/.ssh/authorized_keys"
        chmod 600 "${NON_ROOT_HOME}/.ssh/authorized_keys"
        chown "${user}:${user}" "${NON_ROOT_HOME}/.ssh/authorized_keys"
        if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
            mkdir -p /root/.ssh
            echo "$SSH_PUBLIC_KEY" >> /root/.ssh/authorized_keys
            chmod 600 /root/.ssh/authorized_keys
        fi
        local key_count
        key_count=$(grep -c "ssh-" "${NON_ROOT_HOME}/.ssh/authorized_keys" 2>/dev/null || echo 0)
        log_info "SSH public keys injected (count: ${key_count})"
    else
        log_info "No SSH_PUBLIC_KEY set, password auth only"
    fi
}

setup_jupyter() {
    log_info "[Step 6/7] Configuring Jupyter..."
    local jupyter_config_dir="${NON_ROOT_HOME}/.jupyter"
    local jupyter_runtime_config="${jupyter_config_dir}/jupyter_server_config.d/runtime.py"

    mkdir -p "${jupyter_config_dir}/jupyter_server_config.d"
    chown -R "${NON_ROOT_USER}:${NON_ROOT_USER}" "${jupyter_config_dir}" 2>/dev/null || true
    chmod 700 /root/.ssh 2>/dev/null || true

    cat > "$jupyter_runtime_config" << 'JUPYTER_RUNTIME_EOF'
c = get_config()
JUPYTER_RUNTIME_EOF

    if [ -n "${JUPYTER_PASSWORD:-}" ]; then
        log_info "Setting Jupyter password from JUPYTER_PASSWORD env var..."
        local jupyter_password_hash
        jupyter_password_hash=$(JUPYTER_PASSWORD="${JUPYTER_PASSWORD}" "${CONDA_PYTHON}" -c "
import os
from jupyter_server.auth import passwd
print(passwd(os.environ['JUPYTER_PASSWORD']))
")
        cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.password = '${jupyter_password_hash}'  # nosec B105 - variable hash, not hardcoded
c.ServerApp.token = ''
c.IdentityProvider.token = ''
JUPYTER_RUNTIME_EOF
        log_info "Jupyter password authentication configured"
    elif [ -n "${JUPYTER_TOKEN:-}" ]; then
        log_info "Using JUPYTER_TOKEN from env var..."
        cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.token = '${JUPYTER_TOKEN}'
c.ServerApp.password = ''
c.IdentityProvider.token = '${JUPYTER_TOKEN}'
JUPYTER_RUNTIME_EOF
    else
        JUPYTER_TOKEN=$(pwgen -s 32 1)
        cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.token = '${JUPYTER_TOKEN}'
c.ServerApp.password = ''
c.IdentityProvider.token = '${JUPYTER_TOKEN}'
JUPYTER_RUNTIME_EOF
        log_warn "JUPYTER_TOKEN not set, generated random token"
    fi

    cat >> "$jupyter_runtime_config" << JUPYTER_RUNTIME_EOF
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = ${JUPYTER_PORT:-8888}
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '/workspace'
c.ServerApp.allow_root = True
c.ServerApp.allow_origin = '${JUPYTER_ALLOW_ORIGIN:-}'
c.ServerApp.allow_credentials = True
c.ContentsManager.allow_hidden = True
c.FileContentsManager.allow_hidden = True
JUPYTER_RUNTIME_EOF

    chmod 777 /workspace 2>/dev/null || true
    log_info "Jupyter runtime config written to ${jupyter_runtime_config}"
    log_info "Jupyter configured (root_dir: /workspace, port: ${JUPYTER_PORT:-8888}, python: ${CONDA_PYTHON})"
}

print_access_info() {
    log_info "[Step 7/7] Preparing access information..."
    echo ""
    echo "============================================================"
    echo "  Container ready! Services managed by supervisord"
    echo ""
    echo "  SSH access:"
    echo "    ssh ${NON_ROOT_USER}@<host> -p <mapped-port>"
    echo "    Password: ${USER_PASSWORD:-<set via USER_PASSWORD env>}"
    if [ "${ALLOW_ROOT_SSH:-no}" = "yes" ]; then
        echo "    ssh root@<host> -p <mapped-port>"
        echo "    Root password: ${ROOT_PASSWORD:-<set via ROOT_PASSWORD env>}"
    fi
    echo ""
    echo "  Jupyter access:"
    echo "    URL: http://<host>:<mapped-port>/"
    if [ -n "${JUPYTER_TOKEN:-}" ]; then
        echo "    Token: ${JUPYTER_TOKEN}"
    fi
    if [ -n "${JUPYTER_PASSWORD:-}" ]; then
        echo "    Password: (use JUPYTER_PASSWORD you set)"
    fi
    echo ""
    echo "  Podman (rootless): available for ${NON_ROOT_USER}"
    echo "    (Run 'podman info' after login to verify)"
    echo ""
    echo "  Working directory: /workspace (mount a volume here for persistence)"
    echo "  Conda environment: ${CONDA_ENV} (${CONDA_ENV_PATH})"
    echo "============================================================"
    echo ""
}

print_banner

if [ $# -gt 0 ]; then
    log_info "Command mode detected: '$*' - skipping service startup, exec user command as ${NON_ROOT_USER}"
    diagnose_system
    setup_passwords
    setup_podman
    log_info "Entering user command (tini as init, signals forwarded)..."
    echo ""
    run_as_user "$@"
fi

diagnose_system
setup_passwords
generate_host_keys
configure_sshd
setup_podman
setup_ssh_keys
setup_jupyter
print_access_info

log_info "Starting supervisord (nodaemon mode)..."
log_info "  - sshd runs as root (required for port 22)"
log_info "  - jupyter runs as ${NON_ROOT_USER} (configured in supervisor conf)"
exec /usr/bin/supervisord -c "${SUPERVISORD_CONF}"
