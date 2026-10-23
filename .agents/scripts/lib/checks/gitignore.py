"""Git 忽略规则检查（来自 check-gitignore.py）。

判定分两层：

1. .gitignore 必需规则覆盖——读 .gitignore 文本，瞬时完成。
2. 版本控制索引中的临时依赖——只读 .git/index，不触碰工作区。

第 2 层为何改为索引口径
----------------------
旧实现以 `git status --porcelain` 的输出为判据，并逐行调用 `git check-ignore` 复核：

- 代价过高：`git status` 需对全部跟踪文件逐个 lstat 以判定修改，并递归进入各子模块
  工作树。在 sshfs 通道实测（17,625 个跟踪文件 / 21 个子模块）：完整变体 377 秒未收敛，
  `--ignore-submodules=all` 冷索引 136 秒、热索引 21 秒，无法用于提交前自检。
- 收益为零：`git check-ignore` 默认查索引，已跟踪文件恒判为「未忽略」；而真正被忽略的
  路径又不会出现在 `git status --porcelain` 输出中（未跟踪且被忽略的文件不列出）。
  两端相交恒为空，该步实为恒真命题，却要付出全量工作区扫描的代价。

新口径直接读索引：列出全部跟踪条目（`git ls-files -s -z`，实测 0.6 秒），筛出命中临时
依赖路径且非 gitlink（mode 160000）的条目，再用 `git check-ignore --no-index` 做纯规则
匹配，识别「已进入版本控制、却仍被 .gitignore 规则覆盖」的临时依赖。新口径是旧口径的
严格超集（旧口径因索引遮蔽而永远漏报已跟踪项），且耗时与工作区状态无关。
"""

# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import subprocess
from pathlib import Path

from constants import REQUIRED_RULES, TEMP_PATHS
from lib.cli import print_header

# git 子进程超时（秒）：高延迟挂载（sshfs/9p）上兜底，避免无限期挂起
GIT_TIMEOUT = 60

# gitlink 在索引中的模式（子模块指针），非普通文件，不参与临时依赖判定
GITLINK_MODE = "160000"


def _check_rules(gitignore_path: Path) -> list[str]:
    if not gitignore_path.exists():
        return [f"错误: .gitignore 文件不存在于 {gitignore_path}"]
    content = gitignore_path.read_text(encoding="utf-8")
    return [rule for rule in REQUIRED_RULES if rule not in content]


def _load_index_entries(project_root: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """读取 git 索引中的全部跟踪条目。

    Returns:
        (entries, errors)：entries 为 [(mode, path), ...]，mode 取自索引
        （"100644" 表示普通文件，"160000" 表示 gitlink）；errors 非空表示读取失败。

    只读 .git/index，不访问工作区，耗时与跟踪文件数量基本无关（实测 0.6 秒 / 17,625 条）。
    """
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "ls-files", "-s", "-z"],
            capture_output=True, cwd=str(project_root), timeout=GIT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return [], [f"错误: git ls-files 执行超时（>{GIT_TIMEOUT}s）"]
    except FileNotFoundError:
        return [], ["错误: git 命令未找到，请确保 git 已安装并添加到 PATH"]
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return [], [f"错误: git ls-files 执行失败: {stderr}"]

    entries: list[tuple[str, str]] = []
    for record in result.stdout.decode("utf-8", errors="replace").split("\0"):
        if not record:
            continue
        meta, _, path = record.partition("\t")
        fields = meta.split()
        if len(fields) < 3 or not path:
            continue
        entries.append((fields[0], path))
    return entries, []


def _pick_temp_candidates(entries: list[tuple[str, str]]) -> list[str]:
    """筛出命中临时依赖路径、且不是 gitlink 的跟踪路径。"""
    return [
        path
        for mode, path in entries
        if mode != GITLINK_MODE and any(temp in path for temp in TEMP_PATHS)
    ]


def _match_ignore_rules(project_root: Path, paths: list[str]) -> tuple[list[str], list[str]]:
    """按 .gitignore 规则（绕开索引遮蔽）判定哪些路径本应被忽略。

    --no-index 是关键：默认模式下 git 会查索引，已跟踪文件恒判为「未忽略」，
    从而无法识别「已进入版本控制、却仍被忽略规则覆盖」的临时依赖。
    """
    if not paths:
        return [], []
    payload = ("\0".join(paths) + "\0").encode("utf-8")
    try:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin", "-z"],
            input=payload, capture_output=True, cwd=str(project_root), timeout=GIT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return [], [f"错误: git check-ignore 执行超时（>{GIT_TIMEOUT}s）"]
    except FileNotFoundError:
        return [], ["错误: git 命令未找到，请确保 git 已安装并添加到 PATH"]
    if result.returncode not in (0, 1):
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        return [], [f"错误: git check-ignore 执行失败: {stderr}"]
    matched = [p for p in result.stdout.decode("utf-8", errors="replace").split("\0") if p]
    return matched, []


def _check_tracked_temp_deps(project_root: Path) -> list[str]:
    """检查版本控制索引中是否存在本应被忽略的临时依赖。

    Returns:
        违规说明列表；为空表示通过。元素以「错误: 」开头者为执行失败而非违规。
    """
    entries, errors = _load_index_entries(project_root)
    if errors:
        return errors
    candidates = _pick_temp_candidates(entries)
    if not candidates:
        return []
    matched, errors = _match_ignore_rules(project_root, candidates)
    if errors:
        return errors
    return [f"已进入版本控制但仍被 .gitignore 规则覆盖: {path}" for path in matched]


def run(project_root: Path, args) -> int:
    gitignore_path = project_root / ".gitignore"
    print_header("Git 忽略规则验证")

    print("\n1. 检查 .gitignore 规则覆盖...")
    missing = _check_rules(gitignore_path)
    if missing:
        print(f"   失败: 缺少以下规则: {', '.join(missing)}")
        return 1
    print(f"   通过: 所有 {len(REQUIRED_RULES)} 条必需规则均已覆盖")

    print("\n2. 检查版本控制索引中的临时依赖...")
    violations = _check_tracked_temp_deps(project_root)
    if violations:
        print("   失败: 版本控制索引中存在本应被忽略的临时依赖:")
        for v in violations:
            print(f"     - {v}")
        return 1
    print("   通过: 版本控制索引中不存在临时依赖路径")

    print()
    print_header("验证通过: 所有临时依赖路径已被 .gitignore 覆盖")
    return 0
