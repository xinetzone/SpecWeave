#!/bin/bash
# toolbox 包装器：容器内裸跑时优雅降级，Toolbx 会话内透明转发。
#
# 背景：上游二进制（/usr/local/libexec/toolbox）的 preRun 要求：只要检测到自身运行在容器内
#       （存在 /run/.containerenv），就必须已注入 TOOLBOX_PATH——该变量由宿主侧 Toolbx 启动器提供。
#       普通 `podman run` / `podman-compose` 会话没有宿主启动器，因此直接暴露裸错误
#       "Error: TOOLBOX_PATH not set"（退出码 1），用户无从得知原因与替代路径。
#
# 做法：上游二进制保持原样（vendor/toolbox 只读，不修改其源码），仅在其前加一层显式分派：
#       1) 真实 Toolbx 会话（TOOLBOX_PATH 非空）→ exec 真二进制，行为与上游完全一致；
#       2) 帮助/版本短路 flag → exec 真二进制（cobra 在 PersistentPreRunE 之前处理该分支，不依赖 TOOLBOX_PATH）；
#       3) 其余情况 → 输出可执行指引 + 稳定英文标记行，退出码与上游保持一致（1）。
#
# 说明见 docs/07-toolbx-passthrough.md 与 docs/17-upstream-tools.md。

real_toolbox="/usr/local/libexec/toolbox"

if [ -n "${TOOLBOX_PATH:-}" ]; then
    exec "$real_toolbox" "$@"
fi

case "${1:-}" in
    -h | --help | --version)
        exec "$real_toolbox" "$@"
        ;;
esac

echo "toolbox: TOOLBOX_PATH is not set in this session" >&2
cat >&2 <<'EOF'

当前不在 Toolbx 会话内，toolbox 无法在此运行。
原因：TOOLBOX_PATH 由宿主机的 Toolbx 启动器注入，普通容器会话不具备该上下文。

可改用以下方式之一：
  1) 查看版本或帮助（不受影响）：
       toolbox --version
       toolbox --help
  2) 在本镜像内直接使用 Podman（无需 Toolbx）：
       podman info
  3) 若确实需要 Toolbx 会话，请在宿主机执行：
       toolbox create -i jupyter-podman-rootless:latest -c jupyter-dev
       toolbox enter jupyter-dev

详见 docs/07-toolbx-passthrough.md（Toolbx 透传）与 docs/17-upstream-tools.md（上游工具）。
EOF

exit 1
