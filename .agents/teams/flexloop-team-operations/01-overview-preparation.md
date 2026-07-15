---
id: "flexloop-team-operations-01-overview-preparation"
title: "flexloop团队手册：概述与前置准备"
source: "teams/flexloop-team-operations.md#01"
x-toml-ref: "../../../.meta/toml/.agents/teams/flexloop-team-operations/01-overview-preparation.toml"
---
# flexloop团队手册：概述与前置准备



# 适用范围

- **适用角色**：team-flexloop 全体成员（architect、developer、reviewer、tester）
- **适用场景**：子模块版本同步、子模块内功能开发、从 flexloop 萃取模式/脚本
- **不适用场景**：第三方只读子模块（third_party 类型）的管理、flexloop 项目自身的 CI/CD 维护

# 前置准备

执行任何操作前，请确认以下环境条件已满足：

1. **子模块已初始化**：`vendor/flexloop/` 目录不为空，且存在 `.git` 文件（submodule 指针）
2. **工作树清洁**：`git status` 显示无未提交变更
3. **Git 远程可访问**：对 gitcode.com:flexloop/flexloop.git 有读写权限
4. **flexloop 环境就绪**（如需在子模块内测试）：
   ```bash
   cd vendor/flexloop/apps/chaos
   uv sync
   ```
---
## 相关模式

- [三层委员会制度](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-board-system.md)
- [三层治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)
---
**[返回索引](../flexloop-team-operations.md)** | 下一章 → [02 区域模型与协作原则](02-boundary-principles.md)
