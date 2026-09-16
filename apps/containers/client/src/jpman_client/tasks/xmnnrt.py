"""xmnn-runtime wheel 消费栈的 podman-compose 编排任务（opt-in 命名空间）。

声明式栈：唯一事实源 ``XMNNRT_SPEC``，六任务由 make_stack_tasks 工厂生成；
唯一形态差异——build/up 在调用内核前把 wheel 暂存进 wheels/（薄封装，不复制
生命周期编排，C14）。builder/runtime 分离：xmnn.* 构建器产 whl，本栈消费
whl 装入干净运行时镜像（cp314 GIL base env + 交付内核，零源码、无工具链）。

命令：build / up / down / ps / logs / smoke + pack（客户离线交付包打包）。
栈模块禁止 import podman。
"""

import shutil
from pathlib import Path
from typing import Optional

from invoke import Context, task
from invoke.exceptions import Exit

from ..relpack import pack_release
from .overlay_core import (
    SmokeSpec, StackSpec, TaskDocs, build_image, ensure_runtime_ready,
    gates, make_stack_tasks, overlay_dir, prepare_env, up_stack,
)

_WHEEL_PATTERN = "xmnn-*.whl"

XMNNRT_SPEC = StackSpec(
    namespace="xmnnrt", project="xmnn-runtime", service="xmnnrt",
    overlay_subdir="xmnn-runtime", containerfile="Containerfile.xmnn-runtime",
    default_image_tag="localhost/xmnn-runtime:latest",
    default_base_image="localhost/jupyter-podman-rootless:latest",
    env_prefix="XMNNRT",
    docs=TaskDocs(
        build="构建 xmnn-runtime 运行时镜像（自动暂存最新 whl，构建期执行 10 项硬验证）。",
        up="渲染并启动 xmnn-runtime 栈（默认随带构建；自动从 workspace/dist 暂存最新 whl）。",
        down="停止并删除 xmnn-runtime 栈容器与网络（workspace 绑定不受影响）。",
        ps="查看 xmnn-runtime 栈服务状态。",
        logs="跟踪 xmnn-runtime 栈服务日志（Ctrl+C 退出，不影响容器运行）。",
        smoke="运行 xmnn-runtime 守卫：已装 wheel 与内置 torch CPU 的干净环境 10 项验证。",
    ),
    down_volumes_help="保留兼容签名（本栈无命名卷，参数为空操作）",
    ssh_default="2225", jupyter_default="8893",
    jupyter_banner_note="（内核：Python 3.14 (xmnn runtime)）",
    build_done_label="xmnn-runtime 运行时镜像",
    gpu_override=False, conda_mirror=False, auto_shortflags=False,
    smoke=SmokeSpec(
        python="/opt/conda/bin/python", smoke_dir="/opt/xmnnrt-smoke",
        exec_scripts=("_runtime_smoke.py",), standalone_scripts=("_runtime_smoke.py",),
        running_note="检测到运行中的栈，经 compose exec 执行运行时守卫：",
        standalone_note="栈未运行，使用一次性容器执行运行时守卫：",
        done_message="xmnn-runtime 守卫通过（10 项）",
    ),
    bridge_env_keys=(
        "XMNNRT_IMAGE_TAG", "XMNNRT_CONTAINER_NAME", "XMNNRT_WORKSPACE",
        "XMNNRT_SSH_PORT", "XMNNRT_JUPYTER_PORT",
    ),
)

TASKS = make_stack_tasks(XMNNRT_SPEC)
down, ps, logs, smoke = (TASKS[k] for k in ("down", "ps", "logs", "smoke"))

# —— wheel 暂存（构建上下文 = overlay 目录，whl 必须先进 wheels/，不入 git）——

def _wheels_dir() -> Path:
    return overlay_dir(XMNNRT_SPEC) / "wheels"


def _staged_wheels() -> list[Path]:
    return sorted(_wheels_dir().glob(_WHEEL_PATTERN))


def _latest_dist_wheel() -> Optional[Path]:
    # overlay_dir = client/overlays/xmnn-runtime → parents[1] = client 根
    wheels = sorted((overlay_dir(XMNNRT_SPEC).parents[1] / "workspace" / "dist").glob(_WHEEL_PATTERN),
                    key=lambda p: p.stat().st_mtime)
    return wheels[-1] if wheels else None


def _copy_into_stage(src: Path) -> Path:
    wheels_dir = _wheels_dir()
    wheels_dir.mkdir(parents=True, exist_ok=True)
    for old in _staged_wheels():  # 暂存区同时只留一个 whl（COPY glob 确定性）
        old.unlink()
    return shutil.copy2(src, wheels_dir / src.name)

