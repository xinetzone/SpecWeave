"""配置管理：从环境变量和配置文件读取参数。"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """运行时配置。"""

    access_secret: str
    base_url: str = "https://developer.zhihu.com/api/v1"
    bundles_dir: Path = field(default_factory=lambda: Path("doc/bundles"))
    state_file: Path = field(default_factory=lambda: Path("publish-state.json"))
    default_kb_id: Optional[str] = None
    domain_filter: Optional[str] = None
    top_n: Optional[int] = None
    dry_run: bool = False
    verbose: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置。"""
        secret = os.environ.get("ZHIHU_ACCESS_SECRET", "")
        return cls(access_secret=secret)

    def validate(self) -> list[str]:
        """验证配置完整性，返回错误列表。"""
        errors = []
        if not self.access_secret and not self.dry_run:
            errors.append("ZHIHU_ACCESS_SECRET 环境变量未设置")
        if not self.bundles_dir.exists():
            errors.append(f"bundles 目录不存在: {self.bundles_dir}")
        return errors
