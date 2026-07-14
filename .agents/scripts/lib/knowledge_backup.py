"""知识库 Git 集成与冗余备份模块。

提供备份/恢复、知识时光机（Git 版本查询）、
大规模损坏检测与批量恢复等核心能力。

设计原则：
- 备份为完整副本，支持独立恢复
- 时光机利用 Git 历史，提供版本级知识查询
- 批量操作前先 dry-run，确保可逆
- 所有操作对 Git 仓库无副作用（仅读取，不修改 Git 状态）
"""

import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE = PROJECT_ROOT / "docs" / "knowledge"
DEFAULT_BACKUP_DIR = PROJECT_ROOT / ".backups" / "knowledge"

# ---------------------------------------------------------------------------
# 基础设施
# ---------------------------------------------------------------------------

def _run_git(args: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """运行 Git 命令，返回 (returncode, stdout, stderr)。"""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True, text=True, timeout=timeout,
            cwd=str(PROJECT_ROOT),
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Git 命令超时"
    except (subprocess.SubprocessError, OSError) as e:
        return -1, "", str(e)


def _is_git_repo() -> bool:
    """检查项目是否为 Git 仓库。"""
    return (PROJECT_ROOT / ".git").exists()


def _resolve_to_relative(file_path: str | Path) -> str:
    """将绝对路径转为相对于项目根目录的路径。"""
    path = Path(file_path).resolve()
    return path.relative_to(PROJECT_ROOT).as_posix()


# ---------------------------------------------------------------------------
# 备份与恢复
# ---------------------------------------------------------------------------

def backup_knowledge_base(
    backup_dir: str | Path | None = None,
    *,
    compress: bool = False,
    include_encrypted: bool = True,
) -> tuple[bool, str, Path | None]:
    """创建知识库的完整备份。

    将 docs/knowledge/ 目录完整复制到备份目录，
    按时间戳创建子目录。

    Args:
        backup_dir: 备份目标目录，默认为 .backups/knowledge/。
        compress: 是否压缩备份（暂未实现）。
        include_encrypted: 是否包含加密条目。

    Returns:
        (success, message, backup_path) 元组。
    """
    if backup_dir is None:
        backup_dir = DEFAULT_BACKUP_DIR

    target = Path(backup_dir)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = target / timestamp

    if not KNOWLEDGE_BASE.exists():
        return False, f"知识库目录不存在: {KNOWLEDGE_BASE}", None

    try:
        backup_path.mkdir(parents=True, exist_ok=True)

        # 复制所有文件和目录
        total_files = 0
        for root, dirs, files in os.walk(str(KNOWLEDGE_BASE)):
            # 跳过 .git 目录
            dirs[:] = [d for d in dirs if d != '.git']

            rel_root = Path(root).relative_to(KNOWLEDGE_BASE)
            dest_root = backup_path / rel_root
            dest_root.mkdir(parents=True, exist_ok=True)

            for f in files:
                if not include_encrypted and f.endswith('.encrypted.md'):
                    continue
                src_file = Path(root) / f
                shutil.copy2(src_file, dest_root / f)
                total_files += 1

        # 记录备份元数据
        meta_file = backup_path / ".backup_meta.json"
        import json
        meta = {
            "timestamp": timestamp,
            "source": str(KNOWLEDGE_BASE),
            "total_files": total_files,
            "includes_encrypted": include_encrypted,
        }
        meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

        return True, f"备份完成: {total_files} 个文件 → {backup_path}", backup_path

    except OSError as e:
        return False, f"备份失败: {e.strerror or str(e)}", None


def restore_from_backup(
    backup_path: str | Path,
    *,
    target_dir: str | Path | None = None,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """从备份恢复知识库。

    Args:
        backup_path: 备份目录路径。
        target_dir: 恢复目标目录，默认为 docs/knowledge/。
        dry_run: 仅预览，不实际修改文件。

    Returns:
        (success, message) 元组。
    """
    src = Path(backup_path)
    if target_dir is None:
        target_dir = KNOWLEDGE_BASE
    dest = Path(target_dir)

    if not src.exists():
        return False, f"备份目录不存在: {src}"

    meta_file = src / ".backup_meta.json"
    meta_info = ""
    if meta_file.exists():
        import json
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        meta_info = f"（{meta.get('total_files', '?')} 个文件，{meta.get('timestamp', '?')}）"

    if dry_run:
        # 预览：列出所有文件差异
        src_files = set()
        for root, _, files in os.walk(str(src)):
            for f in files:
                if f == '.backup_meta.json':
                    continue
                rel = Path(root).relative_to(src) / f
                src_files.add(rel.as_posix())

        return True, (
            f"恢复预览 {meta_info}: {len(src_files)} 个文件将恢复到 {dest}"
        )

    try:
        if dest.exists():
            shutil.rmtree(dest)

        shutil.copytree(src, dest, ignore=shutil.ignore_patterns('.backup_meta.json'))

        return True, f"恢复完成 {meta_info}: {dest}"

    except OSError as e:
        return False, f"恢复失败: {e.strerror or str(e)}"


# ---------------------------------------------------------------------------
# 知识时光机
# ---------------------------------------------------------------------------

def list_knowledge_history(
    file_path: str | Path,
    max_commits: int = 20,
) -> tuple[bool, list[dict], str]:
    """列出知识条目的 Git 历史版本。

    Args:
        file_path: 知识条目文件路径（绝对或相对于项目根目录）。
        max_commits: 最大返回的提交数量。

    Returns:
        (success, commits, message) 元组。
        commits 列表中每个元素包含: hash, date, author, message, available。
    """
    if not _is_git_repo():
        return False, [], "项目不是 Git 仓库"

    path = Path(file_path)
    try:
        if path.is_absolute():
            rel_path = _resolve_to_relative(path)
        else:
            rel_path = str(path)
    except ValueError:
        return False, [], f"文件不在项目根目录内: {path}"

    returncode, stdout, stderr = _run_git([
        'log', f'--max-count={max_commits}', '--format=%H|%aI|%an|%s', '--', rel_path,
    ])
    if returncode != 0:
        return False, [], f"Git 历史查询失败: {stderr}"

    commits = []
    for line in stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('|', 3)
        if len(parts) >= 4:
            commits.append({
                'hash': parts[0],
                'date': parts[1],
                'author': parts[2],
                'message': parts[3],
                'available': True,
            })

    return True, commits, f"找到 {len(commits)} 个历史版本"


def get_knowledge_at_version(
    file_path: str | Path,
    commit_hash: str,
) -> tuple[bool, str, str]:
    """获取指定 Git 版本的知识条目内容。

    Args:
        file_path: 知识条目文件路径。
        commit_hash: Git 提交哈希。

    Returns:
        (success, content, message) 元组。
    """
    if not _is_git_repo():
        return False, "", "项目不是 Git 仓库"

    path = Path(file_path)
    try:
        if path.is_absolute():
            rel_path = _resolve_to_relative(path)
        else:
            rel_path = str(path)
    except ValueError:
        return False, "", f"文件不在项目根目录内: {path}"

    returncode, stdout, stderr = _run_git([
        'show', f'{commit_hash}:{rel_path}',
    ])
    if returncode != 0:
        return False, "", f"版本检出失败: {stderr}"

    return True, stdout, f"成功检出 {commit_hash[:8]} 版本"


def compare_knowledge_versions(
    file_path: str | Path,
    old_commit: str,
    new_commit: str,
) -> tuple[bool, str, str]:
    """比较两个版本的知识条目差异。

    Args:
        file_path: 知识条目文件路径。
        old_commit: 旧版本提交哈希。
        new_commit: 新版本提交哈希。

    Returns:
        (success, diff, message) 元组。
    """
    path = Path(file_path)
    try:
        if path.is_absolute():
            rel_path = _resolve_to_relative(path)
        else:
            rel_path = str(path)
    except ValueError:
        return False, "", f"文件不在项目根目录内: {path}"

    returncode, stdout, stderr = _run_git([
        'diff', old_commit, new_commit, '--', rel_path,
    ])
    if returncode != 0:
        return False, "", f"版本比较失败: {stderr}"

    if not stdout.strip():
        return True, stdout, "两个版本内容相同"

    return True, stdout, "版本差异如下"


# ---------------------------------------------------------------------------
# 大规模损坏检测与批量恢复
# ---------------------------------------------------------------------------

def detect_bulk_damage(
    knowledge_base_dir: str | Path | None = None,
) -> tuple[bool, list[dict], str]:
    """扫描知识库，检测所有损坏的条目。

    对每个 Markdown 文件进行完整性校验，列出所有损坏的条目。

    Args:
        knowledge_base_dir: 知识库目录，默认 docs/knowledge/。

    Returns:
        (success, damaged_entries, message) 元组。
        damaged_entries 列表中每个元素包含: file, checksum, error。
    """
    if knowledge_base_dir is None:
        knowledge_base_dir = KNOWLEDGE_BASE

    base = Path(knowledge_base_dir)
    if not base.exists():
        return False, [], f"知识库目录不存在: {base}"

    from .frontmatter import split_frontmatter_and_content
    from .knowledge_integrity import verify_integrity

    damaged = []
    total = 0
    checked = 0

    for md_file in base.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        if "templates" in md_file.parts:
            continue
        total += 1

        try:
            raw = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            damaged.append({
                "file": md_file.relative_to(base).as_posix(),
                "checksum": "N/A",
                "error": "无法读取文件",
            })
            continue

        metadata, content = split_frontmatter_and_content(raw, base_dir=md_file.parent)
        if metadata is None:
            metadata = {}
        content = content.lstrip('\n')
        valid, checksum, msg = verify_integrity(metadata, content)

        checked += 1
        if not valid:
            damaged.append({
                "file": md_file.relative_to(base).as_posix(),
                "checksum": checksum,
                "error": msg,
            })

    if not damaged:
        return True, [], f"扫描完成: {checked}/{total} 个条目，全部通过校验"

    return True, damaged, (
        f"扫描完成: {checked}/{total} 个条目，"
        f"发现 {len(damaged)} 个损坏条目"
    )


def bulk_repair(
    knowledge_base_dir: str | Path | None = None,
    *,
    dry_run: bool = False,
) -> tuple[bool, list[dict], str]:
    """批量修复损坏的知识条目。

    先检测损坏条目，再尝试从 Git 恢复。

    Args:
        knowledge_base_dir: 知识库目录。
        dry_run: 仅检测，不实际修复。

    Returns:
        (success, repair_results, message) 元组。
    """
    if knowledge_base_dir is None:
        knowledge_base_dir = KNOWLEDGE_BASE

    ok, damaged, msg = detect_bulk_damage(knowledge_base_dir)
    if not ok:
        return False, [], msg

    if not damaged:
        return True, [], f"无需修复: {msg}"

    if dry_run:
        return True, [
            {**d, "repair_status": "dry_run"}
            for d in damaged
        ], f"检测到 {len(damaged)} 个损坏条目（dry-run 模式，未实际修复）"

    from .knowledge_integrity import try_repair_from_git

    base = Path(knowledge_base_dir)
    results = []

    for d in damaged:
        file_path = base / d["file"]
        repaired, content, repair_msg = try_repair_from_git(file_path)

        if repaired:
            try:
                file_path.write_text(content, encoding="utf-8")
                results.append({**d, "repair_status": "repaired", "repair_source": repair_msg})
            except OSError as e:
                results.append({
                    **d,
                    "repair_status": "write_failed",
                    "repair_error": f"写入失败: {e.strerror or str(e)}",
                })
        else:
            results.append({**d, "repair_status": "unrepairable", "repair_error": repair_msg})

    repaired_count = sum(1 for r in results if r["repair_status"] == "repaired")
    failed_count = len(results) - repaired_count

    return True, results, (
        f"批量修复完成: {repaired_count} 个已修复, {failed_count} 个无法修复"
    )


# ---------------------------------------------------------------------------
# 变更前保护
# ---------------------------------------------------------------------------

def pre_change_check() -> tuple[bool, dict, str]:
    """在修改知识库前执行预检查。

    检查 Git 工作区状态、是否有未提交的变更，
    确保变更可追溯。

    Returns:
        (safe_to_proceed, status_info, message) 元组。
        status_info 包含: has_git, is_clean, pending_changes, last_commit。
    """
    info = {
        "has_git": _is_git_repo(),
        "is_clean": True,
        "pending_changes": [],
        "last_commit": "",
    }

    if not info["has_git"]:
        return True, info, "项目不是 Git 仓库，跳过 Git 检查"

    # 检查工作区状态
    returncode, stdout, stderr = _run_git(['status', '--porcelain'])
    if returncode != 0:
        return False, info, f"Git 状态检查失败: {stderr}"

    if stdout.strip():
        info["is_clean"] = False
        info["pending_changes"] = [
            line.strip() for line in stdout.strip().split('\n')
        ]

    # 获取最近一次提交
    returncode, stdout, stderr = _run_git(['log', '-1', '--format=%H|%aI|%s'])
    if returncode == 0 and stdout.strip():
        info["last_commit"] = stdout.strip()

    if info["pending_changes"]:
        change_count = len(info["pending_changes"])
        return False, info, (
            f"工作区有 {change_count} 个未提交的变更，"
            f"建议先提交或暂存后再操作"
        )

    return True, info, "工作区干净，可以安全操作"


def list_all_backups(
    backup_dir: str | Path | None = None,
) -> tuple[bool, list[dict], str]:
    """列出所有备份。

    Args:
        backup_dir: 备份目录，默认为 .backups/knowledge/。

    Returns:
        (success, backups, message) 元组。
    """
    if backup_dir is None:
        backup_dir = DEFAULT_BACKUP_DIR

    target = Path(backup_dir)
    if not target.exists():
        return True, [], "备份目录不存在，无备份记录"

    backups = []
    for entry in sorted(target.iterdir(), reverse=True):
        if not entry.is_dir():
            continue

        meta = {}
        meta_file = entry / ".backup_meta.json"
        if meta_file.exists():
            import json
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        backups.append({
            "path": str(entry),
            "name": entry.name,
            "timestamp": meta.get("timestamp", entry.name),
            "total_files": meta.get("total_files", "?"),
        })

    return True, backups, f"找到 {len(backups)} 个备份"