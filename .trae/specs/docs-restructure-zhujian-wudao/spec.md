# 竹简悟道文档结构重组 - 产品需求文档

## Overview
- **Summary**：对 `apps/zhujian-wudao/.agents/docs/` 目录下的7个设计文档进行系统性结构重组，按主题相关性建立分类子目录，迁移并重命名文件，更新所有跨文件引用，建立清晰的索引导航机制，形成可维护、可扩展的文档架构。
- **Purpose**：当前所有文件平铺在 `superpowers/specs/` 单一目录下，缺乏主题分类；随着文档数量增长，可维护性下降；需要建立清晰的分类体系和导航机制，便于后续扩展。
- **Target Users**：AI协作者（开发者、架构师、审查者）、项目维护者、未来参与项目的新成员

## Goals
- 建立按主题分类的子目录结构，替代单一平铺目录
- 将7个现有文件按主题迁移到对应分类目录
- 优化文件命名，保持命名一致性和可读性
- 完整保留所有文件原始内容，不做内容修改
- 更新所有跨文件相对路径引用，确保无断链
- 更新 AGENTS.md 中的文件地图和路由索引
- 创建根目录 README.md 作为索引导航
- 生成重组前后结构对比文档
- 验证所有引用链接有效性

## Non-Goals (Out of Scope)
- 不修改任何文件的内容（除路径引用外）
- 不删除任何原始文件（迁移而非复制，源目录清空后删除）
- 不改变文件命名中的日期前缀约定
- 不重组 `.agents/` 下其他目录（html/、roles/、skills/ 等保持不变）
- 不新增洞察或修改洞察内容
- 不更新统计数字（头部行数/洞察数保持原样，后续复盘轮次自然更新）

## Background & Context
- 当前目录结构：`.agents/docs/superpowers/specs/` 下单目录平铺7个文件
- 文件清单（2026-06-17创建，2026-06-26更新至68条洞察）：
  1. `2026-06-17-zhujian-wudao-spec.md` - 产品规格文档（§一至§九，约500行）
  2. `2026-06-17-zhujian-wudao-review.md` - 项目全面复盘报告（18轮，约644行）
  3. `2026-06-17-zhujian-wudao-registration-review.md` - 报名流程复盘报告（约238行）
  4. `2026-06-17-zhujian-wudao-insights-01-30.md` - 洞察库1-30（产品层+架构层，约701行）
  5. `2026-06-17-zhujian-wudao-insights-31-65.md` - 洞察库31-68（哲学层+元层，约3270行）
  6. `2026-06-17-zhujian-wudao-transferable-methods.md` - 可迁移方法论（面向人类，13章，约760行）
  7. `2026-06-17-transferable-patterns.md` - 可迁移模板（面向Agent，9章，约432行）
- 跨文件引用：文件间存在相对路径引用，主要是 spec.md 引用洞察文件，insights 文件互引，review.md 引用 spec 和 insights
- 外部引用：`.agents/AGENTS.md`、`.agents/conventions.md`、`.agents/project.md` 中存在对这些文档路径的引用

## Functional Requirements
- **FR-1**：在 `.agents/docs/` 下创建4个主题分类子目录
- **FR-2**：将7个文件迁移到对应主题目录，保持原始内容
- **FR-3**：规范文件命名，移除冗余前缀或统一命名格式
- **FR-4**：更新所有文件内部的相对路径引用，确保迁移后链接有效
- **FR-5**：更新 `.agents/AGENTS.md` 中的文件地图和路由索引
- **FR-6**：更新 `.agents/conventions.md` 中的设计文档存放路径说明
- **FR-7**：创建 `.agents/docs/README.md` 作为索引导航文档
- **FR-8**：生成重组前后结构对比文档（restructure-comparison.md）
- **FR-9**：清理空的旧目录结构（`superpowers/specs/`）
- **FR-10**：运行链接校验脚本，验证所有引用无断链

## Non-Functional Requirements
- **NFR-1**：所有文件内容100%保留，除路径字符串外不做任何修改
- **NFR-2**：跨文件引用路径更新准确率100%，无断链
- **NFR-3**：重组后的目录结构具备可扩展性，新增文档可自然归类
- **NFR-4**：文件命名保持一致性，遵循现有日期前缀+类型的约定
- **NFR-5**：索引导航清晰，AI协作者可快速定位所需文档
- **NFR-6**：重组操作可追溯，对比文档记录完整变更历史

## Constraints
- **Technical**：必须保持 Markdown 格式；必须使用相对路径（遵循项目规范，禁止 `file:///` 绝对路径）；文件编码保持 UTF-8
- **Business**：不能影响项目现有功能；不能破坏洞察库完整性；不能影响 HTML 原型（HTML不直接引用docs/下文件）
- **Dependencies**：依赖项目现有链接校验脚本 `.agents/scripts/check-links.py`

