"""文件名命名规范检查（来自 check-filename-convention.py）。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

import re
import subprocess
import sys
from pathlib import Path

from constants import EXCLUDED_DIRS as BASE_EXCLUDED
from lib.project import is_non_worktree_path

RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}
ALLOWED_EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".java",
    ".yaml", ".yml", ".json", ".toml", ".xml", ".html", ".css",
    ".sh", ".bat", ".ps1", ".gitignore", ".gitattributes",
    ".sql",
    ".txt", ".csv", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".tag", ".example", ".template",
    ".ini", ".conf", ".cfg", ".log", ".lock", ".env", ".env.example",
    ".ttf", ".pth",
}
# 白名单含 ".sql" 的理由：apps/dev-tools/wechat-mp-archiver 引入运行时按路径
# 加载的 SQLite 建表脚本（db/schema.sql），SQL 是仓库新增的一类纯文本声明式
# 资产；纳入白名单不影响密钥（.env/*.key）与临时产物（.venv/__pycache__）防护。
# 白名单含 ".env" 的理由：本项目存在「产品描述/段配置」形态的 *.env（如
# apps/containers/offline-delivery/products/xmnn-runtime/product.env，九键产品定义，
# 非凭证）；而裸 ".env" 的 Path.suffix 为空串，本就不经过扩展名校验，
# 密钥保护由 .gitignore + 工作区红线（禁止提交 .env/*.key/*.pem）承担。
# 约定名：容器构建文件（Containerfile / Dockerfile 及其形态后缀，如 Containerfile.xmnn-dev）。
# Path.suffix 会把形态后缀（.xmnn-dev）误判为扩展名，故这类文件跳过扩展名检查。
CONTAINERFILE_STEMS = {"containerfile", "dockerfile"}
# 子模块 gitlink 的 index mode。gitlink 是「记录 submodule commit 的目录项」而非
# 文件，名称由上游仓库决定（如 daoapps.github.io），不受文件命名规范约束。
GITLINK_MODE = "160000"
ALLOWED_CHARS = re.compile(r'^[a-zA-Z0-9._\-/\\]+$')
NON_ASCII = re.compile(r'[^\x00-\x7F]')
CONSECUTIVE_HYPHENS = re.compile(r'--+')
STARTS_WITH_NUMBER = re.compile(r'^[/\\]?(?!(?:\d{4}-\d{2}-\d{2}-|\d{2,}[a-z]?-))\d')
EXCLUDED_DIRS = BASE_EXCLUDED | {"venv", ".chaos", "logs"}
EXCLUDED_FILES = {"报名帖_竹简悟道.md", "竹简悟道_完整版.html"}


def _warn(msg: str) -> None:
    """输出警告到 stderr，不阻塞扫描流程。"""
    print(f"[warn] {msg}", file=sys.stderr)


def _is_valid(filename: str, extension: str | None) -> tuple[bool, str]:
    if NON_ASCII.search(filename):
        return False, f"包含非 ASCII 字符（中文或其他）: {filename}"
    if ' ' in filename:
        return False, f"包含空格字符: {filename}"
    if STARTS_WITH_NUMBER.match(filename):
        return False, f"以数字开头: {filename}"
    if CONSECUTIVE_HYPHENS.search(filename):
        return False, f"包含连续连字符: {filename}"
    name_no_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    if name_no_ext.upper() in RESERVED_NAMES:
        return False, f"是 Windows 保留名称: {filename}"
    if filename.split('.', 1)[0].lower() in CONTAINERFILE_STEMS:
        return True, ""
    if extension and extension.lower() not in ALLOWED_EXTENSIONS:
        return False, f"扩展名不允许: {extension}"
    return True, ""


def _get_staged(directory: Path) -> list[Path]:
    """列出暂存区待检查的路径，剔除子模块 gitlink。

    用 `--raw` 而非 `--name-only`：raw 每行携带新旧 mode，据此识别 gitlink
    （新 mode=160000）。gitlink 指向的是子模块而非普通文件，其名称（如
    `daoapps.github.io`）不应受文件命名规范约束；否则 Path.suffix 会把
    `.io` 当扩展名拦下，正常的子模块指针 bump 也提交不了。
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--raw", "--diff-filter=ACM"],
        capture_output=True, text=True, cwd=str(directory),
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        meta, sep, path = line.partition("\t")
        if not sep or not path.strip():
            continue
        # meta 形如 ":100644 100644 0000000 abc1234 M"，第二个字段是暂存后的新 mode
        fields = meta.split()
        new_mode = fields[1] if len(fields) > 1 else ""
        if new_mode == GITLINK_MODE:
            continue
        files.append(directory / path)
    return files


def _scan(directory: Path, staged_only: bool) -> list[tuple[Path, str]]:
    violations = []
    if staged_only:
        files = _get_staged(directory)
    else:
        # rglob 遍历本身可能因文件系统异常（如 WinError 1920 文件损坏）抛出异常，
        # 必须容错处理：跳过无法访问的子目录，记录警告，继续扫描其他目录。
        files = []
        for entry in directory.rglob("*"):
            try:
                if not entry.is_file():
                    continue
                if any(ex in entry.parts for ex in EXCLUDED_DIRS):
                    continue
                if is_non_worktree_path(entry, directory):
                    continue
                files.append(entry)
            except OSError as exc:
                # 单个文件/目录访问失败不阻塞整体扫描
                _warn(f"访问失败，已跳过: {entry} ({exc})")
                continue
    for item in files:
        try:
            if item.name in EXCLUDED_FILES:
                continue
            ok, msg = _is_valid(item.name, item.suffix)
            if not ok:
                violations.append((item, msg))
        except OSError as exc:
            # 单个文件检查失败不阻塞整体扫描，记录警告而非默默 continue
            _warn(f"检查失败，已跳过: {item} ({exc})")
            continue
        except Exception as exc:
            # 兜底：捕获其他异常（如路径解析错误），避免脚本崩溃
            _warn(f"意外错误，已跳过: {item} ({exc})")
            continue
    return violations


def run(project_root: Path, args) -> int:
    directory = Path(args.directory).resolve() if getattr(args, "directory", None) else project_root
    staged = getattr(args, "staged", False)
    fix = getattr(args, "fix", False)

    print("=" * 60)
    print("文件名命名规范验证")
    print("=" * 60)
    print(f"\n扫描目录: {directory}")
    if staged:
        print("模式: 仅检查暂存区文件")

    violations = _scan(directory, staged_only=staged)
    if not violations:
        print("\n通过: 所有文件名符合规范")
        print("=" * 60)
        return 0

    print(f"\n发现问题: {len(violations)} 个违规文件")
    print("-" * 60)
    for fp, msg in violations:
        try:
            rel = fp.relative_to(project_root)
        except ValueError:
            rel = fp
        print(f"  {rel}")
        print(f"    问题: {msg}")
        if fix:
            print(f"    无法自动修复（中文名称需手动重命名为英文）")
    print("-" * 60)
    print("\n建议:")
    print("  1. 对于包含中文字符的文件，请手动重命名为英文")
    print("  2. 对于其他违规，请修正文件名")
    print("  3. 重新运行脚本验证")
    print("\n" + "=" * 60)
    return 1

