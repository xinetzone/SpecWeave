---
id: "flexloop-team-operations-07-checklist-references"
title: "flexloop团队手册：检查清单与文档索引"
source: "teams/flexloop-team-operations.md#07"
x-toml-ref: "../../../.meta/toml/.agents/teams/flexloop-team-operations/07-checklist-references.toml"
---
# flexloop团队手册：检查清单与文档索引

执行任何与 flexloop 相关的操作前，逐项确认：

- [ ] 子模块已初始化（`vendor/flexloop/AGENTS.md` 存在）
- [ ] 主项目工作树清洁或已 stash 非相关变更
- [ ] 不在 flexloop 内添加指向 SpecWeave 的 Markdown 链接
- [ ] 不使用裸 import，条件导入使用 vendor_sandbox.py
- [ ] 不将 vendor 路径加入 sys.path 永久
- [ ] 不在 SpecWeave 环境中运行 flexloop 测试
- [ ] 子模块内修改已 commit 并 push（提交主项目前）
- [ ] VERSION.md 中的 commit 哈希与子模块指针一致
- [ ] 已运行 `check-vendor.py` 基础检查
- [ ] 文档引用使用相对路径，无 file:/// 绝对路径

全部确认无误后方可提交或推送。

# 相关文档索引

| 文档 | 用途 |
|---|---|
| [flexloop-team.md](../flexloop-team.md) | 团队定义、职责矩阵、治理原则 |
| [data/team-flexloop.yaml](../data/team-flexloop.yaml) | 团队配置数据（成员、权限、工作流） |
| [VENDOR-INTEGRATION.md](../../VENDOR-INTEGRATION.md) | 子模块协同规范（完整技术细节） |
| [dependency-management.md](../../protocols/dependency-management.md) | 临时依赖管理协议 |
| [vendor_sandbox.py](../../scripts/lib/vendor_sandbox.py) | 沙箱运行与条件导入工具 |
| [check-vendor.py](../../scripts/check-vendor.py) | vendor 合规检查入口 |

# 相关模式

- [三层委员会制度](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-board-system.md)
- [三层治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)
---
## 相关模式

- [三层委员会制度](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-board-system.md)
- [三层治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)
---
← 上一章: [06 合规检查与应急处理](06-compliance-emergency.md) | **[返回索引](../flexloop-team-operations.md)**
