"""mdi — Markdown Interface 文档解析与代码生成工具包。

提供 MDI 文档的解析、验证、代码生成、版本对比能力。

快速开始::

    import mdi

    # 解析MDI文档
    doc = mdi.parse("skill.md")

    # 验证文档合规性
    report = mdi.validate("skill.md")
    if report.errors:
        for err in report.errors:
            print(f"ERROR: {err.message}")

    # 生成代码
    gen = mdi.MDIGenerator(lang="python")
    files = gen.generate(doc, output_dir="./output")

    # 版本对比
    diff = mdi.diff_files("v1.md", "v2.md")
    print(diff.format_text())
    print(f"建议版本: {diff.suggest_version_bump()}")
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import (
    MDIDocument,
    Interface,
    Parameter,
    Response,
    ErrorCode,
    CodeBlock,
    CheckItem,
    DecisionNode,
    Section,
    Warning,
)
from mdi.parser import MDIParser
from mdi.validator import MDIValidator, ValidationReport
from mdi.generator import MDIGenerator
from mdi.generators import (
    BaseGenerator,
    PythonGenerator,
    TypeScriptGenerator,
    OpenAPIGenerator,
    MCPGenerator,
    MarkdownGenerator,
    CLIGenerator,
)
from mdi.versioning import (
    DiffResult,
    ChangeType,
    ChangeSeverity,
    diff_documents,
    diff_files,
    diff_strings,
    get_version_bump_recommendation,
    VERSIONING_BEST_PRACTICES,
)


def parse(path: str | Path) -> MDIDocument:
    """解析一个MDI文件，返回MDIDocument对象。

    Args:
        path: MDI文件路径（Markdown格式）。

    Returns:
        解析后的MDIDocument对象。

    Raises:
        FileNotFoundError: 文件不存在时抛出。
    """
    return MDIParser().parse_file(Path(path))


def validate(
    path: str | Path,
    profile_type: str = "auto",
) -> ValidationReport:
    """验证一个MDI文件的合规性。

    Args:
        path: MDI文件路径（Markdown格式）。
        profile_type: Profile类型，"auto"自动检测或指定"skill"/"webapi"/"clitool"。

    Returns:
        ValidationReport验证报告，包含errors/warnings/score。
    """
    return MDIValidator(profile_type=profile_type).validate_file(Path(path))


def generate(
    path: str | Path,
    lang: str = "python",
    output_dir: str | Path = "./mdi_output",
) -> list[Path]:
    """从MDI文件生成代码/测试/文档。

    Args:
        path: MDI文件路径（Markdown格式）。
        lang: 目标语言/格式，支持"python"/"typescript"/"openapi"/"mcp"/"markdown"/"cli"/"pytest"/"jest"。
        output_dir: 输出目录，默认"./mdi_output"。

    Returns:
        生成的文件路径列表。
    """
    doc = parse(path)
    gen = MDIGenerator(lang=lang)
    return gen.generate(doc, Path(output_dir))


__all__ = [
    "parse",
    "validate",
    "generate",
    "MDIDocument",
    "Interface",
    "Parameter",
    "Response",
    "ErrorCode",
    "CodeBlock",
    "CheckItem",
    "DecisionNode",
    "Section",
    "Warning",
    "MDIParser",
    "MDIValidator",
    "ValidationReport",
    "MDIGenerator",
    "BaseGenerator",
    "PythonGenerator",
    "TypeScriptGenerator",
    "OpenAPIGenerator",
    "MCPGenerator",
    "MarkdownGenerator",
    "CLIGenerator",
    "DiffResult",
    "ChangeType",
    "ChangeSeverity",
    "diff_documents",
    "diff_files",
    "diff_strings",
    "get_version_bump_recommendation",
    "VERSIONING_BEST_PRACTICES",
]
