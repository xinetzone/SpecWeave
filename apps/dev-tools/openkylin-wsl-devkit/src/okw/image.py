"""okw image 子命令：在 openKylin WSL 发行版内构建与验收开发容器镜像。

对齐 okw podman 组的纪律：零第三方依赖、禁止隐式拉取（仅 --pull-base 显式允许
拉取基底）、退出码 0/1/2、报告化输出。构建与验收均以发行版内 root 身份执行——
开发容器为 rootful 形态（运行契约 G3：--device /dev/fuse + --security-opt
label=disable + --cgroupns=host，严禁 --privileged）。

镜像工程见 openkylin-dev-container/（Containerfile + entrypoint + conf），
本子命令把 scripts/build.sh 与 scripts/smoke.sh 的语义封装进 okw CLI：
- build：发行版内 root podman（预装或 okw podman install）→ 基镜像本地存在
  （默认禁拉）→ 上下文同步到发行版内 /tmp → podman build --format docker
- verify：镜像本地存在（禁拉）→ 静态探针（P1-P8b，--entrypoint /bin/bash）
  → 全量启动等待 HEALTHCHECK → 服务探针（SSH/Jupyter 进程、端口、Jupyter HTTP）
"""

import base64
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from okw import distro

DEFAULT_TAG = "3.0"
DEFAULT_IMAGE = f"localhost/openkylin-dev:{DEFAULT_TAG}"
DEFAULT_BASE_IMAGE = "localhost/openkylin:3.0"

# 运行契约 G3（见 05 指南）：三个必需参数；严禁 --privileged
RUN_CONTRACT_ARGS = (
    "--device",
    "/dev/fuse",
    "--security-opt",
    "label=disable",
    "--cgroupns=host",
)
SMOKE_PULL_POLICY = "--pull=never"

# 等待 HEALTHCHECK 的轮询节奏（测试中可 monkeypatch 置 0 加速）
HEALTHCHECK_MAX_ATTEMPTS = 20
HEALTHCHECK_WAIT_SLEEP = 2

PODMAN_MISSING_HINT = (
    "发行版内未检测到 podman：openKylin WSL 发行版预装 podman，"
    "或先执行 okw podman install <name> --yes 完成安装"
)
BASE_MISSING_HINT = (
    "基镜像仅存在于本地（官方 registry 的 latest 解析为 2.0 SP1 LTS，非 3.0）："
    "请先在发行版内 podman load -i <基底归档> 或 podman pull <镜像> 导入基底，"
    "或用 --pull-base 显式允许拉取（本命令默认禁止隐式拉取）"
)
IMAGE_MISSING_HINT = (
    f"本地镜像不存在：请先在发行版内执行 okw image build <name>，"
    f"或 podman load -i <镜像归档>；verify 全程使用 {SMOKE_PULL_POLICY} 禁止隐式拉取"
)
BUILD_OK_HINT = "可用 okw image verify <name> [--image <镜像>] 验收该镜像"

# 静态探针：镜像内容物探针（与 scripts/smoke.sh 的 P1-P8 语义一致）
STATIC_PROBE_SCRIPT = """set -euo pipefail
fail() { echo "PROBE_FAIL: $1"; exit 1; }
echo "P1 sshd -t";       sshd -t || fail "sshd -t"
echo "P2 jupyter";       python3 -m jupyter --version >/dev/null 2>&1 || fail "jupyter"
echo "P3 supervisord";   supervisord --version || fail "supervisord"
echo "P4 locale";        locale -a | grep -qiE "zh_CN\\.(utf-?8)" || fail "locale zh_CN.UTF-8"
echo "P5 timezone";      [ "$(cat /etc/timezone)" = "Asia/Shanghai" ] || fail "timezone"
echo "P6 devuser-uid";   [ "$(id -u devuser)" = "1000" ] || fail "devuser uid"
echo "P7 subuid";        grep -q "^devuser:" /etc/subuid || fail "subuid"
echo "P8 podman-bins";   command -v podman >/dev/null && command -v newuidmap >/dev/null && command -v fuse-overlayfs >/dev/null || fail "podman binaries"
echo "ALL_PROBES_OK"
"""

