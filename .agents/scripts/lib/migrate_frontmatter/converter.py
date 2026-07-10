import json
import logging
import shutil
from pathlib import Path
from typing import Any

from ..frontmatter import extract_all_fields, parse_frontmatter_unified
from .constants import (
    BACKUP_DIR,
    BASELINE_MANIFEST_PATH,
    TOML_FM_RE,
    TOML_STORAGE_DIR,
    YAML_FM_RE,
)
from .models import BatchResult, ConvertResult, RollbackResult, VerificationResult

logger = logging.getLogger(__name__)


def compute_toml_ref_path(md_rel_path: str) -> str:
    """计算从 .md 文件到对应外部 .toml 文件的相对路径。

    Args:
        md_rel_path: .md 文件相对于项目根的路径（使用 / 分隔），
                     如 "docs/retrospective/README.md"。

    Returns:
        从 .md 文件所在目录到 .toml 文件的相对路径（使用 / 分隔），
        如 "../../../.meta/toml/docs/retrospective/README.toml"。
    """
    parts = md_rel_path.split("/")
    depth = len(parts) - 1
    prefix = "../" * depth if depth > 0 else ""

    toml_rel_path = TOML_STORAGE_DIR + "/" + md_rel_path.rsplit(".", 1)[0] + ".toml"
    return prefix + toml_rel_path


