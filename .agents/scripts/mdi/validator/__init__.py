"""MDI (Markdown Interface) 规范验证器。

提供MDI文档的规范化验证能力，支持Skill/WebApi/CliTool三种Profile。
验证规则覆盖frontmatter完整性、章节结构、内容质量、链接规范、Profile特定要求。

拆分结构（遵循单一职责原则）：
- models: 数据模型（ValidationIssue, ValidationReport）
- constants: 常量定义（正则、阈值）
- utils: 工具函数（代码块检测、路径查找）
- core: MDIValidator主类（入口+验证流程编排）
- rules/: 验证规则集
  - common: 通用验证规则
  - links: 链接验证规则
  - profiles: Profile特定规则

向后兼容：所有公共API均可直接从 `mdi.validator` 导入，无需修改现有代码。
"""

from .models import ValidationIssue, ValidationReport
from .core import MDIValidator

__all__ = [
    "ValidationIssue",
    "ValidationReport",
    "MDIValidator",
]
