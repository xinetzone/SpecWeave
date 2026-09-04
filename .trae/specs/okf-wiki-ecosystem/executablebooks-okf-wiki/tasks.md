# Executable Books 生态 OKF Wiki 教程 - Implementation Plan

## Task 1: 创建 myst/ 分组目录结构与基础设施
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `projects/awesome-okf-xs/bundles/myst/` 目录
  - 创建分组根 index.md（占位，待所有 bundle 完成后填充最终统计数据）
  - 创建 log.md 初始结构
- **Acceptance Criteria Addressed**: AC-1（部分）
- **Test Requirements**:
  - `rule` TR-1.1: myst/ 目录存在，包含 index.md 和 log.md；证据：文件系统检查

## Task 2: R 阶段 - 分批采集源码事实（第一层：解析核心）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 为 markdown-it-py、mdurl、mdit-py-plugins 三个解析核心项目采集源码事实
  - 逐模块阅读核心源码文件，提取可验证事实（类名、方法签名、数据流、注册机制）
  - 每个项目写入 `spec/facts.md`，事实编号 F-xxx，零推测
  - 通过 G1 质量门：事实中无推断性表述
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-2.1: 3 个项目的 spec/facts.md 均存在，每个至少 30 条事实（小项目 mdurl 至少 15 条）；证据：文件行数统计
  - `rule` TR-2.2: 事实中不包含"用于"/"目的是"/"设计为"等推断词；证据：关键词 Grep 检查

## Task 3: I 阶段 - 架构洞察与知识结构设计（第一层：解析核心）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 facts.md 为 markdown-it-py、mdurl、mdit-py-plugins 各提炼 3-5 个核心架构洞察
  - 设计知识地图（概念分组、学习路径、文档清单）
  - 写入 `spec/insights.md`
  - 通过 G2 质量门：洞察四元组完整（陈述+证据+反常识+行动）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-3.1: 3 个项目的 spec/insights.md 均存在，每个含 3-5 个洞察；证据：文件内容检查
  - `rule` TR-3.2: 每个洞察包含四元组要素；证据：结构化检查

## Task 4: E 阶段 - 生成解析核心 3 个 bundle 的文档
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 信源先行：先生成 references/ 信源登记文件
  - 分批生成 concepts/ 概念文档（每批 ≤ 7 个文件）
  - 生成 examples/ 示例文档
  - 最后生成各级 index.md 导航
  - 生成 log.md
  - 遵循 G3：信源先行、分批生成、Index 最后写
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: 3 个 bundle 均包含完整目录结构（concepts/examples/references/spec/index.md/log.md）；证据：文件系统检查
  - `rule` TR-4.2: 每个内容文档含完整 frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）；证据：YAML 解析验证
  - `rubric` TR-4.3: 文档内容质量；scale 1-5；anchors 1=堆砌/3=基本清晰/5=层层递进可独立使用；threshold >= 4；证据：自我抽检阅读

## Task 5: R+I 阶段 - MyST Sphinx 集成层（MyST-Parser、MyST-NB）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4（可并行，但上下文独立）
- **Description**:
  - 为 MyST-Parser、MyST-NB 两个核心项目采集源码事实（R 阶段）
  - 提炼架构洞察，设计知识地图（I 阶段）
  - 核心项目需要更深入的事实采集（每个 ≥ 60 条事实）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-5.1: 2 个项目的 spec/facts.md 各 ≥ 60 条事实，spec/insights.md 各含 4-5 个洞察；证据：文件统计与内容检查
  - `rule` TR-5.2: G1/G2 质量门通过；证据：推断词 Grep + 四元组结构检查

## Task 6: E 阶段 - 生成 MyST Sphinx 集成层 2 个 bundle
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 为 MyST-Parser、MyST-NB 生成 references/、concepts/、examples/、index.md、log.md
  - MyST-NB 需覆盖 core/（config/read/render）和 ext/glue/ 模块
  - MyST-Parser 需覆盖 sphinx 集成、docutils 桥接、CLI、配置系统
  - 分批生成，每批 ≤ 7 文件
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 2 个 bundle 结构完整，内容文档数 15-30 篇/项目；证据：文件统计
  - `rule` TR-6.2: frontmatter 合规，sources 指向正确 references/；证据：YAML 验证
  - `rubric` TR-6.3: 核心机制解释清晰，配置项和扩展点覆盖完整；scale 1-5；threshold >= 4；证据：自我抽检

## Task 7: R+I+E 阶段 - 格式化与迁移工具层（3 个项目）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 6（可并行）
- **Description**:
  - 为 mdformat-myst、mdformat-footnote、rst-to-myst 采集事实、生成洞察、生成文档
  - mdformat-* 插件项目规模较小，每项目 3-5 篇概念+1-2 篇示例+1-2 篇信源即可
  - rst-to-myst 中等规模，8-12 篇内容文档
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-7.1: 3 个 bundle 结构完整；证据：文件系统检查
  - `rule` TR-7.2: facts.md 和 insights.md 存在，事实数与项目规模匹配；证据：文件统计