def escape_yaml_string(value: str) -> str:
    """转义 YAML 字符串值中的双引号，并用双引号包裹。

    Args:
        value: 原始字符串值。

    Returns:
        转义并用双引号包裹的字符串，适用于 YAML 标量值。
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def generate_yaml_frontmatter(fields: dict[str, str], toml_ref: str) -> str:
    """生成 YAML frontmatter 文本（--- 包裹）。

    保留字段最小集：id（如有）、source（如有）、x-toml-ref（必须）。
    所有字符串值用双引号包裹以避免 YAML 解析错误。

    Args:
        fields: 原 TOML frontmatter 解析出的字段字典。
        toml_ref: 外部 TOML 文件的相对路径。

    Returns:
        完整的 YAML frontmatter 文本（包含 --- 标记）。
    """
    lines = ["---"]

    if "id" in fields:
        lines.append(f"id: {escape_yaml_string(fields['id'])}")

    if "source" in fields:
        lines.append(f"source: {escape_yaml_string(fields['source'])}")

    lines.append(f"x-toml-ref: {escape_yaml_string(toml_ref)}")
    lines.append("---")

    return "\n".join(lines) + "\n"


def convert_file(
    md_path: Path,
    root: Path,
    dry_run: bool = False,
    backup: bool = False,
) -> ConvertResult:
    """转换单个 TOML frontmatter 文件为 YAML+x-toml-ref 格式。

    Args:
        md_path: .md 文件绝对路径。
        root: 项目根目录绝对路径。
        dry_run: 预览模式，不写入文件。
        backup: 是否在转换前备份原文件。

    Returns:
        结果字典，包含：
        - path: 源文件相对路径
        - status: "success" | "failed" | "skipped" | "planned"
        - toml_path: 外部 TOML 文件相对路径（成功时）
        - backup_path: 备份文件相对路径（备份时）
        - error: 错误信息（失败时）
    """
    rel_path = str(md_path.relative_to(root)).replace("\\", "/")
    result: ConvertResult = {"path": rel_path, "status": "pending"}

    try:
        content = md_path.read_text(encoding="utf-8")

        yaml_match = YAML_FM_RE.match(content)
        if yaml_match and "x-toml-ref" in yaml_match.group(1):
            result["status"] = "skipped"
            result["reason"] = "already_migrated"
            return result

        toml_match = TOML_FM_RE.match(content)
        if not toml_match:
            result["status"] = "skipped"
            result["reason"] = "no_toml_frontmatter"
            return result

        toml_text = toml_match.group(1)
        fields = extract_all_fields(toml_text)
        body = content[toml_match.end():]
        if body.startswith("\n"):
            body = body[1:]

        toml_ref = compute_toml_ref_path(rel_path)
        yaml_fm = generate_yaml_frontmatter(fields, toml_ref)

        toml_rel_storage = TOML_STORAGE_DIR + "/" + rel_path.rsplit(".", 1)[0] + ".toml"
        toml_abs_path = root / toml_rel_storage
        backup_rel_path = BACKUP_DIR + "/" + rel_path
        backup_abs_path = root / backup_rel_path

        result["toml_path"] = toml_rel_storage
        result["toml_ref"] = toml_ref

        if dry_run:
            result["status"] = "planned"
            result["yaml_frontmatter"] = yaml_fm.strip()
            return result

        if backup:
            backup_abs_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md_path, backup_abs_path)
            result["backup_path"] = backup_rel_path

        toml_abs_path.parent.mkdir(parents=True, exist_ok=True)
        toml_abs_path.write_text(toml_text + "\n", encoding="utf-8")

        new_content = yaml_fm + body
        md_path.write_text(new_content, encoding="utf-8")

        result["status"] = "success"
        logger.info("转换成功: %s", rel_path)

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error("转换失败 %s: %s", rel_path, e)

    return result


def batch_convert(
    paths: list[Path],
    root: Path,
    dry_run: bool = False,
    backup: bool = False,
) -> BatchResult:
    """批量转换 TOML frontmatter 文件。

    Args:
        paths: 待转换的 .md 文件路径列表。
        root: 项目根目录。
        dry_run: 预览模式。
        backup: 是否备份。

    Returns:
        批量转换结果统计字典：
        - success: 成功转换的文件列表
        - failed: 失败的文件列表
        - skipped: 跳过的文件列表
        - warnings: 警告列表
        - total: 总文件数
    """
    results: BatchResult = {
        "success": [],
        "failed": [],
        "skipped": [],
        "warnings": [],
        "total": len(paths),
    }

    for md_path in paths:
        result = convert_file(md_path, root, dry_run=dry_run, backup=backup)
        status = result["status"]
        if status in ("success", "planned"):
            results["success"].append(result)
        elif status == "skipped":
            results["skipped"].append(result)
        elif status == "failed":
            results["failed"].append(result)

    return results


def verify_consistency(
    root: Path,
    baseline_manifest: dict[str, Any] | None = None,
) -> VerificationResult:
    """验证转换后文件与基线清单的一致性。

    使用 parse_frontmatter_unified() 解析每个迁移后的文件，
    对比字段值是否与基线清单一致（忽略 x-toml-ref 等新增字段）。

    Args:
        root: 项目根目录。
        baseline_manifest: 基线清单数据；为 None 时从 .meta/baseline-manifest.json 加载。

    Returns:
        验证结果字典：
        - passed: 通过验证的文件列表
        - failed: 验证失败的文件列表
        - errors: 错误列表
        - total_checked: 检查文件总数
    """
    if baseline_manifest is None:
        manifest_path = root / BASELINE_MANIFEST_PATH
        if not manifest_path.exists():
            return {
                "passed": [],
                "failed": [],
                "errors": [f"基线清单不存在: {manifest_path}"],
                "total_checked": 0,
            }
        with open(manifest_path, encoding="utf-8") as f:
            baseline_manifest = json.load(f)

    files_baseline = {entry["rel_path"]: entry for entry in baseline_manifest.get("files", [])}

    verification: VerificationResult = {
        "passed": [],
        "failed": [],
        "errors": [],
        "total_checked": 0,
    }

    for rel_path, baseline_entry in files_baseline.items():
        md_path = root / rel_path
        verification["total_checked"] += 1

        if not md_path.exists():
            verification["failed"].append({
                "path": rel_path,
                "reason": "file_missing",
            })
            continue

        try:
            parsed = parse_frontmatter_unified(md_path)
        except Exception as e:
            verification["failed"].append({
                "path": rel_path,
                "reason": f"parse_error: {e}",
            })
            continue

        if parsed is None:
            verification["failed"].append({
                "path": rel_path,
                "reason": "no_frontmatter_parsed",
            })
            continue

        baseline_fields = baseline_entry.get("fields", {})
        mismatches = []
        for key, expected_value in baseline_fields.items():
            actual_value = parsed.get(key)
            if actual_value is None:
                mismatches.append(f"missing field: {key}")
            elif str(actual_value) != str(expected_value):
                mismatches.append(
                    f"field {key} mismatch: expected={expected_value!r}, got={actual_value!r}"
                )

        toml_ref = parsed.get("x-toml-ref")
        if not toml_ref:
            mismatches.append("missing x-toml-ref")
        else:
            toml_path = (md_path.parent / str(toml_ref)).resolve()
            if not toml_path.exists():
                mismatches.append(f"external toml not found: {toml_ref}")

        if mismatches:
            verification["failed"].append({
                "path": rel_path,
                "reason": "; ".join(mismatches),
            })
        else:
            verification["passed"].append({"path": rel_path})

    return verification


def rollback(root: Path, backup_dir: Path | None = None) -> RollbackResult:
    """从 .meta/backup/ 恢复原始文件。

    Args:
        root: 项目根目录。
        backup_dir: 备份目录绝对路径；为 None 时使用默认 .meta/backup/。

    Returns:
        回滚结果字典：
        - restored: 成功恢复的文件列表
        - failed: 失败的文件列表
        - skipped: 跳过的文件列表（无备份）
    """
    if backup_dir is None:
        backup_dir = root / BACKUP_DIR

    result: RollbackResult = {
        "restored": [],
        "failed": [],
        "skipped": [],
    }

    if not backup_dir.exists():
        result["failed"].append({"path": str(backup_dir), "reason": "backup_dir_missing"})
        return result

    for backup_file in sorted(backup_dir.rglob("*.md")):
        rel_path = backup_file.relative_to(backup_dir)
        target_path = root / rel_path

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target_path)
            result["restored"].append({"path": str(rel_path).replace("\\", "/")})
            logger.info("已恢复: %s", rel_path)
        except Exception as e:
            result["failed"].append({
                "path": str(rel_path).replace("\\", "/"),
                "reason": str(e),
            })

    toml_storage = root / TOML_STORAGE_DIR
    if toml_storage.exists():
        try:
            shutil.rmtree(toml_storage)
            logger.info("已清理外部 TOML 目录: %s", toml_storage)
        except Exception as e:
            result["failed"].append({
                "path": TOML_STORAGE_DIR,
                "reason": f"cleanup_failed: {e}",
            })

    return result
