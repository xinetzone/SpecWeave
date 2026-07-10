"""知识库完整性自校验与自动修复模块。

提供 SHA-256 校验和计算、完整性验证、Git 历史版本恢复、
部分损坏优雅降级等核心能力。

设计原则：
- integrity 字段嵌入 frontmatter，不单独存储 sidecar 文件
- 读取时自动校验，校验失败自动触发修复流程
- 修复流程：Git 历史版本恢复 → 优雅降级提取
- 所有操作幂等，不破坏原始文件
"""

import hashlib
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def compute_checksum(content: str) -> str:
    """计算内容文本的 SHA-256 校验和。

    对 content（不含 frontmatter 的正文部分）计算 SHA-256 哈希，
    返回十六进制字符串。

    Args:
        content: 正文内容字符串。

    Returns:
        64 字符十六进制 SHA-256 哈希值。
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def verify_integrity(metadata: dict[str, str | list[str]], content: str) -> tuple[bool, str, str]:
    """验证知识条目的完整性。

    检查 metadata 中的 integrity 字段是否与当前 content 的校验和匹配。

    Args:
        metadata: 元数据字典（需包含 integrity 字段）。
        content: 正文内容字符串。

    Returns:
        (is_valid, actual_checksum, message) 元组：
        - is_valid: 校验是否通过
        - actual_checksum: 实际计算出的校验和
        - message: 校验结果描述
    """
    stored = metadata.get('integrity', '')
    actual = compute_checksum(content)

    if not stored or stored == 'unchecked':
        return True, actual, "未设置校验和，跳过完整性校验"

    if stored == actual:
        return True, actual, "完整性校验通过"

    return False, actual, f"完整性校验失败：存储的校验和 {stored[:16]}... 与计算值 {actual[:16]}... 不匹配"


def update_integrity(metadata: dict[str, str | list[str]], content: str) -> dict[str, str | list[str]]:
    """更新元数据中的 integrity 校验和字段。

    不修改原字典，返回新的元数据副本。

    Args:
        metadata: 原始元数据字典。
        content: 正文内容字符串。

    Returns:
        包含最新 integrity 校验和的元数据字典（新副本）。
    """
    result = dict(metadata)
    result['integrity'] = compute_checksum(content)
    return result


def try_repair_from_git(file_path: str | Path) -> tuple[bool, str, str]:
    """尝试从 Git 历史版本恢复损坏的文件。

    先尝试 HEAD 版本，再尝试最近的 5 个提交历史版本。

    Args:
        file_path: 损坏的文件绝对路径。

    Returns:
        (repaired, content, message) 元组：
        - repaired: 是否成功恢复
        - content: 恢复后的文件内容（成功时）
        - message: 恢复信息（成功或失败原因）
    """
    path = Path(file_path).resolve()

    try:
        # 计算相对于项目根目录的路径
        rel_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return False, "", f"文件不在项目根目录内: {path}"

    # 尝试 HEAD 版本
    try:
        result = subprocess.run(
            ['git', 'show', f'HEAD:{rel_path.as_posix()}'],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT)
        )
        if result.returncode == 0 and result.stdout:
            return True, result.stdout, "从 Git HEAD 版本恢复成功"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        logger.warning("Git HEAD 恢复失败: %s", e)

    # 尝试最近 5 个提交
    try:
        log_result = subprocess.run(
            ['git', 'log', '--oneline', '-5', '--', rel_path.as_posix()],
            capture_output=True, text=True, timeout=30,
            cwd=str(PROJECT_ROOT)
        )
        if log_result.returncode != 0 or not log_result.stdout.strip():
            return False, "", "该文件在 Git 历史中无记录"

        for line in log_result.stdout.strip().split('\n'):
            commit_hash = line.split()[0]
            show_result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{rel_path.as_posix()}'],
                capture_output=True, text=True, timeout=30,
                cwd=str(PROJECT_ROOT)
            )
            if show_result.returncode == 0 and show_result.stdout:
                return True, show_result.stdout, f"从 Git 提交 {commit_hash[:8]} 恢复成功"

        return False, "", "所有历史版本均无法恢复"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
        return False, "", f"Git 版本搜索失败: {e}"


def extract_readable_content(raw_content: str) -> tuple[str, str, str]:
    """从部分损坏的原始内容中提取可读部分。

    尝试识别并提取 frontmatter 和正文中仍然可读的内容，
    用于无法从 Git 恢复时的优雅降级场景。

    Args:
        raw_content: 损坏的原始文件内容字符串。

    Returns:
        (extracted_content, extracted_metadata_str, damage_report) 元组：
        - extracted_content: 提取出的正文内容
        - extracted_metadata_str: 提取出的 frontmatter 字符串（含 --- 标记）
        - damage_report: 损坏程度报告
    """
    lines = raw_content.split('\n')
    damage_report = ""

    # 检查 frontmatter 边界是否完整
    if lines and lines[0].strip() == '---':
        end_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_idx = i
                break

        if end_idx > 0:
            # frontmatter 完整，提取正文
            fm_lines = lines[:end_idx + 1]
            body_lines = lines[end_idx + 1:]
            body = '\n'.join(body_lines)
            fm_str = '\n'.join(fm_lines)

            # 检查正文是否含空字节（截断信号）
            if '\x00' in body:
                body = body.split('\x00')[0]
                damage_report = f"frontmatter 完整，正文在空字节处截断，可读字节数: {len(body.encode('utf-8'))}"
            else:
                body_ratio = len(body.encode('utf-8')) / max(len(raw_content.encode('utf-8')), 1)
                if body_ratio < 0.9:
                    damage_report = f"frontmatter 完整，正文可能不完整（可读比例 {body_ratio:.0%}）"
                else:
                    damage_report = "frontmatter 完整，正文无明显损坏"

            return body, fm_str, damage_report

    # frontmatter 不完整或缺失
    readable_lines = [
        line.replace('\x00', '').replace('\ufffd', '')
        for line in lines
        if line.replace('\x00', '').replace('\ufffd', '').strip()
    ]
    readable = '\n'.join(readable_lines)
    damage_report = f"frontmatter 损坏或缺失，提取了 {len(readable)} 个可读字符"
    return readable, "", damage_report