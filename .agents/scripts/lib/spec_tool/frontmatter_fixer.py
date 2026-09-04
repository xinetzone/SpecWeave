"""Spec frontmatter 修复与归一化工具。

提供以下能力：
- 解析 frontmatter（YAML / TOML）
- 提取/替换 status 字段
- 为缺失 frontmatter 的文件补齐标准 YAML 头
- 将非法 status 值归一化到合法值域
- 统一的 dry-run / 日志输出模式

核心常量（合法值域、映射表）见 constants.py，
新增非法 status 只需在 STATUS_NORMALIZATION_MAP 中补充。
"""

# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from datetime import datetime
from pathlib import Path
import re
from typing import Any

from .constants import (
    VALID_STATUSES,
    STATUS_NORMALIZATION_MAP,
    YAML_FM_START_RE,
    YAML_FM_CLOSE_RE,
    TOML_FM_START_RE,
    TOML_FM_CLOSE_RE,
    STATUS_LINE_YAML_RE,
    STATUS_LINE_TOML_RE,
    H1_TITLE_RE,
)


# ============================================================
# 解析层
# ============================================================

def parse_frontmatter_info(content: str) -> dict[str, Any] | None:
    """解析 frontmatter 信息。

    返回 None 表示没有 frontmatter。
    返回 dict 字段：
      - format: 'yaml' | 'toml'
      - body_start: body 起始位置（起始分隔符之后）
      - body_end: body 结束位置（闭合分隔符之前）
      - body: frontmatter 内容文本（不含分隔符）
      - has_status: 是否包含 status 字段
    """
    stripped = content.lstrip()
    leading_ws = len(content) - len(stripped)

    # YAML
    if YAML_FM_START_RE.match(stripped):
        m = YAML_FM_START_RE.match(stripped)
        nl = "\r\n" if m.group(0).endswith("\r\n") else "\n"
        body_start = len(m.group(0)) + leading_ws
        rest = stripped[len(m.group(0)):]
        close_match = YAML_FM_CLOSE_RE.search(rest)
        if not close_match:
            return None
        body_end = leading_ws + len(m.group(0)) + close_match.start()
        body = content[body_start:body_end]
        return {
            "format": "yaml",
            "body_start": body_start,
            "body_end": body_end,
            "body": body,
            "has_status": bool(STATUS_LINE_YAML_RE.search(body)),
        }

    # TOML
    if TOML_FM_START_RE.match(stripped):
        m = TOML_FM_START_RE.match(stripped)
        nl = "\r\n" if m.group(0).endswith("\r\n") else "\n"
        body_start = len(m.group(0)) + leading_ws
        rest = stripped[len(m.group(0)):]
        close_match = TOML_FM_CLOSE_RE.search(rest)
        if not close_match:
            return None
        body_end = leading_ws + len(m.group(0)) + close_match.start()
        body = content[body_start:body_end]
        return {
            "format": "toml",
            "body_start": body_start,
            "body_end": body_end,
            "body": body,
            "has_status": bool(STATUS_LINE_TOML_RE.search(body)),
        }

    return None


def extract_status_value(body: str, fmt: str) -> str | None:
    """从 frontmatter body 中提取 status 的值（去掉引号包装）。"""
    pattern = STATUS_LINE_YAML_RE if fmt == "yaml" else STATUS_LINE_TOML_RE
    m = pattern.search(body)
    if not m:
        return None
    val = m.group(1).strip()
    # 去掉引号（单引号或双引号）
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return val


def extract_h1_title(content: str) -> str | None:
    """从 Markdown 正文提取第一个 H1 标题文本。"""
    m = H1_TITLE_RE.search(content)
    return m.group(1).strip() if m else None


def clean_title(title: str) -> str:
    """清理标题中的 YAML 特殊字符（保留双引号内的转义处理）。"""
    return title.replace('"', '\\"')


def file_mtime_date(path: Path) -> str:
    """取文件修改时间的日期字符串（YYYY-MM-DD）。"""
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


# ============================================================
# 操作层（dry-run 友好）
# ============================================================

def insert_status_into_body(body: str, fmt: str, status: str) -> str:
    """在 frontmatter body 中插入 status 行（放在第一行）。"""
    if fmt == "yaml":
        status_line = f'status: "{status}"\n'
    else:  # toml
        status_line = f'status = "{status}"\n'
    return status_line + body


def replace_status_in_body(body: str, fmt: str, new_status: str) -> str:
    """替换 frontmatter body 中的 status 值（保留原前缀和引号风格）。

    注意：正则值捕获组不包含行尾空白（用 [ \\t]*$），
    避免吃掉换行符导致闭合分隔符被粘连。
    """
    pattern = STATUS_LINE_YAML_RE if fmt == "yaml" else STATUS_LINE_TOML_RE

    def _repl(m: re.Match) -> str:  # type: ignore[name-defined]
        full = m.group(0)
        val = m.group(1)
        # 找到值在整行中的起始位置
        stripped_val = val.strip()
        val_start = full.find(stripped_val)
        prefix = full[:val_start]
        suffix = full[val_start + len(stripped_val):]
        # 保留原始引号形态：原值有引号就用引号包裹新值，否则也不加
        has_quotes = (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        )
        if has_quotes:
            quote = val[0]
            return f"{prefix}{quote}{new_status}{quote}{suffix}"
        return f'{prefix}"{new_status}"{suffix}'

    return pattern.sub(_repl, body, count=1)


