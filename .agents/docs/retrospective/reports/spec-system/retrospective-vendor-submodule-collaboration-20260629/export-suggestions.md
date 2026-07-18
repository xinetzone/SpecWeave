---
id: "retrospective-vendor-submodule-collaboration-export"
title: "导出建议 — Vendor 外部子模块协同框架"
source: "../../../../../../.trae/specs/standards-tools/establish-vendor-collaboration-framework/spec.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/spec-system/retrospective-vendor-submodule-collaboration-20260629/export-suggestions.toml"
---
# 导出建议 — Vendor 外部子模块协同框架

## 四、导出环节

### 4.1 改进建议

| 问题 | 改进措施 | 优先级 | 预期效果 | 状态 |
|------|---------|--------|---------|------|
| Windows 终端 emoji 编码问题 | 在 lib/cli.py 中添加终端编码检测，GBK 环境自动降级为 ASCII 符号（[✓][✗][!]） | 中 | 消除 Windows 用户运行脚本时的 UnicodeEncodeError | 待规划 |
| check-links.py Windows file:// URL 解析 bug | 修复 file:///d:/ 路径解析逻辑，正确处理 Windows 盘符 | 中 | Windows 环境链接检查准确率提升到 100% | 待规划 |
| 深度检查未集成到 CI | 考虑在 pre-commit hook 或 CI 中添加 `repo-check.py vendor --deep` 检查 | 低 | 防止 PR 引入非法 vendor 引用 | 待规划 |
| 模式萃取流程纯文档化 | 开发萃取辅助脚本，自动化 source 标注、资产索引更新 | 低 | 降低模式萃取的手动操作成本 | 待规划 |

### 4.2 行动计划

| 优先级 | 改进项 | 具体措施 | 建议时间 | 状态 |
|--------|--------|---------|---------|------|
| 高 | 沉淀可复用模式 | 将"四不原则"、三区域边界模型、submodule 元数据外置策略沉淀为方法论模式到 patterns/ | 本次 | 进行中 |
| 高 | 更新知识库索引 | 将 VENDOR-INTEGRATION.md 相关内容登记到 docs/knowledge/README.md | 本次 | 进行中 |
| 中 | 修复 Windows 终端编码 | 在 lib/cli.py 添加终端编码自适应 | 下次遇到时 | 待规划 |
| 中 | 修复 check-links.py Windows bug | 修复 file:// URL 路径解析 | 下次遇到时 | 待规划 |
| 低 | CI 集成深度检查 | 在 CI 配置中添加 vendor --deep 检查 | 有 CI 时 | 待规划 |

### 4.3 模式成熟度更新

| 模式 ID | 成熟度变化 | 触发原因 | 更新时间 | 验证/复用次数 |
|---------|-----------|---------|---------|-------------|
| three-zone-boundary-model（三区域边界模型） | 新增 L1 | 本次首次成功实践三区域划分管理 submodule | 2026-06-29 | 1 次验证 |
| vendor-dependency-four-negatives（外部依赖四不原则） | 新增 L1 | 本次从实践中提炼出"不侵入/不直引/不跟版/不裸考" | 2026-06-29 | 1 次验证 |
| submodule-metadata-externalization（submodule 元数据外置） | 新增 L1 | 实践证明在 submodule 外管理元数据可避免 dirty 状态 | 2026-06-29 | 1 次验证 |
| deep-check-as-parameter（深度检查作为参数扩展） | 复用既有模式 | 复用 existing "参数扩展而非新建脚本" 模式，验证有效 | 2026-06-29 | +1 次复用 |
| spec-implementation-elastic-adjustment（Spec 实施弹性调整） | 新增 L1 | 实施过程中基于事实调整 checklist 项，标注 N/A 及原因 | 2026-06-29 | 1 次验证 |

### 4.4 知识沉淀清单

本次复盘需沉淀以下知识资产：

1. **方法论模式**（patterns/methodology-patterns/）：
   - 三区域边界模型（governance-strategy/ 或 tools-automation/）
   - 外部依赖四不原则（governance-strategy/）
   - Submodule 元数据外置策略（tools-automation/）

2. **知识条目**（docs/knowledge/）：
   - 在 knowledge 索引中登记 VENDOR-INTEGRATION.md
   - 新增 troubleshooting 条目：submodule 内创建文件导致 modified content

3. **代码模式**（patterns/code-patterns/）：
   - Git submodule 状态检测模式（git submodule status 前缀解析 + git status --porcelain）

### 4.5 后续优化方向

1. **短期**：完成本次模式萃取（沉淀 3 个方法论模式 + 1 个代码模式 + 1 个故障排查条目），更新知识库索引
2. **中期**：修复 Windows 编码和链接检查两个工具 bug，提升开发体验
3. **长期**：引入更多 submodule 后，抽象通用的 submodule 管理框架，实现"添加新 submodule"的自动化流程（自动更新 .gitmodules、自动生成 VERSION.md 条目、自动配置 pytest 排除）