## Assumptions
- 所有跨文件引用均为相对路径，可通过字符串替换+路径深度计算更新
- `.agents/AGENTS.md` 和 `.agents/conventions.md` 是唯一引用 docs/ 路径的外部文件
- 日期前缀 `2026-06-17-` 应保留，因为这是项目文档创建日期标识
- `superpowers/` 目录名是历史遗留，重组后不再需要该层级
- insights 文件名中的 `31-65` 虽然实际包含到68，但这是历史命名，本次重组不修正（保持与R14重命名一致，后续复盘自然更新）

## Acceptance Criteria

### AC-1: 主题分类目录创建完成
- **Given**：重组任务开始执行
- **When**：创建主题分类子目录
- **Then**：`.agents/docs/` 下存在4个子目录：`product/`、`insights/`、`reviews/`、`knowledge-transfer/`
- **Verification**: `programmatic`
- **Notes**：使用 `Test-Path` 验证目录存在

### AC-2: 文件迁移完成且内容完整
- **Given**：子目录已创建
- **When**：将7个文件迁移到对应目录
- **Then**：每个文件存在于正确的主题目录中，文件大小与原始文件一致，内容哈希匹配
- **Verification**: `programmatic`
- **Notes**：使用文件大小和内容哈希验证完整性

### AC-3: 文件命名规范统一
- **Given**：文件已迁移
- **When**：检查文件命名
- **Then**：所有文件名遵循 `{YYYY-MM-DD}-{type}-{suffix}.md` 格式，类型与所在目录一致
- **Verification**: `programmatic`
- **Notes**：可迁移资产统一添加 `zhujian-wudao-` 前缀保持一致性

### AC-4: 内部跨文件引用全部更新
- **Given**：文件已迁移
- **When**：更新所有文件内的相对路径引用
- **Then**：所有 `[xxx](old-path)` 引用更新为 `[xxx](new-path)`，路径深度计算正确
- **Verification**: `programmatic`
- **Notes**：运行链接校验脚本验证无断链

### AC-5: 外部引用（AGENTS.md等）更新完成
- **Given**：内部引用已更新
- **When**：更新 `.agents/AGENTS.md` 和 `.agents/conventions.md`
- **Then**：文件地图中的路径、路由索引中的路径、规范中的路径均指向新位置
- **Verification**: `programmatic` + `human-judgment`
- **Notes**：检查文件地图表格和路由表

### AC-6: 根目录 README.md 导航索引创建
- **Given**：文件迁移完成
- **When**：创建 `.agents/docs/README.md`
- **Then**：README 包含完整的目录树、每个文件的用途说明、快速查找表
- **Verification**: `human-judgment`
- **Notes**：遵循 AGENTS.md 路由索引风格

### AC-7: 重组前后对比文档生成
- **Given**：重组完成
- **When**：生成对比文档
- **Then**：对比文档包含旧结构树、新结构树、文件迁移映射表、变更统计
- **Verification**: `human-judgment`

### AC-8: 旧目录清理完成
- **Given**：文件全部迁移
- **When**：清理旧目录
- **Then**：`superpowers/specs/` 空目录已删除，`superpowers/` 目录如为空也删除
- **Verification**: `programmatic`

### AC-9: 链接校验全部通过
- **Given**：所有路径更新完成
- **When**：运行 `python .agents/scripts/check-links.py --path apps/zhujian-wudao/.agents/docs`
- **Then**：脚本输出无断链，0个错误
- **Verification**: `programmatic`

### AC-10: 可扩展性验证
- **Given**：新结构建立
- **When**：评估新增文档的归类路径
- **Then**：新增产品文档→product/，新增洞察→insights/，新增复盘→reviews/，新增方法论→knowledge-transfer/，路径自然清晰
- **Verification**: `human-judgment`

## Open Questions
- [ ] 洞察文件是否需要进一步拆分（如按产品层/架构层/哲学层/元层拆分为4个文件）？**决定：不拆分，保持现有两文件结构，避免引入额外风险**
- [ ] `superpowers/` 目录名是否有特殊含义需要保留？**决定：移除，该名称是superpowers技能生成时的遗留，与竹简悟道项目主题无关**
- [ ] 可迁移文件名是否需要去掉项目前缀使其更通用？**决定：保留项目前缀，因为这些方法论是从竹简悟道萃取的，保持溯源性**
- [ ] 是否需要在迁移后立即运行一次完整复盘更新统计？**决定：不更新统计数字，保持文件原始状态，统计更新留待下一轮自然复盘**
