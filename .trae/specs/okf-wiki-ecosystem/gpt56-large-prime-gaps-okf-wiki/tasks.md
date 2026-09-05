# Tasks：GPT-5.6 大素数空隙突破资讯 → OKF 知识包

> 方法论链路：R（事实采集）→ I（洞察分析）→ E（萃取生成）→ V（对抗审查）
> 场景：知识沉淀 - 博文转化 OKF 知识包

## [x] T1：内容敏感度预检 + 文章内容获取
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 判定为公开内容（知乎专栏公开文章，无访问控制）
  - 使用 browser_use 子代理提取全文，已完成
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 文章正文完整提取（标题 + 约 3200 字正文）
  - `human-judgement` TR-1.2: 内容敏感度判定正确（公开内容 → 标准工作流）
- **Completion Evidence**:
  - 文章标题：GPT-5.6仅用一天改写数学史，「双菲」五人团队8年纪录被破！
  - 正文约 3200 字，提取自 zhuanlan.zhihu.com
  - 内容敏感度：公开内容 → 标准工作流
- **Notes**: 已完成

## [x] T2：骨架判定 + 归属决策
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T1
- **Description**: 
  - 骨架判定：操作可复现性两问 → 均为"否"（资讯类，无可复现操作）→ 无 examples/
  - 归属决策：主线为数学领域素数分布问题 → kexue/math/ 分组
  - 资讯速报骨架：index + concepts/（1篇）+ references/ + log
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: bundle 目录结构符合资讯速报骨架（无 examples/）
  - `human-judgement` TR-2.2: 归属 kexue/math/ 合理，与现有 3 个 math bundle 定位不冲突
- **Completion Evidence**:
  - 操作可复现性两问均为否 → 无 examples/
  - math 分组现有 3 束：几何原本/圆锥曲线论/费马大定理（均为经典阅读），本束为前沿资讯，互补
  - 资讯速报骨架确认：index + concepts/（1篇）+ references/ + log
- **Notes**: math 分组现有 3 束均为经典阅读，本束为前沿资讯，性质互补

## [x] T3：R 阶段 - 事实采集（F 编号）+ P0 核验
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T2
- **Description**: 
  - F-001 起编号登记全部客观事实到 facts.md
  - 作者观点与抒情表述显式标注「作者观点」
  - 信源距离预判：媒体报道（厂商/平台转述）
  - P0 必核验项：数字/日期/人物身份/数学结论/Lean 验证声明
  - 勘误四张清单：日期版本表、成效数字溯源表、口径对照表、引文逐字核对表
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: facts.md 中 F 编号连续无跳号
  - `programmatic` TR-3.2: P0 项每项均有核验结论（✅/⚠️/❌）
  - `human-judgement` TR-3.3: 事实无推断词，观点与事实分层清晰
- **Completion Evidence**:
  - F 编号：F-001 ~ F-030，共 30 条，连续无跳号
  - P0 核验：11 项（4 ✅ / 7 ⚠️ / 0 ❌）
  - 勘误：3 条（Polymath 命名与年份偏差、Lean 形式化存疑、大小素数空隙语境混淆）
  - 作者观点：10 条，全部显式标注
- **Notes**: G1 质量门：事实阶段无因果推断词 ✅ 通过

## [x] T4：I 阶段 - 三层知识拆分 + 洞察分析
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T3
- **Description**: 
  - 事件时间线层（What/When/Who）→ concepts 首篇前部
  - 驱动逻辑/方法原理层（How/Why，含作者洞察须标注）→ 中部
  - 领域意义与趋势层 → 尾部
  - Mermaid 图：大素数空隙研究时间线
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-4.1: 三层知识拆分合理，事实与观点分层清晰
  - `human-judgement` TR-4.2: 洞察四元组完整（现象+根因+影响+建议）
- **Completion Evidence**:
  - 三层结构已落实：事件概览（时间线+人物）→ 方法与原理（问题背景+五人组方法+新进展+形式化验证）→ 领域意义与趋势（潜在影响+不确定性+后续关注）
  - Mermaid timeline 时间线图已嵌入概念文档
  - 作者观点显式标注，与客观事实分层