# 服务探针：容器内进程、端口与 Jupyter HTTP 终态
SERVICE_PROBE = (
    'pgrep -x sshd >/dev/null && echo SSH_OK; '
    'pgrep -f "jupyter" >/dev/null && echo JUPYTER_OK; '
    'ss -ltn 2>/dev/null | grep -E ":22 |:8888 " && echo PORTS_OK; '
    'code=$(curl -sL -o /dev/null -w "%{http_code}" http://127.0.0.1:8888 2>/dev/null); '
    '[ "$code" = "200" ] && echo JUPYTER_HTTP_200 || echo "JUPYTER_HTTP_$code"'
)

_DRIVE_RE = re.compile(r"^([A-Za-z]):(.*)$", re.DOTALL)


def _b64(text: str) -> str:
    """把一段 shell 脚本编码为单行 ASCII token，跨 wsl.exe / podman 透传零破坏。

    实践结论：多行、含引号与 $ 的脚本经 Windows wsl.exe argv 透传会被重建破坏
    （现象：容器内探针报 'id: "devuser": 无此用户' 等假性失败）。base64 编码后
    为纯 ASCII 单 token（无空格、无引号），发行版内 bash -c "echo <b64> |
    base64 -d | bash" 解码执行即可无损传递。与「脚本文件优先」实践等价。
    """
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _decode_and_run(b64: str) -> str:
    """生成发行版内 bash -c 参数：解码并执行一段脚本（无引号问题）。"""
    return f"echo {b64} | base64 -d | bash"


def wsl_mnt_path(win_path: str) -> str:
    """Windows 绝对路径 → 发行版内 /mnt/<drive>/... 路径。

    非 Windows 盘符路径（如已 / 开头）原样规范化返回，便于作为发行版内路径透传。
    """
    p = os.path.abspath(win_path)
    m = _DRIVE_RE.match(p)
    if not m:
        return p.replace("\\", "/")
    return "/mnt/{}/{}".format(m.group(1).lower(), m.group(2).replace("\\", "/"))


def default_context_dir() -> Path:
    """openkylin-dev-container 应用目录（本包 openkylin-wsl-devkit 内）。"""
    return Path(__file__).resolve().parents[2] / "openkylin-dev-container"


@dataclass
class CheckItem:
    name: str
    status: str  # PASS | FAIL | UNKNOWN
    detail: str = ""


@dataclass
class BuildReport:
    distro_name: str
    image: str
    items: list[CheckItem] = field(default_factory=list)
    raw_log: str = ""

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.items.append(CheckItem(name=name, status=status, detail=detail))

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self.items)

    def exit_code(self) -> int:
        if self.all_passed():
            return 0
        if any(i.status == "FAIL" for i in self.items):
            return 1
        return 2  # 只有 UNKNOWN


def _distro_gate(report, distro_name: str) -> bool:
    """发行版存在 + WSL2 门；不通过返回 False（报告已记录）。"""
    try:
        d = distro.get_distro(distro_name)
    except distro.WslError as exc:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看：{exc}")
        return False
    if d is None:
        report.add("发行版存在", "FAIL", f"{distro_name} 未注册（wsl -l -v 查看）")
        return False
    if d.version != "2":
        report.add("WSL 版本", "FAIL", f"检测到 WSL{d.version}，开发容器要求 WSL2")
        return False
    report.add("WSL 版本", "PASS")
    return True


def _podman_gate(report, distro_name: str) -> bool:
    """发行版内 root 身份 podman 可用 + 后端可达门。"""
    pv = distro.exec_distro(distro_name, ["podman", "--version"], user="root")
    if not pv.ok:
        report.add(
            "podman 可用",
            "FAIL",
            f"root 身份执行 podman --version 失败："
            f"{pv.stderr.strip() or f'exit={pv.exit_code}'}；{PODMAN_MISSING_HINT}",
        )
        return False
    report.add("podman 可用", "PASS", pv.stdout.strip())
    info = distro.exec_distro(distro_name, ["podman", "info"], user="root")
    if not info.ok:
        report.add(
            "podman 后端",
            "FAIL",
            f"root 身份 podman info 失败：{info.stderr.strip() or f'exit={info.exit_code}'}",
        )
        return False
    report.add("podman 后端", "PASS")
    return True


