"""okw CLI：argparse 装配。

子命令：list / status / import / export / unregister / exec / verify / scaffold / ref / podman。
"""

import argparse
import sys

from okw import __version__, distro, podman, ref, scaffold, verify

def _print(text: str = "") -> None:
    print(text)

def cmd_list(_args) -> int:
    try:
        distros = distro.list_distros()
    except distro.WslError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    if not distros:
        print("未发现任何 WSL 发行版（wsl --import 导入 openKylin 后重试）")
        return 0
    print(f"共 {len(distros)} 个 WSL 发行版：")
    for d in distros:
        star = "*" if d.is_default else " "
        print(f"  {star} {d.name:<24} WSL{d.version:<3} {d.state}")
    default = distro.default_distro_name()
    if default:
        print(f"默认发行版（星标保护）：{default}")
    return 0

def cmd_status(args) -> int:
    try:
        d = distro.get_distro(args.name)
    except distro.WslError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    if d is None:
        print(f"发行版 {args.name} 不存在（wsl -l -v 查看在列发行版）", file=sys.stderr)
        return 1
    star = "（默认）" if d.is_default else ""
    print(f"{d.name}: WSL{d.version} / {d.state} {star}")
    return 0

def cmd_import(args) -> int:
    try:
        res = distro.import_distro(args.image, args.name, args.location, args.version)
    except distro.WslError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    if not res.ok:
        print("导入失败，按知识库 §4 排障三问排查：", file=sys.stderr)
        print("  1) 失败位置是否漂移（镜像位置/导入目录发生变化）→ 固定位置重试", file=sys.stderr)
        print("  2) 空闲内存是否不足（0.8GB 失败 / 4.5GB 成功）→ wsl --shutdown 后重试", file=sys.stderr)
        print("  3) 仍失败：把 .wsl 解压为纯 tar 再 import", file=sys.stderr)
        if res.stderr.strip():
            print(f"  原始错误：{res.stderr.strip()[:300]}", file=sys.stderr)
        return res.exit_code or 1
    print(f"导入成功：{args.name}（{args.location}）")
    print("提示：默认账号 openkylin/openkylin 为弱口令，首次进入请立即 passwd；", file=sys.stderr)
    print("      桌面版镜像请用 xrdp 连接 3390 端口（知识库 wsl-dual-image-selection）。")
    return 0

def cmd_export(args) -> int:
    res = distro.export_distro(args.name, args.output)
    if not res.ok:
        print(f"导出失败：{res.stderr.strip() or f'exit={res.exit_code}'}", file=sys.stderr)
        return res.exit_code or 1
    print(f"已导出：{args.output}")
    return 0

def cmd_unregister(args) -> int:
    res = distro.unregister_distro(args.name, yes=args.yes)
    if not res.ok:
        print(f"已拒绝：{res.stderr.strip()}", file=sys.stderr)
        return res.exit_code or 1
    print(f"已注销：{args.name}")
    return 0

def cmd_exec(args) -> int:
    cmd = list(args.cmd)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("exec 需要命令：okw exec <name> -- <cmd>", file=sys.stderr)
        return 2
    res = distro.exec_distro(args.name, cmd)
    if not res.ok:
        print(f"执行失败：{res.stderr.strip() or f'exit={res.exit_code}'}", file=sys.stderr)
        return res.exit_code or 1
    if res.stdout:
        print(res.stdout.rstrip("\n"))
    if res.stderr:
        print(res.stderr.rstrip("\n"), file=sys.stderr)
    return 0

def cmd_verify(args) -> int:
    try:
        default_before = distro.default_distro_name()
        report = verify.verify(args.name, default_before=default_before)
    except distro.WslError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print(verify.format_report(report))
    return 0 if report.all_passed else 1

def cmd_scaffold(args) -> int:
    if args.kind == "deb":
        try:
            files = scaffold.scaffold_deb(args.project, args.series, args.version, args.output_dir)
        except scaffold.ScaffoldError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1
        print(f"已生成 debian/ 打包骨架（{len(files)} 个文件）：")
        for f in files:
            print(f"  - {f}")
        print("下一步：编辑 control/changelog → 源码放入项目根 → dpkg-buildpackage -us -uc")
        return 0
    if args.kind == "dput":
        try:
            text, written = scaffold.scaffold_dput(args.openkylin_id, output=args.output)
        except scaffold.ScaffoldError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1
        if written:
            print(f"已写入：{written}")
        else:
            print("配置片段（可重定向到 ~/.dput.cf 或追加）：")
            print(text, end="")
        print("用法：dput okbs:~<你的ID>/ppa <source.changes>（需安装 paramiko / dput-ng）")
        return 0
    print(f"未知 scaffold 类型：{args.kind}", file=sys.stderr)
    return 2