- **Notes**: G2 质量门：洞察四元组完整 ✅

## [x] T5：E 阶段 - 生成 bundle 文件
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T4
- **Description**: 
  - 信源先行：先写 references/（article-source.md + verification.md）
  - 再写 concepts/00-gpt56-prime-gap-breakthrough.md
  - 各级 index.md 最后写
  - 所有具体数字/结论引用 F 编号
  - frontmatter 遵循 OKF v0.2 规范
  - stale_after: 2026-11-04
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: 7 个文件全部生成
  - `programmatic` TR-5.2: frontmatter 必填字段完整
  - `human-judgement` TR-5.3: 信源先行顺序执行，F 编号引用正确
- **Completion Evidence**:
  - 7 个文件全部生成：index.md + concepts/index.md + 00-gpt56-prime-gap-breakthrough.md + references/index.md + article-source.md + verification.md + log.md
  - 所有文件 UTF-8 编码无 BOM、无乱码
  - frontmatter 必填字段（okf_version/title/description/status/stale_after）全部齐全
  - 信源先行：article-source.md / verification.md → 概念文档 → index → log，顺序正确
  - F-001 ~ F-030 共 30 条事实全部可追溯引用
- **Notes**: G3 质量门：模式可迁移（资讯速报骨架可复用）✅

## [x] T6：V 阶段 - 四视角对抗审查 + 机械门禁
- **Status**: `completed`
- **Priority**: high
- **Depends On**: T5
- **Description**: 
  - 四视角审查：事实溯源、结构规范、读者可用性、时效边界
  - 双份 F 编号一致性核对：facts.md vs article-source.md
  - 机械门禁：UTF-8、toctree 三级、相对链接、计数同步、敏感信息、frontmatter、勘误落实
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: 双份 F 编号集合相等且连续
  - `programmatic` TR-6.2: 三级 toctree 完整，条目文件存在
  - `programmatic` TR-6.3: 全部相对链接可达，无 file:///
  - `human-judgement` TR-6.4: 四视角审查无重大问题
- **Completion Evidence**:
  - CP-R1 ✅: 7 个 bundle 文件全部生成，UTF-8 编码无乱码
  - CP-R2 ✅: toctree 三级完整（根 → concepts/references → 文档），所有条目文件存在
  - CP-R3 ✅: 双份 F 编号一致（F-001~F-030，30 条，连续无跳号）
  - CP-R4 ✅: 全部内部链接使用相对路径，无 file:/// 绝对路径
  - CP-R6 ✅: 3 条勘误在 verification.md 和概念正文中均如实落实
  - CP-U1 评分: 4/5（事实溯源完整、观点与事实分层清晰、勘误落实到位；待同行验证项均已标注）
  - CP-U2 评分: 5/5（严格遵循 OKF v0.2，frontmatter/toctree/命名全部合规，资讯速报骨架标准）
- **Notes**: G4 质量门：行动项原子化（变更单一职责）✅

## [x] T7：索引收尾 + 提交
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: T6
- **Description**: 
  - 父分组 index 更新：kexue/math/index.md 3 → 4 bundles
  - 总索引更新：bundles/index.md total 500 → 501, kexue 域 16 → 17
  - 子模块内提交（bundle + 组 index + 总 index）
  - 主仓库提交 spec
  - 主仓库更新子模块指针
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-7.1: 三级计数同步（frontmatter/表格/toctree）
  - `programmatic` TR-7.2: git 提交记录完整，UTF-8 中文无乱码
- **Completion Evidence**:
  - CP-R5 ✅: 索引计数同步（总 501 / kexue 17 / math 4，frontmatter + 正文 + mermaid + 表格三面一致）
  - math/index.md: 知识包 3→4，描述更新，新增 bundle 条目与 toctree
  - kexue/index.md: math 分组描述更新为 4 束
  - bundles/index.md: total_bundles 500→501，kexue 16→17，mermaid 与表格同步更新
  - 注：git 提交待用户确认后执行
- **Notes**: 遵循 blog-article-to-okf-wiki Skill 的 C 阶段规范