def build_run(
    distro_name: str,
    tag: str = DEFAULT_TAG,
    base_image: str = DEFAULT_BASE_IMAGE,
    pull_base: bool = False,
    no_cache: bool = False,
    context: str | None = None,
) -> BuildReport:
    """在发行版内构建 localhost/openkylin-dev:<tag>。默认禁拉基底，仅 --pull-base 放行。"""
    image = f"localhost/openkylin-dev:{tag}"
    report = BuildReport(distro_name=distro_name, image=image)

    if not _distro_gate(report, distro_name):
        return report
    if not _podman_gate(report, distro_name):
        return report

    # 基镜像：默认只允许本地存在；显式 --pull-base 才可拉取
    exists = distro.exec_distro(
        distro_name, ["podman", "image", "exists", base_image], user="root"
    )
    if not exists.ok:
        if pull_base:
            pull = distro.exec_distro(
                distro_name, ["podman", "pull", base_image], user="root", timeout=600
            )
            if not pull.ok:
                report.add(
                    "基镜像存在",
                    "FAIL",
                    f"{base_image} 拉取失败：{pull.stderr.strip() or f'exit={pull.exit_code}'}",
                )
                return report
            report.add("基镜像存在", "PASS", f"{base_image}（--pull-base 已拉取）")
        else:
            report.add("基镜像存在", "FAIL", f"{base_image} 缺失；{BASE_MISSING_HINT}")
            return report
    else:
        report.add("基镜像存在", "PASS", base_image)

    # 构建上下文：Windows 路径（或发行版内绝对路径）→ 发行版内可读目录
    if context is not None and context.startswith("/"):
        ctx_container = context
    else:
        ctx_win = os.path.abspath(context) if context else str(default_context_dir())
        ctx_dir = Path(ctx_win)
        if not ctx_dir.is_dir() or not (ctx_dir / "Containerfile").exists():
            report.add(
                "构建上下文",
                "FAIL",
                f"{ctx_win} 不是含 Containerfile 的构建上下文目录（默认取包内 "
                "openkylin-dev-container/，可用 --context 覆盖）",
            )
            return report
        ctx_container = f"/tmp/okw-build-{int(time.time())}/ctx"
        mnt = wsl_mnt_path(ctx_win)
        prep = distro.exec_distro(
            distro_name,
            [
                "bash",
                "-lc",
                (
                    f"mkdir -p {ctx_container} && cp -a {mnt}/. {ctx_container}/ "
                    f"&& test -f {ctx_container}/Containerfile"
                ),
            ],
            user="root",
            timeout=120,
        )
        if not prep.ok:
            report.add(
                "构建上下文",
                "FAIL",
                f"上下文同步到发行版内失败：{prep.stderr.strip() or prep.stdout.strip()[:200]}",
            )
            return report
    report.add("构建上下文", "PASS", ctx_container)

    # 构建：docker 格式（OCI 静默丢 SHELL/HEALTHCHECK，见 05 指南故障排查）
    cmd = ["podman", "build", "--format", "docker", "-t", image, ctx_container]
    if no_cache:
        cmd.append("--no-cache")
    build = distro.exec_distro(distro_name, cmd, user="root", timeout=900)
    raw = "\n".join(part for part in (build.stdout, build.stderr) if part)
    report.raw_log = raw.rstrip("\n")
    if not build.ok:
        report.add(
            "镜像构建",
            "FAIL",
            f"podman build 失败（exit={build.exit_code}）：{raw.strip()[-400:]}",
        )
        return report
    report.add("镜像构建", "PASS", image)
    return report


def format_build(report: BuildReport) -> str:
    """把构建报告格式化为可读文本（构建日志原样透传 + 检查项摘要）。"""
    lines = [f"== okw image build：{report.distro_name} =="]
    if report.raw_log:
        lines.append("--- podman build 输出 ---")
        lines.append(report.raw_log)
        lines.append("--- 结束 ---")
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        lines.append(f"结论：构建成功 → {report.image}")
        lines.append(f"  下一步：{BUILD_OK_HINT}")
    else:
        fail_count = sum(1 for i in report.items if i.status == "FAIL")
        lines.append(f"结论：构建未通过（{fail_count} 项 FAIL）")
        if any("基镜像存在" == i.name and i.status == "FAIL" for i in report.items):
            lines.append(f"  {BASE_MISSING_HINT}")
    return "\n".join(lines)


