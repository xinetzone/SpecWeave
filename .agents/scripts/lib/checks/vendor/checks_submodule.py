"""vendor 子模块深度检查模块。

子模块初始化检查、工作树清洁度检查、元数据检查、分支跟踪检查等。
"""

from __future__ import annotations

from pathlib import Path

from .git_ops import _run_git
from .parser import (
    _extract_commit_from_version_entry,
    _parse_version_md_for_submodule,
)


def _check_submodule_initialized(project_root: Path, submodule_path: str) -> tuple[bool, list[str]]:
    """检查 submodule 是否已正确初始化。

    验证三项：
    1. submodule 目录存在且非空
    2. .gitmodules 中有对应条目
    3. submodule 的 .git 是文件指针（指向主仓库 .git/modules）
    """
    issues = []
    sm_dir = project_root / submodule_path

    if not sm_dir.exists():
        issues.append(f"submodule 目录不存在: {submodule_path}")
        return False, issues
    if not any(sm_dir.iterdir()):
        issues.append(f"submodule 目录为空（可能未执行 git submodule update --init）: {submodule_path}")
        return False, issues

    gm = project_root / ".gitmodules"
    if gm.exists():
        gm_content = gm.read_text(encoding="utf-8")
        if submodule_path not in gm_content:
            issues.append(f".gitmodules 中未找到 {submodule_path} 条目")

    git_marker = sm_dir / ".git"
    if not git_marker.exists():
        issues.append(f"submodule 未初始化（缺少 .git 文件指针）: {submodule_path}")
    elif not git_marker.is_file():
        issues.append(f"submodule 的 .git 不是文件指针（应为 git submodule 格式）: {submodule_path}")
    else:
        content = git_marker.read_text(encoding="utf-8").strip()
        if not content.startswith("gitdir:"):
            issues.append(f"submodule 的 .git 文件格式异常（应以 'gitdir:' 开头）: {submodule_path}")

    return len(issues) == 0, issues


def _check_submodule_clean(project_root: Path, submodule_path: str, submodule_type: str = "third_party") -> tuple[bool, list[str]]:
    """检查 submodule 工作树是否清洁，无未提交修改或冲突。

    区分两种状态：
    - 未提交的工作树修改 → 错误（所有类型）
    - 本地提交领先远程 → owned_collab 仅 INFO，third_party 警告
    - detached HEAD 状态下跳过"领先远程"检测
    """
    issues = []
    sm_dir = project_root / submodule_path

    result = _run_git(["status", "--porcelain"], cwd=sm_dir)
    if result is None:
        issues.append("ERROR: git 命令不可用，无法检查 submodule 工作树状态")
        return False, issues
    if result.returncode != 0:
        issues.append(f"ERROR: git status 执行失败: {result.stderr.strip()}")
    else:
        status_output = result.stdout.strip()
        if status_output:
            dirty_files = [l for l in status_output.splitlines() if l.strip()]
            issues.append(f"ERROR: submodule 有 {len(dirty_files)} 个未提交的修改")

    result2 = _run_git(["submodule", "status", submodule_path], cwd=project_root)
    if result2 is not None and result2.returncode == 0:
        for line in result2.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            prefix = line[0] if line else " "
            if prefix == "+":
                parts = line.split()
                issues.append(f"ERROR: submodule checkout 的 commit 与 index 不同（当前 {parts[0][1:]} 与记录不一致）")
            elif prefix == "-":
                issues.append("ERROR: submodule 未初始化")
            elif prefix == "U":
                issues.append("ERROR: submodule 存在合并冲突")
    elif result2 is not None and result2.returncode != 0:
        issues.append(f"ERROR: git submodule status 执行失败: {result2.stderr.strip()}")

    is_detached = False
    result_sym = _run_git(["symbolic-ref", "--short", "HEAD"], cwd=sm_dir)
    if result_sym is not None:
        if result_sym.returncode != 0:
            is_detached = True

    if not is_detached:
        result_ahead = _run_git(["rev-list", "@{upstream}..HEAD", "--count"], cwd=sm_dir)
        if result_ahead is not None and result_ahead.returncode == 0:
            count_str = result_ahead.stdout.strip()
            try:
                ahead_count = int(count_str)
                if ahead_count > 0:
                    if submodule_type == "owned_collab":
                        issues.append(f"INFO: submodule 有 {ahead_count} 个本地提交领先远程（请记得推送）")
                    else:
                        issues.append(f"WARNING: submodule 有 {ahead_count} 个本地提交领先远程（第三方子模块不应有本地修改）")
            except ValueError:
                pass

    has_errors = any(iss.startswith("ERROR:") for iss in issues)
    return not has_errors, issues


def _check_submodule_metadata(project_root: Path, submodule_name: str) -> tuple[bool, list[str]]:
    """检查 submodule 元数据完整性：VERSION.md 条目及 commit 一致性。"""
    issues = []
    vendor_dir = project_root / "vendor"
    version_md = vendor_dir / "VERSION.md"

    if not version_md.exists():
        issues.append("vendor/VERSION.md 不存在")
        return False, issues

    entry = _parse_version_md_for_submodule(version_md, submodule_name)
    if entry is None:
        issues.append(f"vendor/VERSION.md 中缺少 {submodule_name} 的条目")
        return False, issues

    recorded_commit = _extract_commit_from_version_entry(entry)
    if recorded_commit is None:
        issues.append(f"vendor/VERSION.md 中 {submodule_name} 条目未包含具体 commit 哈希（可能是占位符）")

    sm_path = f"vendor/{submodule_name}"
    sm_dir = project_root / sm_path
    result = _run_git(["rev-parse", "HEAD"], cwd=sm_dir)
    if result is not None and result.returncode == 0:
        actual_commit = result.stdout.strip()
        if recorded_commit and not actual_commit.startswith(recorded_commit):
            issues.append(
                f"VERSION.md 记录的 commit ({recorded_commit}) 与 submodule 当前 HEAD ({actual_commit[:8]}) 不一致"
            )

    return len(issues) == 0, issues


def _check_branch_tracking(project_root: Path, submodule_path: str) -> tuple[bool, list[str]]:
    """检查 submodule 是否配置了 branch 跟踪。

    读取 .gitmodules，检查指定 submodule 是否配置了 `branch = ` 字段。
    如果子模块类型是 owned_collab 但未配置 branch，返回警告。
    """
    from .parser import _get_submodule_type

    issues = []
    gm = project_root / ".gitmodules"
    if not gm.exists():
        return True, issues

    content = gm.read_text(encoding="utf-8")
    lines = content.splitlines()

    has_branch = False
    target_path = submodule_path.replace("\\", "/")
    current_path_matches = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[submodule"):
            current_path_matches = False
            continue
        if stripped.startswith("path") and "=" in stripped:
            pval = stripped.split("=", 1)[1].strip().replace("\\", "/")
            current_path_matches = (pval == target_path)
            continue
        if current_path_matches and stripped.startswith("branch") and "=" in stripped:
            bval = stripped.split("=", 1)[1].strip()
            if bval:
                has_branch = True

    sm_type = _get_submodule_type(project_root, Path(target_path).name)
    if sm_type == "owned_collab" and not has_branch:
        issues.append(f"WARNING: owned_collab 类型子模块未配置 branch 跟踪，建议在 .gitmodules 中添加 branch = <branch-name>")
        return False, issues

    if has_branch:
        issues.append("INFO: 已配置 branch 跟踪")
    else:
        issues.append("INFO: 未配置 branch 跟踪（third_party 类型可接受）")

    return True, issues
