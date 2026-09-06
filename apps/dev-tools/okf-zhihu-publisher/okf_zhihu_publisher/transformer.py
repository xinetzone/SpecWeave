"""转换适配层。

将 OKF bundle 的 Markdown 文件转换为适合知乎知识库上传的格式：
- 文件名嵌入层级路径（提升检索召回质量）
- frontmatter 保留但不作为首段噪音（添加注释说明）
- 相对路径警告
"""

import re
import tempfile
from pathlib import Path

from .bundle_scanner import BundleFile, generate_remote_title


class BundleTransformer:
    """OKF bundle → 知乎知识库格式转换器。"""

    def __init__(self, output_dir: Path | None = None):
        self.output_dir = output_dir or Path(tempfile.gettempdir()) / "okf-zhihu-pub"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def transform(self, bf: BundleFile) -> Path:
        """转换单个文件，返回转换后的临时文件路径。"""
        content = bf.abs_path.read_text(encoding="utf-8")

        # 1. 提取 frontmatter
        fm, body = self._split_frontmatter(content)

        # 2. 构建新内容：层级标题 + frontmatter（HTML注释包裹减少检索噪音） + 正文
        header = self._build_header(bf, fm)

        new_content = header + "\n\n" + body if body else header

        # 3. 生成输出文件
        out_name = generate_remote_title(bf)
        out_path = self.output_dir / out_name
        out_path.write_text(new_content, encoding="utf-8")

        return out_path

    def _split_frontmatter(self, content: str) -> tuple[dict[str, str], str]:
        """分离 YAML frontmatter 和正文。"""
        if not content.startswith("---"):
            return {}, content

        lines = content.splitlines()
        if len(lines) < 2:
            return {}, content

        fm_lines: list[str] = []
        in_fm = False
        end_idx = 0

        for i, line in enumerate(lines):
            if i == 0 and line.strip() == "---":
                in_fm = True
                continue
            if in_fm and line.strip() == "---":
                end_idx = i + 1
                break
            if in_fm:
                fm_lines.append(line)

        if not in_fm or end_idx == 0:
            return {}, content

        fm_dict: dict[str, str] = {}
        for line in fm_lines:
            if ":" in line:
                key, _, value = line.partition(":")
                fm_dict[key.strip()] = value.strip().strip('"')

        body = "\n".join(lines[end_idx:]).lstrip("\n")
        return fm_dict, body

    def _build_header(self, bf: BundleFile, fm: dict[str, str]) -> str:
        """构建文件头：层级标题 + frontmatter 注释。"""
        title = fm.get("title", bf.bundle_name)
        description = fm.get("description", "")
        tags = fm.get("tags", "")

        lines = [
            f"# {title}",
            "",
            f"> **域**：{bf.domain}",
            f"> **分组**：{bf.group_path}",
            f"> **知识包**：{bf.bundle_name}",
            f"> **层级**：{bf.layer}",
            f"> **文件**：{bf.rel_path}",
        ]
        if description:
            lines.append(f"> **描述**：{description}")
        if tags:
            lines.append(f"> **标签**：{tags}")

        lines.append("")
        lines.append("<!-- OKF-METADATA")
        for k, v in fm.items():
            lines.append(f"  {k}: {v}")
        lines.append("-->")

        return "\n".join(lines)

    def cleanup(self) -> None:
        """清理临时文件。"""
        if self.output_dir.exists():
            for f in self.output_dir.glob("*.md"):
                try:
                    f.unlink()
                except OSError:
                    pass
