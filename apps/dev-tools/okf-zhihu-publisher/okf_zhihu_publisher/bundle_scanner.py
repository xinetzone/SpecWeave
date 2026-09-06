"""OKF bundle 扫描器。

遍历 bundles 目录，找出所有需要同步的 Markdown 文件，
并解析其层级路径。
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional


@dataclass
class BundleFile:
    """一个待同步的 bundle 文件。"""

    # 本地绝对路径
    abs_path: Path
    # 相对 bundles_dir 的路径，如 "jishu/ai/ai-agent/zhihu-cli/index.md"
    rel_path: str
    # 所属域（第一级目录），如 "jishu"
    domain: str
    # 所属组路径（域/组/子组...），如 "jishu/ai/ai-agent"
    group_path: str
    # bundle 名称，如 "zhihu-cli"
    bundle_name: str
    # 层级：concepts / examples / references / ""（根 index）
    layer: str
    # 文件大小（字节）
    file_size: int


class BundleScanner:
    """OKF bundle 目录扫描器。"""

    # 三层目录名
    LAYER_DIRS = {"concepts", "examples", "references"}

    def __init__(self, bundles_dir: Path):
        self.bundles_dir = bundles_dir.resolve()

    def scan(
        self,
        domain_filter: Optional[str] = None,
        top_n: Optional[int] = None,
        bundle_whitelist: Optional[set[str]] = None,
    ) -> list[BundleFile]:
        """扫描 bundles 目录，返回所有 Markdown 文件。

        Args:
            domain_filter: 只扫描指定域，如 "jishu"
            top_n: 只取前 N 个 bundle（按字母序），None 则全部
            bundle_whitelist: 只扫描指定名称的 bundle 集合，None 则不限制
        """
        files: list[BundleFile] = []
        bundle_count = 0
        current_bundle = None

        for md_file in sorted(self._iter_markdown_files()):
            rel_path = str(md_file.relative_to(self.bundles_dir))
            parts = rel_path.replace("\\", "/").split("/")

            # 至少需要: domain/.../bundle/...
            if len(parts) < 2:
                continue

            domain = parts[0]
            if domain_filter and domain != domain_filter:
                continue

            bundle_info = self._find_bundle(parts)
            if bundle_info is None:
                continue

            bundle_name, layer, group_path = bundle_info

            # 白名单过滤
            if bundle_whitelist is not None and bundle_name not in bundle_whitelist:
                continue

            # top_n 控制
            if top_n is not None:
                if current_bundle != bundle_name:
                    current_bundle = bundle_name
                    bundle_count += 1
                    if bundle_count > top_n:
                        break

            files.append(
                BundleFile(
                    abs_path=md_file,
                    rel_path=rel_path,
                    domain=domain,
                    group_path=group_path,
                    bundle_name=bundle_name,
                    layer=layer,
                    file_size=md_file.stat().st_size,
                )
            )

        return files

    def _iter_markdown_files(self) -> Iterator[Path]:
        """遍历所有 .md 文件。"""
        for path in sorted(self.bundles_dir.rglob("*.md")):
            # 跳过 _build 等构建目录
            if "_build" in path.parts:
                continue
            # 跳过隐藏目录
            if any(part.startswith(".") for part in path.parts):
                continue
            yield path

    def _find_bundle(self, parts: list[str]) -> Optional[tuple[str, str, str]]:
        """从路径段中识别 bundle 名称、层级和组路径。

        Returns:
            (bundle_name, layer, group_path) 或 None
        """
        # 策略：找到第一个 LAYER_DIR（concepts/examples/references），
        # 它的上一级就是 bundle 目录
        for i, part in enumerate(parts):
            if part in self.LAYER_DIRS and i > 0:
                bundle_name = parts[i - 1]
                layer = part
                group_path = "/".join(parts[: i - 1]) if i > 1 else parts[0]
                return (bundle_name, layer, group_path)

        # 如果没有三层目录，检查是否是 bundle 根目录的 index.md / log.md
        # 启发式：文件名是 index.md 或 log.md，且父目录下有 concepts/ / examples/ / references/ 之一
        if len(parts) >= 2:
            fname = parts[-1]
            parent = parts[-2]
            if fname in ("index.md", "log.md"):
                # 检查父目录是否是 bundle 根（有三层子目录之一）
                parent_path = self.bundles_dir / "/".join(parts[:-1])
                if any((parent_path / d).is_dir() for d in self.LAYER_DIRS):
                    bundle_name = parent
                    layer = "root"
                    group_path = "/".join(parts[:-2]) if len(parts) > 2 else parts[0]
                    return (bundle_name, layer, group_path)

        return None

    def get_top_bundles(
        self,
        n: int,
        domain_filter: Optional[str] = None,
    ) -> list[str]:
        """获取前 N 个 bundle 名称（按路径字母序）。"""
        bundles: set[str] = set()
        for bf in self.scan(domain_filter=domain_filter):
            bundles.add(bf.bundle_name)
        return sorted(bundles)[:n]


def generate_remote_title(bf: BundleFile) -> str:
    """生成带层级前缀的远程文件名，用于提升检索质量。

    格式：域/组/束/层级/文件名  →  jishu.ai.zhihu-cli.concepts.03-core-capabilities.md
    使用点分隔而非斜杠，因为文件名中斜杠可能有问题。
    """
    parts = bf.rel_path.replace("\\", "/").split("/")
    return ".".join(parts)