@dataclass
class VerifyReport:
    distro_name: str
    image: str
    items: list[CheckItem] = field(default_factory=list)
    no_boot: bool = False

    def add(self, name: str, status: str, detail: str = "") -> None:
        self.items.append(CheckItem(name=name, status=status, detail=detail))

    def all_passed(self) -> bool:
        return all(i.status == "PASS" for i in self.items)

    def exit_code(self) -> int:
        if self.all_passed():
            return 0
        if any(i.status == "FAIL" for i in self.items):
            return 1
        return 2  # 只有 UNKNOWN


def verify_run(distro_name: str, image: str = DEFAULT_IMAGE, no_boot: bool = False) -> VerifyReport:
    """验收镜像：本地存在（禁拉）→ 静态探针 → 全量启动健康 + 服务/HTTP。

    容器操作以发行版内 root 身份执行，使用运行契约 G3 参数与 --pull=never。
    起用的临时容器在结束前必然清理（rm -f）。
    """
    report = VerifyReport(distro_name=distro_name, image=image, no_boot=no_boot)

    if not _distro_gate(report, distro_name):
        return report
    if not _podman_gate(report, distro_name):
        return report

    # 镜像本地存在（任何路径都不得拉取）
    exists = distro.exec_distro(
        distro_name, ["podman", "image", "exists", image], user="root"
    )
    if not exists.ok:
        report.add(
            "镜像存在",
            "FAIL",
            f"本地镜像 {image} 缺失（podman image exists={exists.exit_code}）；{IMAGE_MISSING_HINT}",
        )
        return report
    report.add("镜像存在", "PASS", image)

    # 静态探针：一次临时容器，--entrypoint /bin/bash；脚本 base64 单 token 透传
    probe = distro.exec_distro(
        distro_name,
        [
            "podman",
            "run",
            "--rm",
            SMOKE_PULL_POLICY,
            *RUN_CONTRACT_ARGS,
            "--entrypoint",
            "/bin/bash",
            image,
            "-c",
            _decode_and_run(_b64(STATIC_PROBE_SCRIPT)),
        ],
        user="root",
        timeout=300,
    )
    if not probe.ok:
        detail = (probe.stderr.strip() or probe.stdout.strip() or f"exit={probe.exit_code}")[:200]
        report.add(
            "静态探针",
            "FAIL",
            f"P1-P8 探针未全过：{detail}（可用 podman logs 查看容器内输出）",
        )
    else:
        report.add("静态探针", "PASS", "P1-P8 全部通过（sshd/jupyter/supervisord/locale/tz/devuser/subuid/podman 二进制）")

    if no_boot:
        return report

    # 全量启动：后台容器 + 等待 HEALTHCHECK
    ctr = distro.exec_distro(
        distro_name,
        ["podman", "run", "-d", SMOKE_PULL_POLICY, *RUN_CONTRACT_ARGS, image],
        user="root",
        timeout=300,
    )
    if not ctr.ok:
        report.add(
            "容器启动",
            "FAIL",
            f"podman run -d 失败：{ctr.stderr.strip() or f'exit={ctr.exit_code}'}",
        )
        return report
    ctr_id = (ctr.stdout.strip().splitlines()[-1] if ctr.stdout else "").strip()
    if not ctr_id:
        report.add("容器启动", "FAIL", "未取得容器 ID")
        return report

    healthy = False
    for _ in range(HEALTHCHECK_MAX_ATTEMPTS):
        time.sleep(HEALTHCHECK_WAIT_SLEEP)
        state = distro.exec_distro(
            distro_name,
            ["podman", "inspect", "-f", "{{.State.Health.Status}}", ctr_id],
            user="root",
        )
        if state.ok and state.stdout.strip() == "healthy":
            healthy = True
            break
    if not healthy:
        logs = distro.exec_distro(
            distro_name, ["podman", "logs", ctr_id], user="root"
        )
        log_tail = (logs.stdout or logs.stderr or "").strip()[-300:]
        _cleanup(distro_name, ctr_id)
        report.add(
            "容器健康",
            "FAIL",
            f"HEALTHCHECK 未达 healthy（等待 {HEALTHCHECK_MAX_ATTEMPTS} 次）；日志尾部：{log_tail or '无'}",
        )
        return report
    report.add("容器健康", "PASS")

    # 服务探针：进程 + 端口 + Jupyter HTTP 终态（经 _service_probe 单引号包裹执行）
    svc = _service_probe(distro_name, ctr_id)
    out = svc.stdout or ""
    ok_all = all(mark in out for mark in ("SSH_OK", "JUPYTER_OK", "PORTS_OK", "JUPYTER_HTTP_200"))
    if svc.ok and ok_all:
        report.add("服务探针", "PASS", "SSH_OK / JUPYTER_OK / PORTS_OK / Jupyter HTTP 200")
    else:
        detail = (svc.stderr.strip() or out.strip() or f"exit={svc.exit_code}")[:200]
        report.add(
            "服务探针",
            "FAIL",
            f"服务未全就绪：{detail}（需 SSH_OK/JUPYTER_OK/PORTS_OK/JUPYTER_HTTP_200）",
        )

    _cleanup(distro_name, ctr_id)
    report.add("容器清理", "PASS", ctr_id[:12])
    return report


