"""Python Click CLI骨架生成器。

为CLI Tool Profile生成Python Click命令行骨架代码。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument, Interface, Parameter, Section
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import (
    escape_docstring,
    make_interface_name,
    map_python_type,
    snake_to_pascal,
    sanitize_identifier,
)


class CLIGenerator(BaseGenerator):
    """Python Click CLI骨架生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "cli")
        ).replace("-", "_")
        package_dir = output_dir / module_name
        package_dir.mkdir(parents=True, exist_ok=True)

        commands = self._extract_commands(doc)

        cli_content = self._generate_cli_module(doc, commands)
        cli_path = package_dir / "cli.py"
        generated_files.append(self._write_file(cli_path, cli_content))

        main_content = self._generate_main(doc, module_name)
        main_path = package_dir / "__main__.py"
        generated_files.append(self._write_file(main_path, main_content))

        init_content = f'"""Generated CLI tool: {doc.title or module_name}."""\n\nfrom .cli import main\n\n__all__ = ["main"]\n'
        init_path = package_dir / "__init__.py"
        generated_files.append(self._write_file(init_path, init_content))

        return generated_files

    def _extract_commands(self, doc: MDIDocument) -> list[dict[str, Any]]:
        """从文档中提取命令定义。"""
        commands: list[dict[str, Any]] = []

        if doc.interfaces:
            for iface in doc.interfaces:
                cmd = self._interface_to_command(iface)
                commands.append(cmd)
        else:
            commands = self._commands_from_sections(doc)

        return commands

    def _interface_to_command(self, iface: Interface) -> dict[str, Any]:
        """将Interface转换为命令定义。"""
        cmd_name = sanitize_identifier(iface.name).replace("-", "_")
        return {
            "name": cmd_name,
            "help": iface.description or iface.summary or iface.name,
            "params": list(iface.parameters),
            "method": iface.method,
            "path": iface.path,
        }

    def _commands_from_sections(self, doc: MDIDocument) -> list[dict[str, Any]]:
        """从章节提取命令。"""
        commands: list[dict[str, Any]] = []

        def walk(section, is_command_level=False):
            if section.level >= 3 or is_command_level:
                params = self._collect_params(section)
                if params or section.level == 2:
                    cmd_name = sanitize_identifier(section.title).replace("-", "_")
                    if cmd_name and not cmd_name.startswith("_"):
                        commands.append({
                            "name": cmd_name,
                            "help": section.content[:200].strip() if section.content else section.title,
                            "params": params,
                        })
            for sub in section.subsections:
                walk(sub, section.level >= 2)

        for section in doc.sections:
            walk(section)

        return commands

    def _collect_params(self, section) -> list[Parameter]:
        """从章节收集参数。"""
        params: list[Parameter] = []
        for table in section.tables:
            if table.get("type") == "parameter":
                params.extend(table.get("parsed_items", []))
        return params

    def _generate_cli_module(self, doc: MDIDocument, commands: list[dict[str, Any]]) -> str:
        """生成cli.py模块。"""
        lines: list[str] = []

        lines.append('"""CLI module for {name}."""'.format(name=doc.title or "CLI Tool"))
        lines.append("")
        lines.append("import sys")
        lines.append("from typing import Optional")
        lines.append("")
        lines.append("import click")
        lines.append("")
        lines.append("")

        doc_desc = doc.description or doc.title or "CLI Tool"
        lines.append("@click.group()")
        lines.append("@click.version_option()")
        lines.append(f"def main():")
        lines.append(f'    """{escape_docstring(doc_desc)}"""')
        lines.append("    pass")
        lines.append("")

        for cmd in commands:
            lines.extend(self._generate_command(cmd))

        lines.append("")
        lines.append('if __name__ == "__main__":')
        lines.append("    main()")
        lines.append("")

        return "\n".join(lines)

    def _generate_command(self, cmd: dict[str, Any]) -> list[str]:
        """生成单个命令函数。"""
        lines: list[str] = []
        cmd_name = cmd["name"]
        help_text = cmd.get("help", "").replace('"""', '\\"\\"\\"')

        decorators: list[str] = []
        params = cmd.get("params", [])
        func_params: list[str] = []

        required_args: list[Parameter] = []
        optional_args: list[Parameter] = []
        for p in params:
            if p.required:
                required_args.append(p)
            else:
                optional_args.append(p)

        for param in required_args:
            param_name = sanitize_identifier(param.name).replace("-", "_")
            py_type = self._click_type(param.type)
            decorators.append(f"@click.argument('{param_name}', type={py_type})")
            func_params.append(f"{param_name}: {map_python_type(param.type)}")

        for param in optional_args:
            param_name = sanitize_identifier(param.name).replace("-", "_")
            aliases = param.extra_data.get("aliases") if hasattr(param, "extra_data") and param.extra_data else None
            if aliases:
                opt_parts = []
                for a in aliases:
                    a_clean = a.lstrip("-")
                    if len(a_clean) == 1:
                        opt_parts.append("-" + a_clean)
                    else:
                        opt_parts.append("--" + a_clean)
                opt_name = "/".join(opt_parts)
            else:
                opt_name = "--" + param.name.replace("_", "-")
            py_type = self._click_type(param.type)
            help_str = param.description.replace("'", "\\'") if param.description else ""
            decorator_parts = [f"'{opt_name}'", f"type={py_type}"]
            default_val = self._parse_default(param.default, param.type) if param.default is not None else None
            is_flag = (param.type == "boolean" or param.location == "flag")
            if is_flag:
                decorator_parts = [f"'{opt_name}'", "is_flag=True"]
                if default_val is True:
                    decorator_parts.append("default=True")
                    func_default = "True"
                else:
                    func_default = "False"
            else:
                if default_val is not None:
                    decorator_parts.append(f"default={repr(default_val)}")
                    func_default = repr(default_val)
                else:
                    func_default = "None"
            if help_str:
                decorator_parts.append(f"help='{help_str}'")
            decorators.append("@click.option(" + ", ".join(decorator_parts) + ")")
            func_params.append(f"{param_name}: Optional[{map_python_type(param.type)}] = {func_default}")

        lines.append("")
        for dec in decorators:
            lines.append(dec)
        lines.append(f"@main.command()")
        lines.append(f"def {cmd_name}({', '.join(func_params)}):")
        if help_text:
            lines.append(f'    """{escape_docstring(help_text)}"""')
        lines.append("    click.echo('TODO: Implement " + cmd_name + "')")
        lines.append("")

        return lines

    def _click_type(self, type_str: str | None) -> str:
        """将MDI类型映射为Click类型。"""
        if not type_str:
            return "click.STRING"
        type_lower = type_str.lower().strip()
        if type_lower in ("integer", "int"):
            return "click.INT"
        if type_lower in ("number", "float"):
            return "click.FLOAT"
        if type_lower in ("boolean", "bool"):
            return "click.BOOL"
        return "click.STRING"

    def _parse_default(self, default_str: str | None, type_str: str | None) -> Any:
        """解析默认值字符串为对应Python类型。"""
        if default_str is None:
            return None
        type_lower = (type_str or "").lower()
        if type_lower in ("boolean", "bool"):
            return default_str.lower() in ("true", "yes", "1")
        if type_lower in ("integer", "int"):
            try:
                return int(default_str)
            except ValueError:
                return default_str
        if type_lower in ("number", "float"):
            try:
                return float(default_str)
            except ValueError:
                return default_str
        return default_str

    def _generate_main(self, doc: MDIDocument, module_name: str) -> str:
        """生成__main__.py入口文件。"""
        lines = [
            f'"""Entry point for {module_name} CLI."""',
            "",
            "import sys",
            f"from {module_name}.cli import main",
            "",
            'if __name__ == "__main__":',
            "    sys.exit(main())",
            "",
        ]
        return "\n".join(lines)