def _ensure_wheel_staged(explicit: Optional[str]) -> Path:
    """返回暂存区 whl；无法定位时 Exit(1) 给出 xmnn.wheel 指引。"""
    if explicit:
        src = Path(explicit).expanduser().resolve()
        if not src.is_file() or not src.name.startswith("xmnn-") or not src.name.endswith(".whl"):
            print(f"[xmnnrt] ⚠ --wheel 不是有效的 xmnn whl 文件：{src}")
            raise Exit(1)
        dst = _copy_into_stage(src)
        print(f"[xmnnrt] 已暂存指定 wheel → wheels/{dst.name}")
        return dst
    dist_latest, staged = _latest_dist_wheel(), _staged_wheels()
    if dist_latest is not None:
        # 同名不等于同内容：dev0 wheel 文件名恒定，重打包只改 mtime/大小；
        # 须 name+size+mtime_ns 三者一致才跳过（copy2 保留 mtime，二次运行命中复用）。
        if (staged and staged[-1].name == dist_latest.name
                and staged[-1].stat().st_size == dist_latest.stat().st_size
                and staged[-1].stat().st_mtime_ns == dist_latest.stat().st_mtime_ns):
            print(f"[xmnnrt] wheels/ 已是最新 wheel：{staged[-1].name}（跳过拷贝）")
            return staged[-1]
        dst = _copy_into_stage(dist_latest)
        print(f"[xmnnrt] 已暂存 workspace/dist 最新 wheel → wheels/{dst.name}")
        return dst
    if staged:
        print(f"[xmnnrt] workspace/dist 未发现 wheel，复用 wheels/ 已暂存：{staged[-1].name}")
        return staged[-1]
    print("[xmnnrt] ⚠ 未找到 xmnn wheel：先在运行中的 xmnn-dev 栈执行 invoke xmnn.wheel")
    print("        （产物默认落 client/workspace/dist/），或用 --wheel <path> 显式指定。")
    raise Exit(1)

@task(
    help={
        "tag": "产出镜像标签，默认 localhost/xmnn-runtime:latest（或 .env XMNNRT_IMAGE_TAG）",
        "base-image": "基底镜像，默认 localhost/jupyter-podman-rootless:latest（须与构建器同基底）",
        "pip-mirror": "构建期 pip 镜像源：official|aliyun|tuna（默认 official）",
        "wheel": "显式指定 whl 路径；默认取 workspace/dist 最新 xmnn-*.whl（已暂存同名则复用）",
        "no-cache": "等价 podman build --no-cache（强制全量重建）",
    },
    auto_shortflags=False,
)
def build(c: Context, tag: str | None = None,
          base_image: str = XMNNRT_SPEC.default_base_image,
          pip_mirror: str = "official", wheel: str | None = None,
          no_cache: bool = False) -> None:
    """暂存 wheel 后构建 xmnn-runtime 运行时镜像（构建期 10 项硬验证）。"""
    gates(XMNNRT_SPEC)
    ensure_runtime_ready(XMNNRT_SPEC)
    _ensure_wheel_staged(wheel)
    build_image(c, XMNNRT_SPEC, tag=tag, base_image=base_image,
                pip_mirror=pip_mirror, no_cache=no_cache)

@task(
    help={"skip-build": "跳过镜像构建（默认随带构建；构建前自动暂存 workspace/dist 最新 whl）"},
    auto_shortflags=False,
)
def up(c: Context, skip_build: bool = False) -> None:
    """渲染并启动 xmnn-runtime 栈（podman-compose up -d，默认随带构建）。"""
    gates(XMNNRT_SPEC)
    ensure_runtime_ready(XMNNRT_SPEC)
    prepare_env(XMNNRT_SPEC)
    if not skip_build:
        _ensure_wheel_staged(None)
    up_stack(c, XMNNRT_SPEC, skip_build=skip_build)

@task(help={"version": "交付版本号（默认取 wheels/ whl 版本；GA 请显式指定，如 1.2.1）"},
      auto_shortflags=False)
def pack(c: Context, version: Optional[str] = None) -> None:
    """打包完全独立的客户离线交付物到 release/artifacts（tar.gz + release.json）。"""
    pack_release(release_version=version)


# 用 whl 暂存薄封装替换工厂 build/up；pack 经 TASKS 暴露为 invoke xmnnrt.pack
TASKS["build"], TASKS["up"], TASKS["pack"] = build, up, pack
