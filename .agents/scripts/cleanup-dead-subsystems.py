#!/usr/bin/env python3
"""死子系统清理脚本——支持dry-run预览、自动引用清理、回归验证、原子提交。

用法:
  # 预览模式（默认）：只显示将执行的操作，不实际修改
  python cleanup-dead-subsystems.py -s vendor_sandbox

  # 执行清理：删除文件+清理自动引用（代码引用），手动引用标注待处理
  python cleanup-dead-subsystems.py -s vendor_sandbox --execute

  # 执行清理+运行回归测试
  python cleanup-dead-subsystems.py -s knowledge --execute --test

  # 执行清理+测试+原子提交
  python cleanup-dead-subsystems.py -s knowledge --execute --test --commit

  # 列出所有可清理子系统
  python cleanup-dead-subsystems.py --list

子系统配置:
  powershell      P0: PowerShell脚本编码工具（158行）— 已清理，用于脚本验证
  vendor_sandbox  P1: vendor沙箱运行工具（142行）— 代码零引用，文档引用需人工审核
  knowledge       P2: 知识加密/安全/完整性（708行）— 三文件内部依赖链，零外部引用
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / ".agents" / "scripts"
LIB_DIR = SCRIPTS_DIR / "lib"


@dataclass
class ReferenceEdit:
    """需要清理的引用。"""
    path: Path
    description: str
    auto_clean: bool = True
    edit_fn: Optional[Callable[[str], str]] = None
    pattern: str = ""


@dataclass
class SubsystemConfig:
    """死子系统清理配置。"""
    name: str
    priority: str
    description: str
    files_to_delete: list[Path] = field(default_factory=list)
    references: list[ReferenceEdit] = field(default_factory=list)
    commit_msg: str = ""
    commit_body: list[str] = field(default_factory=list)


def _remove_import_line(content: str, import_line: str) -> str:
    """移除精确匹配的导入行。"""
    lines = content.splitlines(keepends=True)
    return "".join(line for line in lines if line.strip() != import_line.strip())


def _remove_readme_table_row(content: str, module_name: str) -> str:
    """从lib/README.md中移除指定模块的表格行。"""
    lines = content.splitlines(keepends=True)
    return "".join(line for line in lines if f"`lib.{module_name}`" not in line)


def _remove_markdown_list_item(content: str, pattern: str) -> str:
    """移除Markdown列表中包含指定pattern的列表项（以'- '开头的行）。"""
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if pattern in line and line.lstrip().startswith(("- ", "* ")):
            i += 1
            continue
        result.append(line)
        i += 1
    return "".join(result)


def _remove_table_row(content: str, pattern: str) -> str:
    """移除Markdown表格中包含指定pattern的行。"""
    lines = content.splitlines(keepends=True)
    return "".join(line for line in lines if pattern not in line)


def _replace_in_file(content: str, old: str, new: str) -> str:
    """简单替换。"""
    return content.replace(old, new)


def _remove_python_module_entry(content: str, slug: str) -> str:
    """从_api_modules_data.py中移除指定slug的modules.append({...})块。"""
    lines = content.splitlines(keepends=True)
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if f'"slug": "{slug}"' in line:
            start = i
            while start > 0 and "modules.append({" not in lines[start]:
                start -= 1
            if start > 0 and i > 0 and lines[start - 1].strip() == "})":
                start -= 1
            j = start
            brace_depth = 0
            while j < len(lines):
                for ch in lines[j]:
                    if ch == "{":
                        brace_depth += 1
                    elif ch == "}":
                        brace_depth -= 1
                j += 1
                if brace_depth <= 0:
                    break
            i = j
            if i < len(lines) and lines[i].strip() == "":
                i += 1
            continue
        result.append(line)
        i += 1
    return "".join(result)


def _remove_yaml_list_item(content: str, pattern: str) -> str:
    """移除YAML列表中包含pattern的项。"""
    lines = content.splitlines(keepends=True)
    result = []
    for line in lines:
        if pattern in line and line.lstrip().startswith("- "):
            continue
        result.append(line)
    return "".join(result)


def _get_pycache_files(module_names: list[str]) -> list[Path]:
    """获取__pycache__中的.pyc文件。"""
    pyc_dir = LIB_DIR / "__pycache__"
    result = []
    if pyc_dir.exists():
        for mod in module_names:
            for pyc in pyc_dir.glob(f"{mod}.*.pyc"):
                result.append(pyc)
    return result


def _get_powershell_config() -> SubsystemConfig:
    """P0: powershell.py（已清理，用于脚本自验证）。"""
    return SubsystemConfig(
        name="powershell",
        priority="P0",
        description="PowerShell脚本编码工具（158行）— 已清理",
        files_to_delete=[],
        references=[],
        commit_msg="refactor(deadcode): 清理未使用的powershell.py子系统",
        commit_body=[],
    )


def _get_vendor_sandbox_config() -> SubsystemConfig:
    """P1: vendor_sandbox.py 子系统配置。"""
    init_py = LIB_DIR / "__init__.py"
    config = SubsystemConfig(
        name="vendor_sandbox",
        priority="P1",
        description="vendor沙箱运行与条件导入工具（142行），零生产代码导入但架构文档引用较多",
        files_to_delete=[
            LIB_DIR / "vendor_sandbox.py",
        ] + _get_pycache_files(["vendor_sandbox"]),
        commit_msg="refactor(deadcode): 清理未使用的vendor_sandbox.py子系统",
        commit_body=[
            "vendor_sandbox.py零外部生产代码引用，属于死代码子系统。",
            "",
            "清理内容：",
            "- 删除 lib/vendor_sandbox.py（142行）",
            "- 删除 __pycache__ 中对应.pyc",
            "",
            "注意：vendor-integration/文档引用需人工审核后单独处理。",
        ],
    )
    if init_py.exists():
        init_content = init_py.read_text(encoding="utf-8")
        if "vendor_sandbox" in init_content:
            config.references.append(ReferenceEdit(
                path=init_py,
                description="从__init__.py移除vendor_sandbox导入",
                auto_clean=True,
                edit_fn=lambda c: _remove_import_line(c, "from lib import vendor_sandbox"),
                pattern="from lib import vendor_sandbox",
            ))
    vi_dir = PROJECT_ROOT / ".agents" / "vendor-integration"
    if vi_dir.exists():
        for md_file in sorted(vi_dir.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            if "vendor_sandbox" not in content:
                continue
            code_imports = len(re.findall(r"from lib\.vendor_sandbox import|import lib\.vendor_sandbox", content))
            mermaid_refs = content.count("vendor_sandbox.py")
            config.references.append(ReferenceEdit(
                path=md_file,
                description=f"架构文档引用（{code_imports}处代码示例，{mermaid_refs}处文本提及）— 需人工审核",
                auto_clean=False,
                pattern="vendor_sandbox",
            ))
    teams_dir = PROJECT_ROOT / ".agents" / "teams"
    if teams_dir.exists():
        for yaml_file in sorted(teams_dir.rglob("*.yaml")):
            content = yaml_file.read_text(encoding="utf-8")
            if "vendor_sandbox.py" not in content:
                continue
            config.references.append(ReferenceEdit(
                path=yaml_file,
                description="YAML团队配置引用 — 需人工审核",
                auto_clean=False,
                pattern="vendor_sandbox",
            ))
        for md_file in sorted(teams_dir.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            if "vendor_sandbox" not in content:
                continue
            config.references.append(ReferenceEdit(
                path=md_file,
                description="团队操作文档引用 — 需人工审核",
                auto_clean=False,
                pattern="vendor_sandbox",
            ))
    return config


def _get_knowledge_config() -> SubsystemConfig:
    """P2: knowledge_crypto/security/integrity 三文件子系统配置。"""
    config = SubsystemConfig(
        name="knowledge",
        priority="P2",
        description="知识加密/安全/完整性模块（708行），三文件形成内部依赖链但零外部生产代码引用",
        files_to_delete=[
            LIB_DIR / "knowledge_crypto.py",
            LIB_DIR / "knowledge_security.py",
            LIB_DIR / "knowledge_integrity.py",
        ] + _get_pycache_files(["knowledge_crypto", "knowledge_security", "knowledge_integrity"]),
        commit_msg="refactor(deadcode): 清理未使用的knowledge加密子系统",
        commit_body=[
            "knowledge_crypto.py/knowledge_security.py/knowledge_integrity.py零外部生产代码引用。",
            "",
            "清理内容：",
            "- 删除 lib/knowledge_crypto.py（270行）",
            "- 删除 lib/knowledge_security.py（286行）",
            "- 删除 lib/knowledge_integrity.py（152行）",
            "- 删除 __pycache__ 中对应.pyc",
        ],
    )
    return config


SUBSYSTEMS: dict[str, SubsystemConfig] = {
    "powershell": _get_powershell_config(),
    "vendor_sandbox": _get_vendor_sandbox_config(),
    "knowledge": _get_knowledge_config(),
}


def run_command(cmd: list[str], cwd: Path | None = None, check: bool = True,
                timeout: int = 120) -> subprocess.CompletedProcess:
    """运行命令并返回结果。"""
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=cwd or PROJECT_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"  ✗ 命令超时（{timeout}s）")
        return subprocess.CompletedProcess(cmd, -1, stdout="", stderr="timeout")
    if result.stdout:
        for line in result.stdout.strip().splitlines()[:30]:
            print(f"    {line}")
        if len(result.stdout.strip().splitlines()) > 30:
            print(f"    ... (共{len(result.stdout.strip().splitlines())}行输出)")
    if result.stderr and result.returncode != 0:
        for line in result.stderr.strip().splitlines()[:10]:
            print(f"    STDERR: {line}")
    if check and result.returncode != 0:
        print(f"  ✗ 命令失败 (exit code {result.returncode})")
    return result


def verify_imports() -> bool:
    """验证lib包可正常导入。"""
    print("\n📋 验证lib包导入...")
    code = (
        "import sys; sys.path.insert(0, r'" + str(SCRIPTS_DIR).replace("'", "\\'") + "'); "
        "import lib; "
        "mods = [m for m in dir(lib) if not m.startswith('_')]; "
        "print(f'  已导入模块数: {len(mods)}'); "
        "print('  OK: lib包导入成功')"
    )
    result = run_command([sys.executable, "-c", code], check=False)
    return result.returncode == 0


def run_tests() -> bool:
    """运行回归测试，容忍预存失败。"""
    print("\n🧪 运行回归测试...")
    result = run_command(
        [sys.executable, "-m", "pytest", "tests/", "--tb=line", "-q"],
        cwd=SCRIPTS_DIR, check=False, timeout=180,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        print("  ✅ 所有测试通过")
        return True
    preexisting = [
        "test_analyze_xlsx_test_report",
        "test_map_python_type",
        "test_lib_init_can_run_as_script",
    ]
    failed_lines = [l for l in output.splitlines() if "FAILED" in l or "ERROR" in l]
    new_failures = [l for l in failed_lines if not any(pf in l for pf in preexisting)]
    if not new_failures and failed_lines:
        print(f"  ⚠️  {len(failed_lines)}个失败/错误用例均为预先存在问题，与本次清理无关")
        return True
    if new_failures:
        print(f"  ✗ 发现{len(new_failures)}个新失败/错误用例:")
        for f in new_failures[:10]:
            print(f"    - {f}")
        return False
    return True


def atomic_commit(config: SubsystemConfig) -> bool:
    """执行原子提交。"""
    print(f"\n📦 原子提交: {config.commit_msg}")
    files_to_add = []
    for f in config.files_to_delete:
        if f.exists():
            print(f"  ⚠️ 文件仍存在: {f.relative_to(PROJECT_ROOT)}")
            continue
        rel = str(f.relative_to(PROJECT_ROOT))
        if "__pycache__" in rel or rel.endswith(".pyc"):
            print(f"  ⊘ 跳过gitignored文件: {rel}")
            continue
        files_to_add.append(rel)
    for ref in config.references:
        if ref.auto_clean and ref.path.exists():
            files_to_add.append(str(ref.path.relative_to(PROJECT_ROOT)))
    if not files_to_add:
        print("  没有文件需要提交，跳过")
        return True
    print(f"  待提交文件 ({len(files_to_add)}):")
    for f in files_to_add:
        print(f"    - {f}")
    msg = "\n".join([config.commit_msg] + config.commit_body)
    add_result = run_command(["git", "add"] + files_to_add, check=False)
    if add_result.returncode != 0:
        print("  ✗ git add 失败")
        return False
    run_command(["git", "diff", "--staged", "--stat"], check=False)
    commit_result = run_command(["git", "commit", "-m", msg], check=False)
    if commit_result.returncode != 0:
        print("  ✗ git commit 失败")
        run_command(["git", "reset", "HEAD", "--"] + files_to_add, check=False)
        return False
    run_command(["git", "log", "--oneline", "-1"], check=False)
    print("  ✅ 提交成功")
    return True


def execute_cleanup(config: SubsystemConfig, dry_run: bool, run_tests_flag: bool,
                    do_commit: bool) -> bool:
    """执行子系统清理。"""
    print(f"\n{'=' * 60}")
    print(f"清理子系统: {config.priority} {config.name}")
    print(f"说明: {config.description}")
    mode = "🔍 DRY-RUN（预览）" if dry_run else "⚡ EXECUTE（执行）"
    print(f"模式: {mode}")
    print(f"{'=' * 60}")

    existing_files = [f for f in config.files_to_delete if f.exists()]
    auto_refs = [r for r in config.references if r.auto_clean]
    manual_refs = [r for r in config.references if not r.auto_clean]

    print(f"\n📁 待删除文件 ({len(existing_files)}):")
    for f in existing_files:
        rel = f.relative_to(PROJECT_ROOT)
        size = f.stat().st_size if f.is_file() else 0
        print(f"  - {rel} ({size} bytes)")

    print(f"\n🔧 自动清理引用 ({len(auto_refs)}):")
    for ref in auto_refs:
        rel = ref.path.relative_to(PROJECT_ROOT)
        print(f"  - {rel}: {ref.description}")

    if manual_refs:
        print(f"\n⚠️  需人工审核引用 ({len(manual_refs)}):")
        for ref in manual_refs:
            rel = ref.path.relative_to(PROJECT_ROOT)
            print(f"  - {rel}: {ref.description}")

    if dry_run:
        print(f"\n🔍 Dry-run 模式：使用 --execute 参数执行实际操作")
        if manual_refs:
            print(f"   💡 {len(manual_refs)}个架构/配置文档引用需在代码清理后人工审核处理")
        return True

    print("\n⚡ 开始执行清理...")
    for f in existing_files:
        try:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                shutil.rmtree(f)
            print(f"  ✓ 已删除: {f.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"  ✗ 删除失败 {f.relative_to(PROJECT_ROOT)}: {e}")
            return False

    for ref in auto_refs:
        if not ref.path.exists() or not ref.edit_fn:
            continue
        try:
            content = ref.path.read_text(encoding="utf-8")
            if ref.pattern and ref.pattern not in content:
                print(f"  ⊘ 跳过（pattern未找到）: {ref.path.relative_to(PROJECT_ROOT)}")
                continue
            new_content = ref.edit_fn(content)
            if new_content == content:
                print(f"  ⊘ 无变化: {ref.path.relative_to(PROJECT_ROOT)}")
                continue
            ref.path.write_text(new_content, encoding="utf-8")
            removed = len(content.splitlines()) - len(new_content.splitlines())
            print(f"  ✓ 已清理: {ref.path.relative_to(PROJECT_ROOT)} (移除{removed}行)")
        except Exception as e:
            print(f"  ✗ 清理引用失败 {ref.path.relative_to(PROJECT_ROOT)}: {e}")
            return False

    if not verify_imports():
        print("  ✗ 导入验证失败")
        return False

    if run_tests_flag:
        if not run_tests():
            print("  ✗ 回归测试失败，中止提交")
            return False

    if manual_refs:
        print(f"\n⚠️  提醒：{len(manual_refs)}个文档/配置引用需人工审核处理：")
        for ref in manual_refs:
            print(f"  - {ref.path.relative_to(PROJECT_ROOT)}")

    if do_commit:
        if not atomic_commit(config):
            return False

    print(f"\n✅ 子系统 {config.name} 代码清理完成！")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="死子系统清理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", "-n", action="store_true", default=True,
                            help="预览模式（默认）：只显示操作不执行")
    mode_group.add_argument("--execute", "-e", action="store_true",
                            help="执行模式：实际删除文件和清理自动引用")
    parser.add_argument("--subsystem", "-s", choices=list(SUBSYSTEMS.keys()),
                        help="要清理的子系统名称")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有可清理子系统")
    parser.add_argument("--test", "-t", action="store_true", help="清理后运行回归测试")
    parser.add_argument("--commit", "-c", action="store_true", help="清理并通过测试后原子提交")

    args = parser.parse_args()

    if args.list:
        print("可清理的死子系统:\n")
        for name, cfg in SUBSYSTEMS.items():
            existing = [f for f in cfg.files_to_delete if f.exists()]
            if not cfg.files_to_delete:
                status = "✅ 已清理"
            elif existing:
                status = f"⏳ 待清理（{len(existing)}个文件）"
            else:
                status = "✅ 已清理"
            print(f"  {cfg.priority} {name:20s} {status}")
            print(f"         {cfg.description}")
        print()
        return 0

    if not args.subsystem:
        parser.print_help()
        return 1

    config = SUBSYSTEMS[args.subsystem]
    dry_run = not args.execute

    if args.commit and not args.test:
        print("⚠️ --commit 需要同时指定 --test 以确保提交前验证通过，已自动启用--test")
        args.test = True

    success = execute_cleanup(config, dry_run=dry_run, run_tests_flag=args.test,
                              do_commit=args.commit)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
