# Tasks：GPT-5.6 大素数空隙突破资讯 → OKF 知识包

> 方法论链路：R（事实采集）→ I（洞察分析）→ E（萃取生成）→ V（对抗审查）
> 场景：知识沉淀 - 博文转化 OKF 知识包

## [ ] T1：内容敏感度预检 + 文章内容获取
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 判定为公开内容（知乎专栏公开文章，无访问控制）
  - 使用 browser_use 子代理提取全文，已完成
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 文章正文完整提取（标题 + 约 3200 字正文）
  - `human-judgement` TR-1.2: 内容敏感度判定正确（公开内容 → 标准工作流）
- **Notes**: 已完成

## [ ] T2：骨架判定 + 归属决策
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
- **Notes**: math 分组现有 3 束均为经典阅读，本束为前沿资讯，性质互补

## [ ] T3：R 阶段 - 事实采集（F 编号）+ P0 核验
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
- **Notes**: G1 质量门：事实阶段无因果推断词

## [ ] T4：I 阶段 - 三层知识拆分 + 洞察分析
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
- **Notes**: G2 质量门：洞察四元组完整

## [ ] T5：E 阶段 - 生成 bundle 文件
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
- **Notes**: G3 质量门：模式可迁移（资讯速报骨架可复用）

## [ ] T6：V 阶段 - 四视角对抗审查 + 机械门禁
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
- **Notes**: G4 质量门：行动项原子化（变更单一职责）

## [ ] T7：索引收尾 + 提交
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
- **Notes**: 遵循 blog-article-to-okf-wiki Skill 的 C 阶段规范
