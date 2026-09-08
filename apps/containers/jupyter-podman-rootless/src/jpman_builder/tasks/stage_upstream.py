"""构建前自动 stage 上游 submodule 源树。

三个上游仓库（podman-compose / podman-py / toolbox）以 git submodule 形式注册在
SpecWeave 根工作区的 ``vendor/`` 下，位于镜像构建上下文之外。容器镜像在构建时需要
在上下文中通过 ``upstream/<name>`` 引用它们的源树（本地安装/构建），因此本模块在
每次镜像构建前把三份源树的工作树内容复制到 ``<project_root>/upstream/<name>``
（该目录已被应用的 ``.gitignore`` 忽略，不进入版本控制）。
"""
from __future__ import annotations

import shutil
from pathlib import Path

#: 需要 stage 的上游仓库名（对应 SpecWeave 根 ``vendor/<name>`` 目录）
UPSTREAM_NAMES: tuple[str, ...] = ("podman-compose", "podman-py", "toolbox")

#: 复制时忽略的条目（git 元数据、Python/测试缓存等，避免污染构建上下文）
_IGNORED_NAMES = shutil.ignore_patterns(
    ".git",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
)


def _find_workspace_root(project_root: Path) -> Path:
    """从 ``project_root`` 逐级向上查找含 ``.gitmodules`` 的工作区根（SpecWeave root）。"""
    current = Path(project_root).resolve()
    while True:
        if (current / ".gitmodules").is_file():
            return current
        if current.parent == current:  # 已到文件系统根
            break
        current = current.parent
    raise FileNotFoundError(
        f"未找到包含 .gitmodules 的工作区根目录（从 {project_root} 向上查找失败）"
    )


def _stage_one(name: str, workspace_root: Path, dst: Path) -> None:
    """复制单个上游源树；幂等（已存在目标先清空）；源缺失/为空时抛带修复提示的异常。"""
    src = workspace_root / "vendor" / name
    if not src.is_dir() or not any(src.iterdir()):
        raise FileNotFoundError(
            f"上游源树缺失或为空: {src}（submodule 可能未初始化）。"
            f"请先在 SpecWeave 根目录执行: git submodule update --init vendor/{name}"
        )

    if dst.exists():
        print(f"[INFO][stage] 清理旧副本: {dst}")
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"[INFO][stage] 复制源树: {src}")
    print(f"[INFO][stage]      -> {dst}")
    shutil.copytree(src, dst, ignore=_IGNORED_NAMES)


def stage_upstream_sources(project_root: Path) -> None:
    """把工作区 ``vendor/`` 下三个上游源树复制到 ``<project_root>/upstream/<name>``。

    Args:
        project_root: 应用（镜像构建上下文）根目录，``upstream/`` 将创建在其下。

    Raises:
        FileNotFoundError: 找不到含 ``.gitmodules`` 的工作区根，或上游源树缺失/为空
            （submodule 未 init），消息内含修复提示。
        OSError: 清理旧副本或复制源树失败（原样抛出）。
    """
    project_root = Path(project_root).resolve()
    workspace_root = _find_workspace_root(project_root)
    print(f"[INFO][stage] 工作区根目录: {workspace_root}")

    upstream_root = project_root / "upstream"
    print(f"[INFO][stage] stage 目标目录: {upstream_root}")
    for name in UPSTREAM_NAMES:
        _stage_one(name, workspace_root, upstream_root / name)
    print(f"[INFO][stage] 完成: {', '.join(UPSTREAM_NAMES)} 已复制到 {upstream_root}")