## Task 8: R+I+E 阶段 - Sphinx 扩展套件（8 个项目，分两批）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6（MyST-Parser 完成后更易理解扩展机制）
- **Description**:
  - 第一批（核心扩展）：sphinx-book-theme、sphinx-design、sphinx-external-toc（中等规模，8-15 篇内容/项目）
  - 第二批（UI 组件扩展）：sphinx-copybutton、sphinx-togglebutton、sphinx-tabs、sphinx-exercise、sphinx-proof（小规模，3-8 篇内容/项目）
  - 每个项目完成 R→I→E 三阶段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-8.1: 8 个 bundle 结构完整；证据：文件系统检查
  - `rule` TR-8.2: sphinx-book-theme 覆盖主题架构/SCSS/模板/配置；sphinx-design 覆盖指令体系/网格/卡片/标签页/下拉；证据：内容检查
  - `rule` TR-8.3: 小规模扩展至少覆盖安装/注册/指令/配置项；证据：概念文档清单检查

## Task 9: R+I+E 阶段 - 基础设施工具层（3 个项目）
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 8（可并行）
- **Description**:
  - 为 jupyter-cache、github-activity、web-compile 完成 R→I→E 三阶段
  - jupyter-cache 是核心基础设施（MyST-NB 的执行后端），需较深入覆盖（12-18 篇内容文档），覆盖数据库/缓存API/CLI/执行器
  - github-activity（CLI 工具）和 web-compile（Web 资源编译）为小规模项目，3-6 篇内容文档
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `rule` TR-9.1: 3 个 bundle 结构完整；证据：文件系统检查
  - `rule` TR-9.2: jupyter-cache 覆盖 db/cache/executor CLI 模块；证据：内容检查

## Task 10: V 阶段 - Grep API 真实性验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Tasks 4, 6, 7, 8, 9（所有文档生成完成后）
- **Description**:
  - 提取所有文档中引用的类名、函数名、方法名、配置项名
  - 对每个名称在对应项目源码中执行 Grep 验证存在性
  - 记录虚构 API，逐一修复
  - 对修复后的文档重新验证
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-10.1: 所有文档中引用的 API 在源码中可 Grep 到，零虚构；证据：Grep 验证报告
  - `rule` TR-10.2: 虚构 API 已全部修复；证据：修复后重新 Grep 验证

## Task 11: V 阶段 - 链接检查与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 对 myst/ 分组下所有 .md 文件执行链接检查
  - 修复所有断链（包括内部交叉链接和 sources 引用）
  - 确保交叉链接使用 `/` 开头的 bundle-relative 路径
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-11.1: 零断链；证据：link-check 报告输出
  - `rule` TR-11.2: 交叉链接无 `../` 相对路径（统一使用 `/` 开头）；证据：Grep 检查 `\]\(\.\.` 模式

## Task 12: V 阶段 - Frontmatter 合规性检查与修复
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 解析所有非保留 .md 文件的 YAML frontmatter
  - 检查必填字段（type）和推荐字段（title/description/tags/generated/verified/status/stale_after/sources）
  - 检查保留文件规范（index.md 仅 bundle 根带 okf_version，子目录 index.md 无 frontmatter）
  - 修复所有不合规项
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-12.1: 100% 文件 YAML frontmatter 可解析，type 字段非空；证据：YAML 解析脚本输出
  - `rule` TR-12.2: 子目录 index.md 不含 frontmatter；证据：文件内容检查

## Task 13: 完善 myst/ 分组根 index.md 和更新总索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 填充 myst/index.md 最终内容：生态概览、19 个知识束统计表格、推荐学习路径、生态关系图
  - 更新 bundles/index.md：加入 myst 分组、更新统计数据（total_bundles: 44→63, groups: 11→12）
  - 更新 myst/log.md
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-13.1: myst/index.md 包含 okf_version frontmatter、知识束概览表、学习路径、生态关系图；证据：文件内容检查
  - `rule` TR-13.2: bundles/index.md 中 total_bundles 更新为 63，groups 更新为 12，myst 分组条目存在；证据：文件内容检查

## Task 14: 最终自检与统计
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 13
- **Description**:
  - 统计总文档数、概念数、示例数、信源数
  - 生成最终统计数据更新到 myst/index.md
  - 确保所有 log.md 有初始条目
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-14.1: 统计数据准确（与实际文件数一致）；证据：文件计数 vs 文档声明
  - `rubric` TR-14.2: 整体产出质量评估；scale 1-5；threshold >= 4；证据：综合评估

## Notes
- 实施顺序策略：Task 1（基础设施）→ Task 2-4（解析核心）→ Task 5-6（Sphinx集成）→ Task 7/8/9 可部分并行（格式化工具、Sphinx扩展、基础设施工具）→ Task 10-12（V阶段验证）→ Task 13-14（索引完善与收尾）
- 每批文档生成 ≤ 7 个文件，防止上下文过载
- 核心项目（markdown-it-py、MyST-Parser、MyST-NB、sphinx-book-theme、sphinx-design、jupyter-cache）优先保证质量
- V阶段（Task 10-12）必须严格执行，不可跳过 Grep API 验证