def cmd_ref(args) -> int:
    if args.topic:
        topic = ref.get_topic(args.topic)
        if topic is None:
            print(f"未知主题：{args.topic}。可用：{', '.join(ref.list_topics())}", file=sys.stderr)
            return 2
        print(ref.format_topic(topic))
        return 0
    print("== openKylin 知识库参考主题 ==")
    for name in ref.list_topics():
        topic = ref.get_topic(name)
        assert topic is not None
        print(f"  - {name:<16} {topic.title}")
    print("用法：okw ref <主题>（如 okw ref series）")
    return 0

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
    p_ref.add_argument("topic", nargs="?", help="主题：series/wsl-troubleshoot/okbs/verify")

    # podman 子命令组：preflight / install / verify
    p_podman = sub.add_parser(
        "podman",
        help="openKylin 发行版内 rootless Podman 预检、安装与验收",
        description=(
            "三步流程：先 preflight 只读探测风险项与缺失，"
            "确认无风险后 install --yes 执行安装与 subuid/subgid 映射追加，"
            "最后 verify 验收 rootless 上下文；--smoke-image 需本地已存在镜像。"
        ),
    )
    p_podman_sub = p_podman.add_subparsers(dest="podman_cmd", metavar="<podman_cmd>")

    p_preflight = p_podman_sub.add_parser(
        "preflight",
        help="只读预检：发行版/WSL版本/openKylin身份/APT能力/包候选/subuid+subgid映射",
        description=(
            "只读预检，不触发 apt update、不写文件、不改默认发行版星标。"
            "APT 索引缺失时候选标为 UNKNOWN 并给出行动建议；"
            "映射已有冲突时 install 阶段将拒绝自动追加。"
        ),
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
            "漏 --yes 时输出三行副作用清单并中止。"
            "不修改软件源、不修改 wsl.conf、不修改默认发行版星标。"
        ),
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

    p_verify = p_podman_sub.add_parser(
        "verify",
        help="验收默认用户下 rootless Podman 上下文（默认只读，不跑容器）",
        description=(
            "默认用户身份检查：subuid/subgid 映射、unshare 是否可用、podman info --rootless。"
            "默认只读不创建/启动容器；--smoke-image 需本地已存在该镜像，不触发隐式拉取。"
        ),
    )
    p_verify.add_argument("name", help="发行版名称")
    p_verify.add_argument(
        "--smoke-image",
        metavar="LOCAL_IMAGE",
        help=(
            "存在本地的可用镜像名（REPOSITORY:TAG / 镜像 ID），"
            "若不存在将直接 FAIL 并提示先在发行版内 podman pull / podman load；"
            "严禁触发任何隐式 registry 拉取。"
        ),
    )

    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2

    if args.command == "list":
        return cmd_list(args)
    if args.command == "status":
        return cmd_status(args)
    if args.command == "import":
        return cmd_import(args)
    if args.command == "export":
        return cmd_export(args)
    if args.command == "unregister":
        return cmd_unregister(args)
    if args.command == "exec":
        return cmd_exec(args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.command == "scaffold":
        return cmd_scaffold(args)
    if args.command == "ref":
        return cmd_ref(args)
    if args.command == "podman":
        if not args.podman_cmd:
            subparsers_action = next(
                a for a in parser._subparsers._group_actions if a.dest == "command"
            )
            podman_parser = subparsers_action._name_parser_map["podman"]
            podman_parser.print_help()
            return 2
        if args.podman_cmd == "preflight":
            return podman.cmd_preflight(args)
        if args.podman_cmd == "install":
            return podman.cmd_install(args)
        if args.podman_cmd == "verify":
            return podman.cmd_verify(args)
        subparsers_action = next(
            a for a in parser._subparsers._group_actions if a.dest == "command"
        )
        podman_parser = subparsers_action._name_parser_map["podman"]
        podman_parser.print_help()
        return 2
    parser.print_help()
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
