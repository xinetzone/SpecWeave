---
id: "flexloop-team-operations-06-compliance-emergency"
title: "flexloop团队手册：合规检查与应急处理"
source: "teams/flexloop-team-operations.md#06"
x-toml-ref: "../../../.meta/toml/.agents/teams/flexloop-team-operations/06-compliance-emergency.toml"
---
# flexloop团队手册：合规检查与应急处理

团队成员可使用以下自动化工具进行自检：

| 工具 | 命令 | 检查内容 | 执行时机 |
|---|---|---|---|
| vendor 基础检查 | `python .agents/scripts/check-vendor.py` | 子模块模式、分支跟踪、非法导入、工作树清洁、反向链接 | 提交前必执行 |
| vendor 深度检查 | `python .agents/scripts/check-vendor.py --deep` | 上述检查 + 初始化状态、元数据一致性、测试隔离 | 版本更新后必执行 |
| 链接有效性 | `python .agents/scripts/check-links.py --path vendor/` | 文档链接、反向依赖 | 修改文档后必执行 |
| 重复代码检查 | `python .agents/scripts/check-duplication.py` | 跨脚本重复代码 | 萃取新脚本后必执行 |
| Mermaid 检查 | `python .agents/scripts/check-mermaid.py --fix` | Mermaid 语法安全 | 修改含图的文档后必执行 |
| 反向链接修复 | `python .agents/scripts/fix-flexloop-reverse-links.py` | 自动修复遗留反向依赖链接 | 发现反向依赖时执行 |

# 应急处理

## 场景 A：子模块工作树污染（modified content）

**症状**：`git status` 显示 `modified: vendor/flexloop (modified content)`

**处理流程**：
1. 判断修改来源：
   - 正在进行的开发工作 → 遵循工作流2继续开发，完成后 commit/push
   - 意外修改或临时文件 → 清理：
     ```bash
     cd vendor/flexloop
     git checkout .
     git clean -fd
     ```
   - 需保留参考 → 暂存：
     ```bash
     cd vendor/flexloop
     git stash
     ```
2. 确认 `git status vendor/flexloop` 不再显示 modified content

## 场景 B：更新后出现兼容性问题

**症状**：子模块更新后，SpecWeave 功能异常或测试失败

**处理流程**：
1. 立即回滚到上一个稳定版本：
   ```bash
   git submodule update vendor/flexloop
   ```
2. 确认 VERSION.md 中记录的 commit 哈希与回滚后的指针一致
3. 重新运行关键测试验证回滚成功
4. 分析兼容性问题原因，在下一次更新前制定适配方案

## 场景 C：发现反向依赖链接

**症状**：check-vendor.py 报告反向依赖，或 check-links.py 发现失效外链

**处理流程**：
1. 运行自动修复脚本：
   ```bash
   python .agents/scripts/fix-flexloop-reverse-links.py
   ```
2. 检查修复结果，确认链接语义保留完整
3. 进入 flexloop 子模块 commit 并 push：
   ```bash
   cd vendor/flexloop
   git add .
   git commit -m "docs: fix reverse dependency links to SpecWeave"
   git push
   ```
4. 回到 SpecWeave 更新子模块指针
5. 提交 gitlink 更新

## 场景 D：子模块处于 detached HEAD 状态

**症状**：`cd vendor/flexloop && git status` 显示 HEAD detached at xxxxxxx

**处理流程**：
1. 切回 main 分支：
   ```bash
   cd vendor/flexloop
   git checkout main
   ```
2. 如需保留 detached HEAD 上的修改，先创建分支：
   ```bash
   git checkout -b temp-changes
   git checkout main
   git merge temp-changes
   ```
---
## 相关模式

- [三层委员会制度](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-board-system.md)
- [三层治理](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)
---
← 上一章: [05 工作流3：模式萃取](05-workflow-pattern-extraction.md) | **[返回索引](../flexloop-team-operations.md)** | 下一章 → [07 检查清单与文档索引](07-checklist-references.md)