def build_yaml_frontmatter(title: str, status: str, date: str | None = None) -> str:
    """构造标准 YAML frontmatter 字符串。"""
    lines = ["---", f'title: "{title}"', f'status: "{status}"']
    if date:
        lines.append(f"date: {date}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


# ============================================================
# 高层 API — 单文件处理
# ============================================================

def process_spec_file(
    spec_path: Path,
    *,
    default_status: str = "draft",
    add_date: bool = False,
    fix_missing_status: bool = False,
    normalize_status: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """处理单个 spec.md 文件的 frontmatter。

    返回结果字典，包含 action / reason / mode 等字段。
    处理优先级：
      1. 有 frontmatter + 有 status + 可归一化 → 归一化
      2. 有 frontmatter + 缺 status → 插入 status 行
      3. 无 frontmatter → 新建 frontmatter
      4. 其他 → 跳过
    """
    result: dict[str, Any] = {
        "file": str(spec_path),
        "action": "skipped",
        "reason": "",
        "mode": "",
        "old_status": "",
        "new_status": "",
        "title": "",
    }

    try:
        content = spec_path.read_text(encoding="utf-8")
    except Exception as e:
        result["action"] = "error"
        result["reason"] = f"读取失败: {e}"
        return result

    fm_info = parse_frontmatter_info(content)

    # 情况1：已有 frontmatter 且有 status
    if fm_info and fm_info["has_status"]:
        if normalize_status:
            current = extract_status_value(fm_info["body"], fm_info["format"])
            if current is None:
                result["reason"] = "已有 status 但无法解析值"
                return result
            normalized = STATUS_NORMALIZATION_MAP.get(current)
            if normalized:
                return _do_normalize(spec_path, content, fm_info, current, normalized, dry_run, result)
            if current in VALID_STATUSES:
                result["reason"] = f"已有合法 status: {current}"
                return result
            result["reason"] = f"status 值 '{current}' 不在归一化映射表中"
            return result
        result["reason"] = "已有 frontmatter 且含 status"
        return result

    # 情况2：已有 frontmatter 但缺 status
    if fm_info and not fm_info["has_status"]:
        if not fix_missing_status:
            result["reason"] = "已有 frontmatter 但缺 status（未启用 fix_missing_status）"
            return result
        return _do_insert_status(spec_path, content, fm_info, default_status, dry_run, result)

    # 情况3：无 frontmatter
    return _do_add_frontmatter(spec_path, content, default_status, add_date, dry_run, result)


def _do_normalize(
    spec_path: Path, content: str, fm_info: dict, old: str, new: str, dry_run: bool, result: dict
) -> dict:
    result["mode"] = "normalize_status"
    result["old_status"] = old
    result["new_status"] = new
    new_body = replace_status_in_body(fm_info["body"], fm_info["format"], new)
    new_content = content[: fm_info["body_start"]] + new_body + content[fm_info["body_end"]:]
    if dry_run:
        result["action"] = "would_normalize"
        result["reason"] = f"status 从 '{old}' 归一化为 '{new}'"
        return result
    try:
        spec_path.write_text(new_content, encoding="utf-8")
        result["action"] = "normalized"
        result["reason"] = f"status 已从 '{old}' 归一化为 '{new}'"
    except Exception as e:
        result["action"] = "error"
        result["reason"] = f"写入失败: {e}"
    return result


def _do_insert_status(
    spec_path: Path, content: str, fm_info: dict, status: str, dry_run: bool, result: dict
) -> dict:
    result["mode"] = "fix_status"
    result["new_status"] = status
    new_body = insert_status_into_body(fm_info["body"], fm_info["format"], status)
    new_content = content[: fm_info["body_start"]] + new_body + content[fm_info["body_end"]:]
    if dry_run:
        result["action"] = "would_add_status"
        result["reason"] = f"在 {fm_info['format'].upper()} frontmatter 中插入 status: {status}"
        return result
    try:
        spec_path.write_text(new_content, encoding="utf-8")
        result["action"] = "status_added"
        result["reason"] = f"已在 {fm_info['format'].upper()} frontmatter 中插入 status: {status}"
    except Exception as e:
        result["action"] = "error"
        result["reason"] = f"写入失败: {e}"
    return result


def _do_add_frontmatter(
    spec_path: Path, content: str, status: str, add_date: bool, dry_run: bool, result: dict
) -> dict:
    result["mode"] = "new"
    result["new_status"] = status
    raw_title = extract_h1_title(content)
    if not raw_title:
        result["action"] = "error"
        result["reason"] = "未找到 H1 标题"
        return result
    title = clean_title(raw_title)
    result["title"] = title
    date_str = file_mtime_date(spec_path) if add_date else None
    fm = build_yaml_frontmatter(title, status, date_str)
    new_content = fm + content.lstrip("\n")
    if dry_run:
        result["action"] = "would_add"
        fields = "title + status" + (" + date" if add_date else "")
        result["reason"] = f"将添加 frontmatter（{fields}）"
        return result
    try:
        spec_path.write_text(new_content, encoding="utf-8")
        result["action"] = "added"
        result["reason"] = "已添加 frontmatter"
    except Exception as e:
        result["action"] = "error"
        result["reason"] = f"写入失败: {e}"
    return result


# ============================================================
# 高层 API — 批量处理
# ============================================================

def process_spec_dir(
    spec_root: Path,
    *,
    default_status: str = "draft",
    add_date: bool = False,
    fix_missing_status: bool = False,
    normalize_status: bool = False,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """批量处理 spec_root 下所有 spec.md 文件。

    返回结果列表，每个元素是 process_spec_file 的返回值。
    """
    results = []
    if not spec_root.exists():
        return results
    for spec_md in sorted(spec_root.rglob("spec.md")):
        results.append(
            process_spec_file(
                spec_md,
                default_status=default_status,
                add_date=add_date,
                fix_missing_status=fix_missing_status,
                normalize_status=normalize_status,
                dry_run=dry_run,
            )
        )
    return results
