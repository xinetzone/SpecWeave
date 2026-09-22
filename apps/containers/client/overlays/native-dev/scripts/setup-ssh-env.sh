#!/bin/bash
# ==============================================================================
# setup-ssh-env.sh — 让 SSH 会话同样拿到 compose 注入的源码调试环境变量
#
# 背景（2026-09-20 实证 / C30）：compose `environment` 注入的 5 个调试变量只到达
#   容器 PID 1（`podman exec` 可见）与 Jupyter 内核（kernel.json 内嵌），
#   **SSH 会话拿不到**——sshd 派生会话不继承容器 config env；且 `ssh host "cmd"`
#   的最外层 bash -c 既不读 /etc/profile.d/*、也不读 ~/.bashrc / BASH_ENV
#   （实测：bash 仅在执行脚本文件时读 BASH_ENV，-c 命令字符串不读）。
#   症状：SSH 进容器跑 `python tools/accuracy.py` 报
#   `ModuleNotFoundError: No module named 'xmnn'`——tvm/vta/xmnn 经 PYTHONPATH
#   从 /workspace 挂载树导入，不是 site-packages。
#
# 双通道注入（与基底 entrypoint 的 `SetEnv CONTAINER_HOST=` 先例同构）：
#   ① /etc/profile.d/50-native-dev-env.sh —— login shell（jupyter Terminal 的
#      `bash -l`、`ssh -t` 交互式）；`${VAR:=默认}` 语义，已存在则不覆盖；
#   ② sshd_config 的 `SetEnv` —— 覆盖 `ssh host "cmd"` 的非交互 bash -c：
#      sshd 直接把变量放进会话进程环境，是唯一不经任何 shell 启动文件的注入点。
#
# 关键实测（勿改回多行）：sshd_config 对 `SetEnv` 是 **first-wins**——
#   写 5 行 `SetEnv VAR=...` 时 `sshd -T` 只回显第一条，其余 4 条被静默丢弃；
#   必须写成**单行 5 个 NAME=VALUE 空格分隔**（`sshd -T` 实测 5 条全回显）。
#
# 幂等：两处都是「先删旧行、再写新行」；`sshd -t` 校验失败即整段回滚，
#   绝不让容器因注入而 sshd 起不来。
# 值必须与 overlays/native-dev/compose.yaml 的 environment 逐字一致
#   （tests/test_native_dev_ssh_env.py 锁死，防两处漂移）。
# ==============================================================================
set -euo pipefail

# 三个路径可被环境变量改写，仅供 tests/test_native_dev_ssh_env.py 在临时目录里
# 实跑本脚本（生产路径即默认值，容器内勿设置）。
PROFILE_FILE="${NATIVE_SSH_ENV_PROFILE_FILE:-/etc/profile.d/50-native-dev-env.sh}"
SSHD_CONFIG="${NATIVE_SSH_ENV_SSHD_CONFIG:-/etc/ssh/sshd_config}"
SSHD_BIN="${NATIVE_SSH_ENV_SSHD_BIN:-/usr/sbin/sshd}"

# ── 与 compose.yaml 的 environment 同值（单一事实源：compose.yaml）────────────
PYTHONPATH_VALUE=/workspace/npu_tvm/python:/workspace/npu_tvm/vta/python:/workspace/npuusertools
TVM_LIBRARY_PATH_VALUE=/workspace/npu_tvm/build
LD_LIBRARY_PATH_VALUE=/workspace/npu_tvm/build:/workspace/npu_tvm/build/vta:/opt/conda/envs/main/lib
NPU_TOOLS_ROOT_VALUE=/workspace
XMNN_TOOLS_ROOT_VALUE=/workspace/npuusertools

VARS=(PYTHONPATH TVM_LIBRARY_PATH LD_LIBRARY_PATH NPU_TOOLS_ROOT XMNN_TOOLS_ROOT)

# ── 通道①：login shell（/etc/profile.d，jupyter Terminal 的 bash -l 也读）──────
{
    echo '#!/bin/sh'
    echo '# 由 overlays/native-dev/scripts/setup-ssh-env.sh 生成，勿手工编辑（见脚本头注）。'
    echo '# `${VAR:=默认}`：已存在则不覆盖；SSH 会话默认拿不到容器 config env。'
    for name in "${VARS[@]}"; do
        ref="${name}_VALUE"
        printf ': "${%s:=%s}"\nexport %s\n' "${name}" "${!ref}" "${name}"
    done
} > "${PROFILE_FILE}"
chmod 644 "${PROFILE_FILE}"

# ── 通道②：sshd SetEnv（`ssh host "cmd"` 非交互形态）──────────────────────────
# 幂等清理：删掉本脚本写过的全部形态（历史多行形态、以及上一次留下的标记行），
# 只按我们自己的键名/标记匹配，不误伤使用者自行添加的其它 SetEnv。
sed -i -E -e '/^# native-dev ssh-env/d' \
    -e '/^SetEnv .*(PYTHONPATH|TVM_LIBRARY_PATH|LD_LIBRARY_PATH|NPU_TOOLS_ROOT|XMNN_TOOLS_ROOT)=/d' \
    "${SSHD_CONFIG}"

cp -p "${SSHD_CONFIG}" "${SSHD_CONFIG}.native-dev.bak"
{
    echo '# native-dev ssh-env (managed by setup-ssh-env.sh; SetEnv is first-wins, keep it on ONE line)'
    printf 'SetEnv'
    for name in "${VARS[@]}"; do
        ref="${name}_VALUE"
        printf ' %s=%s' "${name}" "${!ref}"
    done
    printf '\n'
} >> "${SSHD_CONFIG}"

if "${SSHD_BIN}" -t; then
    rm -f "${SSHD_CONFIG}.native-dev.bak"
else
    mv -f "${SSHD_CONFIG}.native-dev.bak" "${SSHD_CONFIG}"
    echo "[ssh-env] ERROR: sshd_config invalid after SetEnv injection, reverted" >&2
    exit 1
fi

# 生效性自检：sshd -T 必须回显全部 5 条（first-wins 陷阱的守卫）
effective=$("${SSHD_BIN}" -T 2>/dev/null | grep -c '^setenv ')
if [ "${effective}" -ne "${#VARS[@]}" ]; then
    echo "[ssh-env] ERROR: sshd -T reports ${effective} setenv entries, expected ${#VARS[@]}" >&2
    exit 1
fi

# 让运行中的 sshd 重读配置：实测 sshd **不在每次连接时重读** sshd_config
# （监听进程启动即缓存），只改文件不 SIGHUP 时新连接仍拿不到 SetEnv。
# SIGHUP 使 sshd re-exec 重读配置，已建立的会话不受影响（sshd-session 是独立
# 进程）；构建期无 sshd 进程，此段自动跳过。
# 仅当改写的是运行中 sshd 真正读取的那份配置（默认路径）时才重载——测试替身
# （NATIVE_SSH_ENV_SSHD_CONFIG 指向临时文件）不去触碰宿主/其它 sshd 进程。
if [ "${SSHD_CONFIG}" = "/etc/ssh/sshd_config" ]; then
    sshd_master=$(pgrep -x sshd 2>/dev/null | head -1 || true)
    if [ -n "${sshd_master}" ]; then
        kill -HUP "${sshd_master}"
        echo "[ssh-env] sshd (pid ${sshd_master}) 已 SIGHUP 重读配置"
    fi
fi

echo "[ssh-env] profile.d  : ${PROFILE_FILE}"
echo "[ssh-env] sshd SetEnv: ${VARS[*]}（${effective} 条已生效）"
