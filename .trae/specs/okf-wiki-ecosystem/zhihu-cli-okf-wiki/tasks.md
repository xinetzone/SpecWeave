# Zhihu CLI 知乎数据开放平台 OKF Wiki - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: R 阶段 - 信源获取与 F 编号事实采集
- **Priority**: high
- **Depends On**: None
- **Status**: completed
- **Completion Evidence**:
  - 采集事实 105 条（F-001~F-105），7个分类，编号连续无跳号
  - P0 待核验 14 项已识别并标记
  - 文件：`.trae/specs/okf-wiki-ecosystem/zhihu-cli-okf-wiki/facts.md`
  - TR-1.1 ✅ 事实编号连续无跳号，格式统一
  - TR-1.2 ✅ 厂商自述数据单独标记，共 14 项 P0
  - TR-1.3 ✅ 观点类内容标注"作者观点"
- **Description**:
  - 对6篇来源文章进行结构化事实采集，从 F-001 起连续编号
  - 按主题分类：平台定位类、产品能力类、安装配置类、技术架构类、安全设计类、实战玩法类、生态集成类
  - 作者观点显式标注，厂商自述数据单独标记
  - 产出：`facts.md`（spec 目录内）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-1.1: 事实编号连续无跳号，格式统一为 `| F-XXX | 事实内容 | 来源 | 分类 |`
  - `rule` TR-1.2: 厂商自述成效数字/额度数据单独标记，不与事实混同
  - `rule` TR-1.3: 观点类内容标注"作者观点"，不登记为事实
- **Notes**: 6篇文章预估采集 60-80 条事实

## [x] Task 2: R 阶段 - P0 权威核验
- **Priority**: high
- **Depends On**: Task 1
- **Status**: completed
- **Completion Evidence**:
  - 14 项 P0 核验：3 ✅ / 11 ⚠️ / 0 ❌
  - 3 条勘误：接入方式实为三种（E-001 中）、额度随时点变化（E-002 低）、Skills 与 CLI 关系澄清（E-003 低）
  - 8 项厂商自述数据已标记无法独立核验
  - TR-2.1 ✅ 所有 P0 项均有核验结论与来源
  - TR-2.2 ✅ 发现的口径差异已记录勘误，未静默照搬
  - TR-2.3 ✅ 勘误四张清单覆盖：日期版本表/成效数字/口径对照/引文核对

## [x] Task 3: I 阶段 - 骨架判定与三层知识拆分
- **Priority**: high
- **Depends On**: Task 1
- **Status**: completed
- **Completion Evidence**:
  - 骨架确认：index + concepts/ + examples/ + references/ + log
  - concepts/ 6 篇：平台介绍/接入架构/安全设计/核心能力/实战玩法/生态集成
  - examples/ 3 篇：注册安装/核心命令/Agent 接入
  - references/ 3 篇：article-source/verification/index
  - structure-plan.md 已生成，每篇文档有大纲和 F 编号映射
  - TR-3.1 ✅ 目录结构符合 OKF v0.2 规范
  - TR-3.2 ✅ 每篇 concept 有明确知识层级定位
  - TR-3.3 ✅ 三层拆分合理（事实层→机制层→应用层递进）

## [x] Task 4: E 阶段 - 信源先行生成 references/
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Status**: completed
- **Completion Evidence**:
  - bundle-references/article-source.md：105 条 F 编号事实完整双份登记
  - bundle-references/verification.md：P0 核验报告 + 勘误汇总 + 厂商自述声明
  - bundle-references/index.md：toctree + 导航表
  - TR-4.1 待 V 阶段正式核对（初检一致）
  - TR-4.2 ✅ verification.md 含勘误章节
  - TR-4.3 ✅ references/index.md 含 toctree 块与表格链接并存
- **Description**:
  - 识别所有 P0 级声明：数字（额度、版本号、文件大小）、日期（发布时间）、官方表态、产品功能矩阵
  - 通过 WebSearch 补充官方权威信源进行交叉核验
  - 过勘误四张清单：日期/版本表、成效数字溯源表、口径对照表、引文逐字核对表
  - 产出：核验记录（写入 facts.md 末尾或单独 verification-raw.md）
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-2.1: 所有 P0 项均有核验结论（✅/⚠️/❌）与核验来源
  - `rule` TR-2.2: 发现源文错误时，新增 F 编号记录正确值与差异，不静默照搬
  - `rubric` TR-2.3: 勘误四张清单覆盖度评估（P0 项逐项过筛，无遗漏）
- **Notes**: 知乎开放平台官方文档为第一优先核验源；无法核验的标注"仅博文单源"

## [ ] Task 3: I 阶段 - 骨架判定与三层知识拆分
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 确认知识包目录骨架（已初判设 examples/）
  - 三层知识拆分：
    - 第一层（事实层）：平台定位、产品矩阵、核心命令列表 → concepts/00-平台介绍.md
    - 第二层（机制原理层）：接入方式架构、安全设计、凭证存储 → concepts/01-技术架构.md、concepts/02-安全设计.md
    - 第三层（应用/玩法层）：实战玩法汇总、生态集成 → concepts/03-实战玩法.md、concepts/04-生态集成.md
  - examples/ 规划：安装配置示例、核心命令使用示例
  - 确定归属分组：AI Agent 域 → 工具/平台分组
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 目录结构符合 OKF v0.2 规范（index + concepts/ + examples/ + references/ + log）
  - `rule` TR-3.2: 每篇 concept 有明确的知识层级定位，事实与观点分层
  - `rubric` TR-3.3: 三层拆分合理性评估（逻辑递进、无重叠、无遗漏）
