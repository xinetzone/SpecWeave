#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent Workspace Starter 自检脚本（零第三方依赖）。

用途：
    核验「智能体工作区起步套件」的 starter 套件是否完整可用，共做三项检查：
    1) 必需文件清单齐备性（根 AGENTS.md / .agents/ 关键文件 / 8 个导览 README / LICENSE-NOTICE.md）；
    2) 根 AGENTS.md 是否含「启动协议」关键词锚点（智能体工作区发现的最低门槛）；
    3) target 内所有 Markdown 相对链接是否可达（跳过 http/https、mailto、纯锚点）。

用法：
    python scripts/verify_starter.py
        # 默认检查脚本所在产品根下的 starter/ 目录
    python scripts/verify_starter.py --target <目录>
        # 检查指定目录（例如已把 starter 拷入的自有项目根）

退出码：
    0 = 三项检查全部通过；
    1 = 存在任一失败项（目标目录不存在 / 缺失文件 / 关键词缺失 / 断链）。

依赖：仅 Python 标准库（argparse / re / sys / pathlib），兼容 Python 3.10+。
"""

import argparse
import re
import sys
from pathlib import Path

# 「启动协议」关键词锚点——与根 AGENTS.md 启动协议步骤 1.2 同源。
BOOTSTRAP_KEYWORD = "启动协议"

# 必需文件清单（相对 target 根，共 40 项；照 insight.md §2.2 与 starter/ 实际目录核对后硬编码）。
REQUIRED_FILES = (
    # 根契约与许可
    "AGENTS.md",
    "LICENSE-NOTICE.md",
    # .agents/ 入口层
    ".agents/README.md",
    ".agents/ONBOARDING.md",
    ".agents/context-routing.md",
    ".agents/global-core-rules.md",
    ".agents/capability-registry.md",
    # 核心类目代表文件
    ".agents/roles/README.md",
    ".agents/roles/developer.md",
    ".agents/roles/reviewer.md",
    ".agents/roles/tester.md",
    ".agents/rules/README.md",
    ".agents/rules/ai-coding-guidelines.md",
    ".agents/rules/content-sensitivity-precheck.md",
    ".agents/rules/fix-prevent-close-loop.md",
    ".agents/rules/spec-writing-guide.md",
    ".agents/rules/spec-creation-precheck.md",
    ".agents/protocols/README.md",
    ".agents/protocols/prompt-bootstrap.md",
    ".agents/protocols/workspace-discovery.md",
    ".agents/workflows/README.md",
    ".agents/workflows/feature-development.md",
    ".agents/workflows/code-review.md",
    ".agents/templates/README.md",
    ".agents/templates/task-template.md",
    ".agents/templates/handoff-template.md",
    ".agents/commands/README.md",
    ".agents/commands/mermaid.md",
    ".agents/checklists/README.md",
    ".agents/checklists/code-review-checklist.md",
    ".agents/skills/README.md",
    ".agents/skills/load-specweave/SKILL.md",
    # 8 个导览 README（新建态）
    ".agents/modules/README.md",
    ".agents/teams/README.md",
    ".agents/prompts/README.md",
    ".agents/tools/README.md",
    ".agents/worlds/README.md",
    ".agents/capabilities/README.md",
    ".agents/cases/README.md",
    ".agents/systems/README.md",
)

# 链接提取：匹配 ](target) 形式；先剔除围栏代码块与行内代码，避免示例代码产生误报。
FENCE_RE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"\]\(\s*([^)]*?)\s*\)")

# 明确跳过（非本地相对链接）的前缀。
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "ftp://", "data:", "file:")


def read_text(path):
    """按 UTF-8 读取文本，解码异常时以替换字符兜底，保证脚本不因单个文件编码问题中断。"""
    return path.read_text(encoding="utf-8", errors="replace")


def product_root():
    """由脚本位置（<product>/scripts/verify_starter.py）反推产品根目录。"""
    return Path(__file__).resolve().parent.parent


def default_target():
    """默认检查目标：产品根下的 starter/ 目录。"""
    return product_root() / "starter"


def check_required_files(target):
    """检查必需文件清单，返回缺失文件（相对路径字符串）列表。"""
    return [rel for rel in REQUIRED_FILES if not (target / rel).is_file()]


def check_bootstrap_keyword(target):
    """检查根 AGENTS.md 是否含「启动协议」关键词，返回 (是否通过, 说明)。"""
    agents_md = target / "AGENTS.md"
    if not agents_md.is_file():
        return False, "根 AGENTS.md 不存在，无法核验关键词锚点"
    if BOOTSTRAP_KEYWORD in read_text(agents_md):
        return True, "AGENTS.md 命中关键词「%s」" % BOOTSTRAP_KEYWORD
    return False, "AGENTS.md 未命中关键词「%s」" % BOOTSTRAP_KEYWORD


def extract_links(md_path):
    """提取单个 Markdown 文件中待核验的本地相对链接目标（已剔除外部链接与纯锚点）。"""
    text = read_text(md_path)
    text = FENCE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    links = []
    for raw in LINK_RE.findall(text):
        raw = raw.strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1].strip()
        if not raw:
            continue
        lowered = raw.lower()
        if raw.startswith("#") or lowered.startswith(SKIP_PREFIXES) or "://" in raw:
            continue
        if raw.startswith("/") or raw.startswith("\\"):
            continue
        if '"' in raw:  # 形如 (path "title")，取引号前部分
            raw = raw.split('"', 1)[0].strip()
        raw = raw.split("#", 1)[0].strip()  # 去掉锚点
        if not raw:
            continue
        if "%20" in raw:  # 兜底还原常见编码空格
            raw = raw.replace("%20", " ")
        links.append(raw)
    return links


def check_links(target):
    """检查 target 内所有 .md 的相对链接可达性。

    返回 (扫描文件数, 核验链接数, 失败项列表)，失败项为 (源文件相对路径, 原始链接) 元组。
    """
    md_files = sorted(p for p in target.rglob("*.md") if p.is_file())
    failures = []
    checked = 0
    for md_path in md_files:
        for link in extract_links(md_path):
            checked += 1
            resolved = (md_path.parent / link).resolve()
            if not resolved.exists():
                failures.append((md_path.relative_to(target).as_posix(), link))
    return len(md_files), checked, failures


def main():
    # 保证中文报告在重定向/管道场景下仍以 UTF-8 输出。
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        description="Agent Workspace Starter 自检：检查 starter 套件的文件齐备性、启动协议关键词与相对链接可达性。"
    )
    parser.add_argument(
        "--target",
        default=None,
        help="待检查目录；缺省为脚本所在产品根下的 starter/。",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve() if args.target else default_target()

    print("=== Agent Workspace Starter 自检报告 ===")
    print("目标目录：%s" % target)
    print()

    if not target.is_dir():
        print("[失败] 目标目录不存在或不是目录：%s" % target)
        print()
        print("结论：自检未通过（exit 1）")
        return 1

    exit_code = 0

    # 检查 1：必需文件齐备性
    missing = check_required_files(target)
    print("[1/3] 必需文件齐备性")
    if missing:
        exit_code = 1
        print("  失败：%d/%d 个必需文件缺失：" % (len(missing), len(REQUIRED_FILES)))
        for rel in missing:
            print("    - %s" % rel)
    else:
        print("  通过：%d/%d 个必需文件齐备。" % (len(REQUIRED_FILES), len(REQUIRED_FILES)))
    print()

    # 检查 2：启动协议关键词锚点
    passed, detail = check_bootstrap_keyword(target)
    print("[2/3] 启动协议关键词锚点")
    if passed:
        print("  通过：%s。" % detail)
    else:
        exit_code = 1
        print("  失败：%s。" % detail)
    print()

    # 检查 3：相对链接可达性
    md_count, link_count, link_failures = check_links(target)
    print("[3/3] 相对链接可达性")
    if link_failures:
        exit_code = 1
        print("  失败：扫描 %d 个 Markdown 文件，核验 %d 条相对链接，%d 条不可达："
              % (md_count, link_count, len(link_failures)))
        for src, link in link_failures:
            print("    - %s -> %s" % (src, link))
    else:
        print("  通过：扫描 %d 个 Markdown 文件，核验 %d 条相对链接，全部可达。"
              % (md_count, link_count))
    print()

    if exit_code == 0:
        print("结论：全部通过（exit 0）")
    else:
        print("结论：自检未通过（exit 1）")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())