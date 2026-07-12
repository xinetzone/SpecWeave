"""MDI代码生成器基类。

定义所有生成器的统一接口。
"""

from __future__ import annotations

import sys
from pathlib import Path
from string import Template
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument
from lib.atomic_write import atomic_write_text

TEMPLATES_DIR = Path(__file__).parent / "templates"

try:
    import jinja2
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


class BaseGenerator:
    """代码生成器基类。

    Args:
        template_dir: 自定义模板目录，None则使用内置默认模板。
    """

    def __init__(self, template_dir: Path | None = None) -> None:
        self.template_dir = Path(template_dir) if template_dir else None
        self._jinja_env: jinja2.Environment | None = None

        if HAS_JINJA2:
            loader_paths = []
            if self.template_dir and self.template_dir.exists():
                loader_paths.append(str(self.template_dir))
            loader_paths.append(str(TEMPLATES_DIR))
            self._jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(loader_paths),
                keep_trailing_newline=True,
                trim_blocks=True,
                lstrip_blocks=True,
            )

    def generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        """从MDIDocument生成代码/文档文件。

        Args:
            doc: 已解析的MDI文档对象。
            output_dir: 输出目录。

        Returns:
            生成的文件路径列表。
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return self._generate(doc, output_dir)

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        """子类实现的具体生成逻辑。"""
        raise NotImplementedError

    def _get_template(self, name: str) -> str:
        """获取模板内容，优先使用用户模板，回退到内置模板。

        Args:
            name: 模板文件名。

        Returns:
            模板字符串。
        """
        if self.template_dir:
            user_template = self.template_dir / name
            if user_template.exists():
                return user_template.read_text(encoding="utf-8")

        builtin = TEMPLATES_DIR / name
        if builtin.exists():
            return builtin.read_text(encoding="utf-8")

        return ""

    def _render_template(self, name: str, context: dict[str, Any]) -> str:
        """渲染模板。

        优先使用Jinja2，如果不可用则回退到string.Template。

        Args:
            name: 模板文件名。
            context: 模板上下文变量。

        Returns:
            渲染后的字符串。
        """
        template_str = self._get_template(name)
        if not template_str:
            return ""

        if self._jinja_env is not None and HAS_JINJA2:
            try:
                template = self._jinja_env.get_template(name)
                return template.render(**context)
            except Exception:
                pass

        tpl = Template(template_str)
        return tpl.safe_substitute(context)

    def _write_file(self, path: Path, content: str) -> Path:
        """原子写入文件，确保父目录存在且写入过程中读者不会看到部分内容。"""
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(path, content, encoding="utf-8")
        return path