def _service_probe(distro_name: str, ctr_id: str) -> distro.CmdResult:
    """以发行版内 root 身份对容器执行服务探针。

    探针含双引号与 $ 引用，跨 wsl.exe 透传易碎（见 _b64 说明）；经 base64
    单 token 解码执行，避免二次 shell 展开。
    """
    return distro.exec_distro(
        distro_name,
        [
            "podman",
            "exec",
            ctr_id,
            "bash",
            "-c",
            _decode_and_run(_b64(SERVICE_PROBE)),
        ],
        user="root",
        timeout=120,
    )


def _cleanup(distro_name: str, ctr_id: str) -> None:
    """尽力清理临时容器；失败不影响验收结论（残留容器可见于发行版 podman ps）。"""
    distro.exec_distro(distro_name, ["podman", "rm", "-f", ctr_id], user="root", timeout=120)


def format_verify(report: VerifyReport) -> str:
    """把验收报告格式化为可读文本（对齐 okw podman verify 风格）。"""
    lines = [f"== okw image verify：{report.distro_name} =="]
    max_w = max((len(i.name) for i in report.items), default=0)
    for it in report.items:
        tag = f"[{it.status:<7}]"
        lines.append(f"  {tag} {it.name:<{max_w}}  {it.detail}".rstrip())
    lines.append("")
    if report.all_passed():
        if report.no_boot:
            lines.append("结论：镜像验收通过（--no-boot，未启动服务栈）")
            lines.append("  如需全量启动验收：okw image verify <name> [--image <镜像>]")
        else:
            lines.append("结论：镜像验收全部通过（存在 + 静态探针 + 健康 + 服务/HTTP）")
    else:
        fail_count = sum(1 for i in report.items if i.status == "FAIL")
        unknown_count = sum(1 for i in report.items if i.status == "UNKNOWN")
        summary = []
        if fail_count:
            summary.append(f"{fail_count} 项 FAIL")
        if unknown_count:
            summary.append(f"{unknown_count} 项 UNKNOWN")
        lines.append("结论：验收未通过（" + " / ".join(summary) + "）")
        lines.append(f"  全程使用 {SMOKE_PULL_POLICY}，未触发任何隐式拉取；")
        lines.append("  起用的临时容器已尽力清理（残留容器可用发行版内 podman ps -a 查看）。")
    return "\n".join(lines)


def cmd_build(args) -> int:
    """CLI 入口：okw image build <发行版> [--tag] [--base-image] [--pull-base] [--no-cache] [--context]。"""
    report = build_run(
        args.name,
        tag=getattr(args, "tag", DEFAULT_TAG),
        base_image=getattr(args, "base_image", DEFAULT_BASE_IMAGE),
        pull_base=bool(getattr(args, "pull_base", False)),
        no_cache=bool(getattr(args, "no_cache", False)),
        context=getattr(args, "context", None),
    )
    print(format_build(report))
    return report.exit_code()


def cmd_verify(args) -> int:
    """CLI 入口：okw image verify <发行版> [--image] [--no-boot]。"""
    report = verify_run(
        args.name,
        image=getattr(args, "image", DEFAULT_IMAGE),
        no_boot=bool(getattr(args, "no_boot", False)),
    )
    print(format_verify(report))
    return report.exit_code()