- **Notes**: 操作可复现性两问已确认为"是"，examples/ 目录设立

## [ ] Task 4: E 阶段 - 信源先行生成 references/
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 生成 `references/article-source.md`：博文事实清单（F 编号双份登记之一），与 spec facts.md 编号一致
  - 生成 `references/verification.md`：P0 核验报告，含勘误章节
  - 生成 `references/index.md`：toctree + 导航表
  - 信源先行：这是 E 阶段第一步，先于 concepts/ 生成
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: article-source.md 的 F 编号集合与 spec facts.md 完全一致（正则比对）
  - `rule` TR-4.2: verification.md 包含勘误章节，每条 ❌/⚠️ 项有说明
  - `rule` TR-4.3: references/index.md 含 toctree 块与表格链接并存
- **Notes**: 双份 F 编号一致性是 V 阶段核心质量门

## [x] Task 5: E 阶段 - 生成 concepts/ 概念文档
- **Priority**: high
- **Depends On**: Task 4
- **Status**: completed
- **Completion Evidence**:
  - 6 篇概念文档全部生成（英文命名 kebab-case）
  - 00-platform-overview / 01-access-architecture / 02-security-credentials
  - 03-core-capabilities / 04-practical-playbooks / 05-ecosystem-integration
  - 事实处均带 [F-xxx] 引用，观点处标注"社区观点"
  - Mermaid 图表 2 张（接入架构 + 安全流程）
  - TR-5.1 ✅ 抽查验证：数字/产品名/官方表态均有 F 编号引用
  - TR-5.2 ✅ concepts/index.md 含 toctree 块
  - TR-5.3 ✅ 内容质量评估：结构清晰、三层递进

## [x] Task 6: E 阶段 - 生成 examples/ 示例文档
- **Priority**: medium
- **Depends On**: Task 5
- **Status**: completed
- **Completion Evidence**:
  - 3 篇示例文档：01-setup-installation / 02-core-commands / 03-agent-integration
  - 文件名英文命名 kebab-case
  - examples/index.md 含 toctree 块
  - TR-6.1 ✅ 步骤顺序合理，输入输出清晰
  - TR-6.2 ✅ examples/index.md 含 toctree 块
  - TR-6.3 ✅ 示例可复现性评估：读者可按步骤完成操作

## [x] Task 7: E 阶段 - 生成 index.md 与 log.md
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Status**: completed
- **Completion Evidence**:
  - 根 index.md：OKF v0.2 frontmatter 完整 + 简介 + 导航表 + toctree
  - log.md：初始版本记录
  - toctree 收录：concepts/index、examples/index、references/index、log
  - stale_after: 2026-12-31
  - TR-7.1 ✅ frontmatter 必填字段完整
  - TR-7.2 ✅ toctree 收录齐全
  - TR-7.3 ✅ 表格链接与 toctree 条目一致

## [x] Task 8: V 阶段 - 对抗审查与机械门禁
- **Priority**: high
- **Depends On**: Task 7
- **Status**: completed
- **Completion Evidence**:
  - TR-8.1 ✅ 双份 F 编号一致性：article-source.md 与 facts.md 均为 F-001~F-105（105条，连续无跳号）
  - TR-8.2 ✅ 三级 toctree 完整性：check-toctrees.py 全量通过，所有 index.md 引用有效
  - TR-8.3 ✅ 相对链接可达：无 file:/// 绝对路径，全部使用相对路径
  - TR-8.4 ✅ 勘误落实：E-001（三种接入方式）、E-002（额度时点标注）、E-003（Skills+CLI关系澄清）均在正文中体现
  - TR-8.5 ✅ 四视角审查：事实溯源有 F 编号/结构规范 OKF v0.2/可用性分层导航/时效边界标注
  - UTF-8 编码检查通过（9642 个文件）

## [x] Task 9: V 阶段 - 索引接入与计数同步
- **Priority**: high
- **Depends On**: Task 8
- **Status**: completed
- **Completion Evidence**:
  - 归属：jishu/ai/ai-agent/zhihu-cli（AI Agent 框架组 · 工具教程类）
  - ai-agent/index.md：total_bundles 44→45，导航表加行，toctree 追加
  - bundles/index.md：total_bundles 500→501，jishu 域 376→377，ai 分组 170→171，五面对齐
  - jishu/index.md：ai 分组 170→171
  - TR-9.1 ✅ 分组 index toctree 条目数与实际目录数一致（45 个）
  - TR-9.2 ✅ bundles/index.md 计数五面一致（frontmatter/计数行/节标题/分组表/toctree）
  - TR-9.3 ✅ 新 bundle 可从根 index 经 jishu→ai→ai-agent BFS 到达

## [ ] Task 10: C 阶段 - 原子提交
- **Priority**: medium
- **Depends On**: Task 9
