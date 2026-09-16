"""xmnn-runtime 客户离线交付包的厂商侧打包器（容器操作经 WSL Podman）。

经 ``invoke xmnnrt.pack`` 调用；``release/`` 目录本身保持零 Python——客户
只需要容器运行时与随包 bash/PowerShell 控制脚本。

流程：解析 wheels/ 暂存 whl 版本 → WSL 内重新 tag →
``podman save | gzip -1`` → ``gzip -t`` → 原子改名 → ``release.json`` 清单
（含镜像 id / torch 版本 / 归档 sha256 / 构建来源）。

版本语义：默认交付版本取 whl 版本（如 1.2.1.dev0，内容真值不伪造）；
GA 交付应在构建非 dev wheel 后用 ``--version 1.2.1`` 显式指定。
"""

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

# src/jpman_client/relpack.py → parents[0]=jpman_client [1]=src [2]=client
CLIENT_ROOT = Path(__file__).resolve().parents[2]
OVERLAY_DIR = CLIENT_ROOT / "overlays" / "xmnn-runtime"
RELEASE_DIR = OVERLAY_DIR / "release"
ARTIFACTS_DIR = RELEASE_DIR / "artifacts"

_WHEEL_RE = re.compile(r"xmnn-(?P<ver>.+)-cp314-cp314-linux")
_DEFAULT_DISTRO = "podman-machine-default"


@dataclass(frozen=True)
class WheelInfo:
    file: str
    version: str
    size_bytes: int


@dataclass(frozen=True)
class ImageInfo:
    ref: str
    id: str
    torch_cpu: str
    abi: str = "cp314-gil"


@dataclass(frozen=True)
class ArchiveInfo:
    file: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class ReleaseManifest:
    schema_version: str
    product: str
    version: str
    wheel: WheelInfo
    image: ImageInfo
    archive: ArchiveInfo
    built_at: str
    source_commit: str
    pack_tool: str = "jpman_client.relpack"


def resolve_wheel(wheels_dir: Path | None = None) -> WheelInfo:
    """从暂存目录选取最新 xmnn whl 并解析版本（按 mtime）。"""
    wheels_dir = wheels_dir or (OVERLAY_DIR / "wheels")
    candidates = sorted(wheels_dir.glob("xmnn-*.whl"),
                        key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(
            f"未在 {wheels_dir} 找到 xmnn-*.whl，请先 invoke xmnnrt.build"
        )
    whl = candidates[-1]
    match = _WHEEL_RE.search(whl.name)
    if not match:
        raise ValueError(f"无法从 whl 文件名解析版本：{whl.name}")
    return WheelInfo(file=whl.name, version=match.group("ver"),
                     size_bytes=whl.stat().st_size)


def to_wsl_path(path: Path) -> str:
    """Windows 绝对路径 → WSL drvfs 路径：``D:\\x`` → ``/mnt/d/x``。"""
    resolved = path.resolve()
    drive = resolved.parts[0].rstrip(":\\/").lower()
    return "/".join(["", "mnt", drive, *resolved.parts[1:]])


def wsl_distro() -> str:
    return (os.environ.get("XMNN_WSL_DISTRO")
            or os.environ.get("COMPOSE_WSL_DISTRO")
            or _DEFAULT_DISTRO)


def source_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=CLIENT_ROOT,
            capture_output=True, text=True, timeout=15,
        )
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _run_wsl_script(script_path: Path, args: list[str], timeout: int) -> str:
    """经 wsl.exe 执行脚本文件（避免 -c 多行内联脚本被 wsl 参数层转义破坏）。

    非登录 bash：避免 Fedora-WSL enterns.sh 拉起交互 shell 丢弃命令；
    所有动态值经 argv 传入，脚本内不做字符串插值。
    """
    cmd = ["wsl", "-d", wsl_distro(), "--", "bash",
           to_wsl_path(script_path), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"WSL 打包步骤失败 (exit {proc.returncode}):\n{detail}")
    return proc.stdout


# 容器侧打包脚本（参数：$1=版本 $2=归档文件名 $3=artifacts 的 WSL 路径）。
# set -o pipefail：podman save 失败时不以 gzip 的退出码为准；
# 临时文件 + gzip -t + 原子 mv 保证交付目录中不出现截断归档；
# uid 在 VM 内实测，不硬编码。
_PACK_SCRIPT = """set -euo pipefail
VER="$1"
ARCHIVE="$2"
ART="$3"
UID0="$(id -u)"
export XDG_RUNTIME_DIR="/run/user/$UID0"
mkdir -p "$XDG_RUNTIME_DIR"
SRC="localhost/xmnn-runtime:latest"
NAME="xmnn-runtime"
podman image exists "$SRC"
podman tag "$SRC" "$NAME:$VER"
mkdir -p "$ART"
rm -f "$ART"/.tmp-*.tar.gz
TMP="$ART/.tmp-$VER.tar.gz"
podman save "$NAME:$VER" | gzip -1 > "$TMP"
gzip -t "$TMP"
mv "$TMP" "$ART/$ARCHIVE"
echo "IMAGE_ID=$(podman inspect -f '{{.Id}}' "$NAME:$VER")"
echo "TORCH=$(podman inspect -f '{{index .Config.Labels "org.specweave.torch-cpu"}}' "$NAME:$VER")"
echo "SHA=$(sha256sum "$ART/$ARCHIVE" | cut -d' ' -f1)"
echo "SIZE=$(stat -c '%s' "$ART/$ARCHIVE")"
"""


def pack_release(release_version: str | None = None) -> ReleaseManifest:
    """执行完整打包，返回清单；release.json 同时落 artifacts/。"""
    wheel = resolve_wheel()
    version = release_version or wheel.version

    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    archive_name = f"xmnn-runtime-{version}.tar.gz"
    # 脚本写到 artifacts/（位于交付目录树内但被 .gitignore 忽略），执行后删除；
    # 显式 LF 换行，避免 Windows CRLF 导致 bash 解析错误。
    script_path = ARTIFACTS_DIR / f".pack-{os.getpid()}.sh"
    script_path.write_text(_PACK_SCRIPT, encoding="utf-8", newline="\n")
    try:
        output = _run_wsl_script(
            script_path,
            [version, archive_name, to_wsl_path(ARTIFACTS_DIR)],
            timeout=900,
        )
    finally:
        script_path.unlink(missing_ok=True)
    meta = dict(re.findall(r"^(IMAGE_ID|TORCH|SHA|SIZE)=(.*)$",
                           output, flags=re.MULTILINE))

    image = ImageInfo(ref=f"xmnn-runtime:{version}",
                      id=meta["IMAGE_ID"], torch_cpu=meta["TORCH"])
    archive = ArchiveInfo(file=archive_name,
                          size_bytes=int(meta["SIZE"]), sha256=meta["SHA"])
    manifest = ReleaseManifest(
        schema_version="1", product="xmnn-runtime", version=version,
        wheel=wheel, image=image, archive=archive,
        built_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        source_commit=source_commit(),
    )
    (ARTIFACTS_DIR / "release.json").write_text(
        json.dumps(asdict(manifest), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest
