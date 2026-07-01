"""MDIGenerator统一门面入口。

提供简单的API用于生成各种语言的代码和文档。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument
from mdi.parser import MDIParser
from mdi.generators import GENERATOR_MAP, BaseGenerator


class MDIGenerator:
    """MDI代码生成器统一入口。

    Args:
        lang: 目标语言/格式，支持 python/typescript/openapi/mcp/markdown/cli。
        template_dir: 自定义模板目录（可选）。
    """

    def __init__(self, lang: str = "python", template_dir: Path | None = None) -> None:
        self.lang = lang.lower()
        self.template_dir = Path(template_dir) if template_dir else None
        self._parser = MDIParser(profile_type="auto")
        self._generator = self._create_generator()

    def _create_generator(self) -> BaseGenerator:
        """创建对应的生成器实例。"""
        generator_cls = GENERATOR_MAP.get(self.lang)
        if generator_cls is None:
            supported = ", ".join(self.supported_languages())
            raise ValueError(
                f"不支持的语言: {self.lang!r}，支持的语言: {supported}"
            )
        return generator_cls(template_dir=self.template_dir)

    def generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        """从MDIDocument对象生成代码/文档。

        Args:
            doc: 已解析的MDI文档对象。
            output_dir: 输出目录。

        Returns:
            生成的文件路径列表。
        """
        output_dir = Path(output_dir)
        return self._generator.generate(doc, output_dir)

    def generate_file(self, input_path: Path, output_dir: Path) -> list[Path]:
        """从MDI文件生成代码/文档。

        Args:
            input_path: MDI文件路径。
            output_dir: 输出目录。

        Returns:
            生成的文件路径列表。
        """
        input_path = Path(input_path)
        doc = self._parser.parse_file(input_path)
        return self.generate(doc, output_dir)

    @staticmethod
    def supported_languages() -> list[str]:
        """返回支持的语言/格式列表。"""
        return ["python", "typescript", "openapi", "mcp", "markdown", "cli"]
