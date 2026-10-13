"""okw CLI 的 argparse 装配（纯函数层）。

职责边界：本模块只描述命令面，不读 argv、不做 IO、不触子进程；
``build_parser()`` 可被快照测试反复调用。子组空命令的帮助回打通过装配期
``set_defaults`` 绑定该子 parser 自身的 ``print_help`` 闭包实现，
不依赖 argparse 任何下划线私有属性（由 test_no_private_argparse_api
逐字符串门禁保护）。
"""

import argparse

from okw import __version__, compose, desktop, distro, image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="okw",
        description="openKylin WSL 开发工具包：以 WSL 为切入点的发行版管理、环境验收、脚手架与知识参考。",
    )
    parser.add_argument("--version", action="version", version=f"okw {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    sub.add_parser("list", help="列出 WSL 发行版（含默认星标）")
    p_status = sub.add_parser("status", help="查看单个发行版状态")
    p_status.add_argument("name")

    p_import = sub.add_parser("import", help="导入 openKylin 镜像（wsl --import 封装）")
    p_import.add_argument("image", help=".wsl 镜像文件路径（gzip tar）")
    p_import.add_argument("--name", required=True, help="发行版名称，如 openKylin-3.0")
    p_import.add_argument("--location", required=True, help="安装目录（VHD 存放位置）")
    p_import.add_argument("--version", default=distro.DEFAULT_IMPORT_VERSION, help="WSL 版本（默认 2）")

    p_export = sub.add_parser("export", help="导出发行版为 tar 包")
    p_export.add_argument("name")
    p_export.add_argument("--output", required=True, help="输出文件路径")

    p_unreg = sub.add_parser("unregister", help="注销发行版（破坏性，需 --yes）")
    p_unreg.add_argument("name")
    p_unreg.add_argument("--yes", action="store_true", help="确认注销")

    p_exec = sub.add_parser("exec", help="在发行版内执行命令")
    p_exec.add_argument("name")
    p_exec.add_argument("cmd", nargs=argparse.REMAINDER, help="命令及参数（建议加 -- 分隔）")

    p_verify = sub.add_parser("verify", help="openKylin 环境五步验收")
    p_verify.add_argument("name")

    p_scaff = sub.add_parser("scaffold", help="生成开发脚手架（deb / dput）")
    p_scaff.add_argument("kind", choices=["deb", "dput"], help="脚手架类型")
    p_scaff.add_argument("--project", help="deb：项目名")
    p_scaff.add_argument("--series", help="deb：系列代号 yangtze/nile/huanghe（或 1.0/2.0/3.0）")
    p_scaff.add_argument("--version", help="deb：包版本，如 0.1.0")
    p_scaff.add_argument("--output-dir", default=".", help="deb：目标目录（默认当前目录）")
    p_scaff.add_argument("--openkylin-id", help="dput：openKylin 账号 ID")
    p_scaff.add_argument("--output", help="dput：输出文件路径（默认打印片段）")

    p_ref = sub.add_parser("ref", help="openKylin 知识库快速参考")
    p_ref.add_argument(
        "topic", nargs="?", help="主题：series/wsl-troubleshoot/okbs/verify/ai-stack"
    )

    # ai 子命令组：preflight / install / verify（本期仅 OCR 已验证路径）
    ai_epilog = (
        "退出码：0=全部 PASS；1=存在 FAIL（按报告中的中文指引修复后重试）；"
        "2=用法错误、preflight/verify 仅 UNKNOWN，或 install 未提供 --yes（零写入）。\n"
        "边界：okw 不配置 API Key/Token、不下载模型、不安装 ollama；Gen2 全栈仅只读盘点。"
    )
    p_ai = sub.add_parser(
        "ai",
        help="openKylin AI 栈：只读盘点、显式安装已验证 OCR 路径并验收",
        description=(
            "三步流程：preflight 单批 apt-cache policy 只读盘点 AI 分层组件；"
            "install --yes 仅安装已验证直接包 libkylin-ai-base-dev（APT 解析 tesseract 与 "
            "chi_sim/eng 语言包）；verify 只读确认本地 OCR 可用，--smoke-ocr 对本地图片离线识别。"
        ),
        epilog=ai_epilog,
    )
    # 装配期闭包：`okw ai` 无子命令时回打本子组帮助（退出码在 main 中给 2）。
    p_ai.set_defaults(_group_help=p_ai.print_help)
    p_ai_sub = p_ai.add_subparsers(dest="ai_cmd", metavar="<ai_cmd>")

    p_ai_preflight = p_ai_sub.add_parser(
        "preflight",
        help="只读盘点：发行版/WSL版本/openKylin身份/APT能力/AI 分层组件候选",
        description=(
            "只读预检，单条 apt-cache policy 批量盘点；不触发 apt update、不写文件、"
            "不改默认发行版。OCR 必选组件有候选标 PASS；可选层缺失标 UNKNOWN 不阻断；"
            "索引过期给出手动 apt update 建议，网络错误给出排查方向。"
        ),
        epilog=ai_epilog,
    )
    p_ai_preflight.add_argument("name", help="发行版名称（wsl -l -v 查看）")

    p_ai_install = p_ai_sub.add_parser(
        "install",
        help="安装已验证 OCR 路径 libkylin-ai-base-dev（必须 --yes）",
        description=(
            "--yes 后：① root apt update 刷新索引；② root apt install -y "
            "--no-install-recommends libkylin-ai-base-dev（APT 解析 OCR 运行库、tesseract、"
            "chi_sim/eng 语言包）；③ 默认用户只读 OCR 验收。漏 --yes 仅打印 3 条副作用清单、"
            "退出码 2、零写入。不改软件源/wsl.conf/默认发行版，不装可选层、模型或 ollama。"
        ),
        epilog=ai_epilog,
    )
    p_ai_install.add_argument("name", help="发行版名称（wsl -l -v 查看）")
    p_ai_install.add_argument(
        "--yes",
        action="store_true",
        help="显式确认 apt update、安装 libkylin-ai-base-dev 及依赖、事后只读 OCR 验收",
    )

    p_ai_verify = p_ai_sub.add_parser(
        "verify",
        help="只读验收本地 OCR（默认不识别；--smoke-ocr 对本地图片离线识别）",
        description=(
            "只读检查 Gen1 SDK/运行库已装、tesseract --version 与 --list-langs 含 chi_sim+eng；"
            "可选层缺失仅 UNKNOWN 不阻断。--smoke-ocr 仅对发行版内本地图片执行一次离线识别，"
            "不访问网络、不下载模型。"
        ),
        epilog=ai_epilog,
    )
    p_ai_verify.add_argument("name", help="发行版名称（wsl -l -v 查看）")
    p_ai_verify.add_argument(
        "--smoke-ocr",
        metavar="IMAGE",
        help="发行版内可访问的本地图片路径；仅对其离线识别，失败报错且不触网",
    )

    # image 子命令组：build / verify（对齐 podman 组的禁拉取与退出码纪律）
    image_epilog = (
        "退出码：0=全部 PASS；1=存在 FAIL（按报告中的中文指引修复后重试）；"
        "2=用法错误或仅 UNKNOWN。全程禁止隐式拉取（仅 build 的 --pull-base 显式放行基底）。"
    )
    p_image = sub.add_parser(
        "image",
        help="openKylin 开发容器镜像：在发行版内构建与验收",
        description=(
            "两步流程：build 在指定发行版内（root 身份）构建 localhost/openkylin-dev:<tag>"
            "（基镜像默认仅本地，构建上下文自动同步到发行版内 /tmp）；"
            "verify 验收镜像——本地存在 + 静态探针 + 全量启动健康 + 服务/HTTP，"
            "容器操作全程 --pull=never 且使用 G3 运行契约参数。"
        ),
        epilog=image_epilog,
    )
    # 装配期闭包：`okw image` 无子命令时回打本子组帮助（退出码在 main 中给 2）。
    # 注意：argparse 会把该默认传播给 image 组下叶子命令的 Namespace；
    # 仅 main 在「无叶子」分支使用，handler 一律不得读取 _group_help。
    p_image.set_defaults(_group_help=p_image.print_help)
    p_image_sub = p_image.add_subparsers(dest="image_cmd", metavar="<image_cmd>")

    p_img_build = p_image_sub.add_parser(
        "build",
        help="在发行版内构建 localhost/openkylin-dev:<tag>（root 身份）",
        description=(
            "发行版内 root 身份执行：podman 可用性 → 基镜像本地存在（默认禁拉；"
            "--pull-base 显式放行）→ 上下文同步（Windows 路径转发行版内 /tmp，"
            "或 --context 指定发行版内已有目录）→ podman build --format docker。"
        ),
        epilog=image_epilog,
    )
    p_img_build.add_argument("name", help="发行版名称（wsl -l -v 查看）")
    p_img_build.add_argument("--tag", default=image.DEFAULT_TAG, help=f"镜像标签（默认 {image.DEFAULT_TAG}）")
    p_img_build.add_argument(
        "--base-image",
        default=image.DEFAULT_BASE_IMAGE,
        help=f"基底镜像（默认 {image.DEFAULT_BASE_IMAGE}，本地导入的 3.0 rootfs）",
    )
    p_img_build.add_argument(
        "--pull-base",
        action="store_true",
        help="基底镜像本地缺失时显式允许拉取（默认禁止任何隐式拉取）",
    )
    p_img_build.add_argument("--no-cache", action="store_true", help="构建时禁用层缓存")
    p_img_build.add_argument(
        "--context",
        help="构建上下文目录（Windows 绝对路径或发行版内绝对路径；默认包内 openkylin-dev-container/）",
    )

    p_img_verify = p_image_sub.add_parser(
        "verify",
        help="验收镜像：本地存在 + 静态探针 + 全量启动健康 + 服务/HTTP",
        description=(
            "发行版内 root 身份执行：podman 可用性 → 镜像本地存在（禁拉）→ "
            "静态探针（P1-P8，--entrypoint /bin/bash）→ 后台启动等待 HEALTHCHECK → "
            "服务探针（SSH/Jupyter 进程、22/8888 端口、Jupyter HTTP 200）→ 清理临时容器。"
            "--no-boot 时只做静态探针。"
        ),
        epilog=image_epilog,
    )
    p_img_verify.add_argument("name", help="发行版名称")
    p_img_verify.add_argument("--image", default=image.DEFAULT_IMAGE, help=f"待验收镜像（默认 {image.DEFAULT_IMAGE}）")
    p_img_verify.add_argument("--no-boot", action="store_true", help="只做静态探针，不启动服务栈")

    # podman 子命令组：preflight / install / verify
    podman_epilog = (
        "退出码：0=全部 PASS；1=存在 FAIL（按报告中的中文指引修复后重试）；"
        "2=用法错误、preflight/verify 仅 UNKNOWN，或 install 未提供 --yes（零写入）。"
    )
    p_podman = sub.add_parser(
        "podman",
        help="openKylin 发行版内 rootless Podman 预检、安装与验收",
        description=(
            "三步流程：先 preflight 只读探测风险项与缺失，"
            "确认无风险后 install --yes 执行安装与 subuid/subgid 映射追加，"
            "最后 verify 验收 rootless 上下文；--smoke-image 需本地已存在镜像。"
        ),
        epilog=podman_epilog,
    )
    # 装配期闭包：`okw podman` 无子命令时回打本子组帮助（退出码在 main 中给 2）。
    # 注意：argparse 会把该默认传播给 podman 组下叶子命令的 Namespace；
    # 仅 main 在「无叶子」分支使用，handler 一律不得读取 _group_help。
    p_podman.set_defaults(_group_help=p_podman.print_help)
    p_podman_sub = p_podman.add_subparsers(dest="podman_cmd", metavar="<podman_cmd>")

    p_preflight = p_podman_sub.add_parser(
        "preflight",
        help="只读预检：发行版/WSL版本/openKylin身份/APT能力/包候选/subuid+subgid映射",
        description=(
            "只读预检，不触发 apt update、不写文件、不改默认发行版星标。"
            "APT 索引缺失时候选标为 UNKNOWN 并给出行动建议；"
            "映射已有冲突时 install 阶段将拒绝自动追加。"
        ),
        epilog=podman_epilog,
    )
    p_preflight.add_argument("name", help="发行版名称（wsl -l -v 查看）")

    p_install = p_podman_sub.add_parser(
        "install",
        help="在目标发行版内安装 4 个直接包 + 追加 subuid/subgid 映射（必须 --yes）",
        description=(
            "--yes 后将执行：① root 身份 apt update + 复查候选；"
            "② 安装 4 个直接包（podman/uidmap/slirp4netns/fuse-overlayfs）；"
            "③ 为默认用户追加 subuid/subgid 映射（仅在标准区间 [100000, 165536) "
            "   与其它用户无冲突且畸形文件中止时才写入）；"
            "④ 最后以默认用户身份运行 rootless verify。"
            "漏 --yes 时仅输出 4 条副作用清单并以退出码 2 中止，不做任何写入。"
            "不修改软件源、不修改 wsl.conf、不修改默认发行版星标。"
        ),
        epilog=podman_epilog,
    )
    p_install.add_argument("name", help="发行版名称")
    p_install.add_argument(
        "--yes",
        action="store_true",
        help=(
            "显式确认后才执行副作用：(1) 触发 apt update 刷新 APT 索引；"
            "(2) root 安装 4 个直接包（含传递依赖）；"
            "(3) 向 /etc/subuid 与 /etc/subgid 追加默认用户映射区间 [100000, 165536) "
            "（仅在文件完好、同名无冲突、与其它用户不重叠时才写）；"
            "(4) 运行默认用户身份的 rootless verify。"
        ),
    )

    p_verify_podman = p_podman_sub.add_parser(
        "verify",
        help="验收默认用户下 rootless Podman 上下文（默认只读，不跑容器）",
        description=(
            "默认用户身份检查：subuid/subgid 映射、unshare 是否可用、podman info --rootless。"
            "默认只读不创建/启动容器；--smoke-image 需本地已存在该镜像，不触发隐式拉取。"
        ),
        epilog=podman_epilog,
    )
    p_verify_podman.add_argument("name", help="发行版名称")
    p_verify_podman.add_argument(
        "--smoke-image",
        metavar="LOCAL_IMAGE",
        help=(
            "存在本地的可用镜像名（REPOSITORY:TAG / 镜像 ID），"
            "若不存在将直接 FAIL 并提示先在发行版内 podman pull / podman load；"
            "严禁触发任何隐式 registry 拉取。"
        ),
    )

    # compose 子命令组：preflight / install / verify（rootless podman 的下游引导层）
    compose_epilog = (
        "退出码：0=全部 PASS；1=存在 FAIL（按报告中的中文指引修复后重试）；"
        "2=用法错误、preflight/verify 仅 UNKNOWN，或 install 未提供 --yes（零写入）。\n"
        + compose.LICENSE_NOTICE
    )
    p_compose = sub.add_parser(
        "compose",
        help="在 rootless Podman 就绪后引导 xuan-compose（xc，GPL-2.0-only 第三方）",
        description=(
            "下游引导三步：preflight 只读探测 rootless podman/uv/Python3.14/xc shim；"
            "install --yes 经用户级 uv（~/.local/bin）托管 Python 3.14 并以 uv tool 安装"
            " xuan-compose，生成 xc 与 xuan-compose 两个 shim；verify 只读验收双 shim，"
            "--smoke 在隔离临时目录跑 xc config --quiet 做端到端探活（不起容器不拉镜像）。"
            "安装源 --source 必填：本地目录 / git+https URL / 包名，okw 不内置任何默认源。"
        ),
        epilog=compose_epilog,
    )
    # 装配期闭包：`okw compose` 无子命令时回打本子组帮助（退出码在 main 中给 2）。
    p_compose.set_defaults(_group_help=p_compose.print_help)
    p_compose_sub = p_compose.add_subparsers(dest="compose_cmd", metavar="<compose_cmd>")

    p_compose_preflight = p_compose_sub.add_parser(
        "preflight",
        help="只读预检：rootless podman / uv / 托管 Python3.14 / xc shim / 可选安装源",
        description=(
            "只读预检，不下载、不写文件。uv、Python 3.14、xc shim 缺失标 UNKNOWN"
            "（install 可自动补齐）；结构门与 rootless podman 失败为 FAIL。"
            "--source 可预检本地目录（校验 pyproject.toml）；URL/包名源不触网，标 UNKNOWN。"
        ),
        epilog=compose_epilog,
    )
    p_compose_preflight.add_argument("name", help="发行版名称（wsl -l -v 查看）")
    p_compose_preflight.add_argument(
        "--source",
        help="可选：本地目录（Windows 路径自动转 /mnt/<drive>）/ git+https URL / 包名",
    )

    p_compose_install = p_compose_sub.add_parser(
        "install",
        help="经用户级 uv 引导安装 xuan-compose（必须 --yes，--source 必填）",
        description=(
            "--yes 且 rootless podman 就绪后：① 缺 uv 则装到 ~/.local/bin（无需 root）；"
            "② uv python install 3.14 托管独立解释器（不改系统 Python）；"
            "③ uv tool install 安装 xuan-compose 并生成 xc/xuan-compose 双 shim"
            "（已装则 --force 幂等；本地源默认拷贝安装，--editable 仅限本地源）；"
            "④ 全路径执行双 shim version --short 验收。漏 --yes 仅打印副作用清单，零写入。"
        ),
        epilog=compose_epilog,
    )
    p_compose_install.add_argument("name", help="发行版名称")
    p_compose_install.add_argument(
        "--source",
        required=True,
        help="必填：本地目录 / git+https 等 URL / PEP503 包名（okw 不内置默认源）",
    )
    p_compose_install.add_argument(
        "--yes",
        action="store_true",
        help="显式确认下载与用户级安装副作用（详见子命令 description 四步）",
    )
    p_compose_install.add_argument(
        "--editable",
        action="store_true",
        help="本地源以可编辑模式安装（uv tool install --editable）；仅本地目录源允许",
    )

    p_compose_verify = p_compose_sub.add_parser(
        "verify",
        help="验收双 shim 与 rootless 上下文（默认只读；--smoke 做配置解析端到端探活）",
        description=(
            "只读检查 rootless podman 与 ~/.local/bin 下 xc、xuan-compose 双 shim 的"
            " version --short 一致性。--smoke 在 /tmp 隔离目录写最小 compose.yaml 并执行"
            " xc config --quiet（xc 内部触达 podman info），不起容器、不拉镜像，结束即清理。"
        ),
        epilog=compose_epilog,
    )
    p_compose_verify.add_argument("name", help="发行版名称")
    p_compose_verify.add_argument(
        "--smoke",
        action="store_true",
        help="执行隔离临时目录内的 xc config --quiet 端到端探活（非容器冒烟）",
    )

    # desktop 子命令组：preflight / install / verify（openKylin UKUI 桌面 / xrdp）
    desktop_epilog = (
        "退出码：0=PASS；1=FAIL（按中文指引修复后重试）；2=用法错误或 install 未提供 --yes（零写入）。"
        "桌面由发行版内 xrdp 提供，Windows 侧用 mstsc 连接 localhost:<port>（默认 3390）。"
    )
    p_desktop = sub.add_parser(
        "desktop",
        help="openKylin UKUI 桌面（xrdp/WSL）预检、补齐与验收",
        description=(
            "针对已预装桌面的 openKylin Desktop WSL 镜像：preflight 只读预检桌面链路"
            "（结构项/服务/端口/默认用户/首登黑屏看门狗）；install --yes 以 root 幂等启用 "
            "xrdp 与 xrdp-sesman，并以默认用户补齐 ~/.xsession 看门狗（含备份）；verify "
            "只读验收并附加 Windows 侧回环端口可达性。okw 不安装桌面套件。"
        ),
        epilog=desktop_epilog,
    )
    p_desktop.set_defaults(_group_help=p_desktop.print_help)
    p_desktop_sub = p_desktop.add_subparsers(dest="desktop_cmd", metavar="<desktop_cmd>")

    p_desk_pre = p_desktop_sub.add_parser("preflight", help="只读预检桌面链路", epilog=desktop_epilog)
    p_desk_pre.add_argument("name", help="发行版名称（wsl -l -v 查看）")
    p_desk_pre.add_argument("--port", type=int, default=desktop.DEFAULT_PORT, help="远程桌面端口（默认 3390）")

    p_desk_ins = p_desktop_sub.add_parser("install", help="启用 xrdp 并补齐首登黑屏看门狗（必须 --yes）", epilog=desktop_epilog)
    p_desk_ins.add_argument("name", help="发行版名称")
    p_desk_ins.add_argument("--yes", action="store_true", help="显式确认启用服务与改写 ~/.xsession 的副作用")
    p_desk_ins.add_argument("--port", type=int, default=desktop.DEFAULT_PORT, help="远程桌面端口（默认 3390）")

    p_desk_ver = p_desktop_sub.add_parser("verify", help="只读验收桌面链路与 Windows 侧端口", epilog=desktop_epilog)
    p_desk_ver.add_argument("name", help="发行版名称")
    p_desk_ver.add_argument("--port", type=int, default=desktop.DEFAULT_PORT, help="远程桌面端口（默认 3390）")

    return parser
