---
version: "1.0"
x-toml-ref: "../../../../.meta/toml/.trae/specs/docs-restructure/categorize-learning-wiki-by-topic/spec.toml"
---
# docs/knowledge/learning 目录主题分类系统性划分 - Product Requirement Document

## Overview
- **Summary**: 对 `docs/knowledge/learning` 目录下的 60+ 份 Wiki 学习资料（包含 24 个已原子化的子目录 Wiki 和 35+ 个单文件 Wiki）按照知识主题进行系统性的二级分类划分，创建 8 个一级主题子目录，其中厂商产品学习系列按厂商再分二级子目录，建立主题导航索引，解决当前内容平铺导致的检索困难和认知负担问题。
- **Purpose**: 当前 learning 目录下所有 Wiki 内容平铺在同一层级（约 60+ 条目），随着内容持续积累，存在三个核心问题：（1）认知负担重——新用户无法快速定位感兴趣的主题领域；（2）主题边界模糊——基础概念、工程方法论、具体产品、商业分析混在一起，缺乏层次感；（3）系列内容分散——同一主题的相关 Wiki（如 Interface/API/ABI/Protocol、向日葵产品系列）缺乏物理聚合。通过系统性主题划分，实现知识的层次化组织，提升可发现性和可维护性。
- **Target Users**: AI 智能体开发者、项目维护者、知识库贡献者、使用学习资料的团队成员

## Goals
- 将 learning 目录下的所有 Wiki 按照知识主题划分为 8 个一级主题类别，建立清晰的分类体系
- 为每个主题类别创建独立子目录，实现同主题内容物理聚合
- 对厂商产品学习系列（向日葵、涂鸦）在主题目录下再按厂商建立二级子目录
- 设计主题编号前缀（01-08），体现从基础到应用、从技术到商业的认知递进顺序
- 创建 learning 目录的主题导航 README.md，提供分类总览和快速入口
- 创建 CATEGORIES.md 主题划分说明文档，详细列出每个主题的定义、边界、包含内容列表和划分依据
- 确保已原子化的 Wiki 目录作为整体迁移，保持其内部结构完整性
- 修复因目录移动产生的所有内部链接引用
- 更新 docs/knowledge/README.md 中的知识库索引

## Non-Goals (Out of Scope)
- 不对任何 Wiki 文件的内容实质进行修改
- 不改变已原子化 Wiki 目录的内部文件结构和命名
- 不新增或删除任何 Wiki 内容文件
- 不对未原子化的单文件 Wiki 进行原子化拆分（仅做分类迁移，原子化为独立任务）
- 不重新评估或更新 Wiki 的成熟度、质量标签
- 不改变 Wiki 之间的交叉引用逻辑（仅更新路径）
- 不调整 docs/knowledge 下其他目录（best-practices/、decisions/、operations/ 等）的结构

## Background & Context
- learning 目录目前存放了约 60+ 份 AI 技术学习资料，其中 24 个已完成原子化（每个是一个子目录，含多章节文件），其余为单文件 Wiki
- 现有 docs/knowledge/README.md 通过平铺列表展示所有内容，分类标签存在但未实现物理目录分组
- 部分内容已形成自然系列：Interface/API/ABI/Protocol 四层概念、向日葵贝锐科技产品系列（8篇+索引）、MyST Markdown 双份教程、Agent 协议四层栈
- 项目已完成多次文档重组（复盘报告分类、方法论模式分类、竹简悟道文档重组等），具备成熟的分类迁移经验和工具链（check-links.py、finalize-atomization.py、check-move.py）
- 现有文档重组遵循 docs-restructure 主题规范，有标准化的 tasks.md 任务模板和 checklist.md 验收清单
- 内容主题跨越多个维度：底层协议标准、工程方法论、具体产品工具、文档技术栈、多模态生成、商业分析、厂商产品、系统底层

## Functional Requirements
- **FR-1**: 在 learning 目录下创建 8 个一级主题子目录，使用两位数编号前缀（01-08）+ kebab-case 命名
- **FR-2**: 将 24 个已原子化 Wiki 目录整体迁移到对应主题子目录，保持内部结构不变
- **FR-3**: 将 35+ 个单文件 Wiki（含索引入口文件）迁移到对应主题子目录
- **FR-4**: 厂商产品学习系列在主题目录下建立二级厂商子目录（sunlogin/、tuya/）
- **FR-5**: 创建 learning/CATEGORIES.md 主题划分说明文档，包含分类原则、每个主题的定义与边界、完整的内容归属清单
- **FR-6**: 创建/更新 learning/README.md，建立主题导航总览，按一级主题分类展示所有 Wiki 入口
- **FR-7**: 保留已原子化 Wiki 目录下的 README.md（如有）作为该 Wiki 的内部导航
- **FR-8**: 修复所有因文件/目录移动产生的相对路径引用（包括 Wiki 内部交叉引用、上级索引引用）
- **FR-9**: 更新 docs/knowledge/README.md 中的 learning 部分，反映新的目录结构和主题分类
- **FR-10**: 运行链接检查工具验证所有链接有效性
- **FR-11**: 迁移完成后清理空目录

## Non-Functional Requirements
- **NFR-1**: 分类完成后，所有 Wiki 文件的 YAML frontmatter 元数据保持完整，无丢失或损坏
- **NFR-2**: 迁移操作必须保持原子性——按主题分批迁移，每批迁移后立即验证链接，避免中间状态导致大规模断链
- **NFR-3**: 主题目录命名遵循 `{两位数编号}-{kebab-case主题名}` 格式，与项目现有命名风格一致
- **NFR-4**: 分类后，查找特定主题 Wiki 的点击路径不超过 3 次（learning → 主题目录 → Wiki 入口）
- **NFR-5**: 所有跨文件引用 100% 修复，无断链
- **NFR-6**: 已原子化 Wiki 的内部章节导航链接（prev/next/directory）保持正确
- **NFR-7**: 迁移后 Git 能正确识别重命名操作（而非删除+新增），保留文件历史

## Constraints
- **Technical**:
  - 必须使用项目现有的文件移动验证脚本 `check-move.py` 辅助操作
  - 必须使用 `check-links.py --fix` 自动修复相对路径层级错误
  - 必须运行 `finalize-atomization.py` 完成断链修复和导航更新收尾
  - 迁移前需用 `build-ref-index.py` 构建引用索引，识别所有受影响文件
- **Business**:
  - 分类必须基于知识内容的核心主题，而非创建时间、作者或成熟度
  - 每个 Wiki 唯一归属一个一级主题，避免重复放置
  - 编号顺序体现认知递进：基础协议 → 工程方法 → 平台工具 → 文档技术 → 内容生成 → 商业趋势 → 厂商系列 → 系统底层
- **Dependencies**:
  - 依赖现有的 finalize-atomization.py 脚本进行断链修复
  - 依赖 check-links.py 进行链接验证
  - 依赖 check-move.py 进行迁移完整性验证
  - 依赖 build-ref-index.py 进行引用影响范围分析

## Assumptions
- 所有 Wiki 内容已完整，无需内容修改
- 8 个一级主题类别已能覆盖所有现有内容，无需设"其他/misc"类别
- 已原子化 Wiki 的根目录同名 .md 文件是该 Wiki 的入口/导航文件，应与对应原子化目录放在同一主题下
- 向日葵产品系列索引（sunlogin-product-series-index.md）应作为该系列的入口，与其他向日葵 Wiki 聚合在一起
- 文件移动后，Git 能够正确识别重命名操作
- 二级子目录（厂商子目录）仅在厂商产品系列主题下使用，其他主题保持一级结构

## Acceptance Criteria

### AC-1: 8个一级主题子目录创建完成
- **Given**: learning 目录当前所有内容平铺
- **When**: 执行分类划分
- **Then**: learning 目录下应存在 8 个一级主题子目录，名称格式为 `{两位数编号}-{kebab-case}`，编号从 01 到 08
- **Verification**: `programmatic`
- **Notes**: 通过目录列举验证目录存在且命名规范

### AC-2: 所有Wiki正确归类到对应主题
- **Given**: 8 个主题子目录已创建
- **When**: 完成文件和目录迁移
- **Then**: 所有 24 个原子化 Wiki 目录和 35+ 个单文件 Wiki 全部位于对应主题子目录中，根目录仅保留 README.md 和 CATEGORIES.md
- **Verification**: `programmatic`
- **Notes**: 文件数量核对：迁移前后文件总数一致；按主题统计文件数之和等于总数

### AC-3: 每个Wiki唯一归属一个主题
- **Given**: 迁移完成
- **When**: 检查文件分布
- **Then**: 每个 Wiki（原子化目录或单文件）只存在于一个主题子目录中，无重复、无遗漏
- **Verification**: `programmatic`
- **Notes**: 无文件同时出现在多个主题目录

### AC-4: 厂商产品系列二级子目录正确建立
- **Given**: 厂商产品主题目录已创建
- **When**: 迁移向日葵和涂鸦系列内容
- **Then**: 厂商产品主题目录下存在 sunlogin/ 和 tuya/ 二级子目录，系列索引文件位于厂商子目录入口
- **Verification**: `programmatic`

### AC-5: 已原子化Wiki内部结构完整
- **Given**: 原子化 Wiki 目录迁移完成
- **When**: 检查已原子化 Wiki 的内部文件
- **Then**: 每个原子化 Wiki 目录内的章节文件、子目录（examples/、appendix/ 等）保持原有结构和命名，无丢失无损坏
- **Verification**: `programmatic`

### AC-6: CATEGORIES.md内容完整
- **Given**: 分类完成
- **When**: 查看 CATEGORIES.md
- **Then**: 文档应包含：（1）分类设计原则与划分依据；（2）8个主题的详细定义、核心主题词、边界说明、认知定位；（3）每个主题下列出所有包含的 Wiki（带链接和一句话说明）；（4）主题间的关联关系和推荐学习路径
- **Verification**: `human-judgment`

### AC-7: learning/README.md主题导航完整
- **Given**: 分类完成
- **When**: 查看 learning/README.md
- **Then**: README 应包含：（1）learning 知识库简介和统计数字（Wiki总数、主题数）；（2）8个主题的导航表格，每个主题有编号、名称、一句话描述、Wiki数量；（3）每个主题下的 Wiki 快速链接列表；（4）推荐学习路径建议
- **Verification**: `human-judgment`

### AC-8: 所有内部链接正确无误
- **Given**: 文件迁移和链接修复完成
- **When**: 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning --fix`
- **Then**: 检查结果显示 0 个断链，所有相对路径正确（特别注意目录深度变化导致的 `../` 层级调整）
- **Verification**: `programmatic`

### AC-9: Wiki内部章节导航正确
- **Given**: 链接修复完成
- **When**: 抽查已原子化 Wiki 的章节导航（prev/next/directory 链接）
- **Then**: 原子化 Wiki 内的章节间导航链接正确指向对应章节文件，目录链接正确指向对应位置
- **Verification**: `programmatic`

### AC-10: 上层文档索引同步更新
- **Given**: 链接修复完成
- **When**: 检查 docs/knowledge/README.md
- **Then**: 该文件中对 learning 目录下 Wiki 的引用路径已更新为新的主题子目录结构
- **Verification**: `programmatic`

### AC-11: 跨目录引用验证通过
- **Given**: 所有修复完成
- **When**: 运行全量链接检查 `python .agents/scripts/check-links.py --path docs/knowledge`
- **Then**: 整个 docs/knowledge 目录下无断链
- **Verification**: `programmatic`

### AC-12: Wiki元数据完整性保持
- **Given**: 分类完成
- **When**: 抽查若干 Wiki 文件的 YAML frontmatter
- **Then**: 所有 Wiki 文件的 frontmatter（id、title、tags、date、summary 等字段）保持完整，无损坏
- **Verification**: `programmatic`

### AC-13: 空目录已清理
- **Given**: 迁移完成
- **When**: 检查 learning 目录
- **Then**: 迁移后遗留的空目录已清理，无残留空目录
- **Verification**: `programmatic`

## 主题划分方案

### 分类设计原则

1. **认知递进原则**：主题编号（01-08）体现从基础到应用、从技术到商业的学习路径：底层标准 → 工程方法 → 平台工具 → 文档技术 → 内容生成 → 商业趋势 → 厂商案例 → 系统底层
2. **知识内聚原则**：同一主题的 Wiki 在知识层面高度相关，阅读一个后自然引导到同主题其他 Wiki
3. **唯一归属原则**：每个 Wiki 只属于一个主题，避免重复放置造成维护困难
4. **系列聚合原则**：同一厂商/产品系列的 Wiki 物理聚合，方便系统性学习
5. **粒度均衡原则**：各主题包含的 Wiki 数量相对均衡（5-12个），避免过大主题（>15个）或过小主题（<3个）
6. **面向检索原则**：主题命名直观反映内容领域，用户看到主题名即可判断内容范围

### 8个一级主题详细定义

| 编号 | 主题目录名 | 主题名称 | 包含 Wiki 数 | 核心内容 | 认知定位 |
|------|-----------|---------|------------|---------|---------|
| 01 | 01-agent-protocols-interfaces | Agent协议与接口技术栈 | ~10 | MCP/ACP/A2A/ANP、Interface/API/ABI/Protocol、IDL、FFI、TVM FFI、Agent Runtime、Skills标准、国内MCP生态 | 基础层：互操作标准与接口抽象 |
| 02 | 02-agent-engineering-methodology | Agent工程方法论 | ~6 | Harness Engineering、四代工程概念、Karpathy准则、上下文压缩、Vibe Coding Prompt、LongCat Loop Engineering | 方法层：AI工程范式与实践准则 |
| 03 | 03-agent-platforms-tools | Agent平台与工具生态 | ~12 | Anthropic Agent路线图、金融Agent、Claude Tag、EchoBird、BrowserAct、Open Code Review、MopMonk安全、Octo平台、Rainman翻译、The Agency、AReaL强化学习、QuantDinger量化 | 应用层：具体Agent平台与开源工具 |
| 04 | 04-docs-markup-tooling | 文档工具链与标记语言 | ~4 | MyST Markdown指南、MyST Markdown教程、scikit-build-core构建、HTML声明式局部更新 | 工具层：文档技术与开发工具 |
| 05 | 05-ai-multimodal-content | AI多模态与内容生成 | ~5 | Agnes/Pavo短剧平台、AudioX音频生成、LibTV AI短剧、Text-to-CAD、Anime.js+Three.js动画 | 内容层：AIGC与多模态生成 |
| 06 | 06-business-trends-analysis | AI商业与趋势观察 | ~5 | AI变现方法论、Papi酱个人IP趋势、KickArt营销分析、国产LLM对比、三大AI工具分析 | 商业层：商业化与行业趋势 |
| 07 | 07-vendor-product-learning | 厂商产品学习系列 | ~11 | 向日葵贝锐系列（8篇+索引+Oray矩阵）、涂鸦TuyaOpen系列（3篇） | 案例层：按厂商组织的产品深度学习 |
| 08 | 08-systems-infrastructure | 底层系统与基础设施 | ~2 | WSL CLI架构、WSL学习计划 | 系统层：操作系统与底层基础设施 |

### 主题间关联关系与推荐学习路径

```
01-agent-protocols-interfaces（基础标准）
    ↓ 为Agent实现提供互操作基础
02-agent-engineering-methodology（工程方法）
    ↓ 指导Agent平台的设计与使用
03-agent-platforms-tools（平台工具）
    ↕ 平行关系
04-docs-markup-tooling（文档技术）  05-ai-multimodal-content（内容生成）
    ↓ 产品商业落地
06-business-trends-analysis（商业趋势）
    ↑ 案例支撑
07-vendor-product-learning（厂商案例）
    ↕ 底层支撑
08-systems-infrastructure（系统基础）
```

**推荐入门路径**：01 → 02 → 03 → 按需选择 04/05/06/07
**垂直领域路径**：07-vendor-product-learning 可结合 03 和 06 交叉学习
**底层技术路径**：08 → 01 → 02 → 03

## Open Questions
- [ ] dspark-paper-wiki.md 和 ian-xiaohei-illustrations.md 因未查看内容，暂时归入 06-business-trends-analysis（如内容不符则在实施时调整）
- [ ] 国内 Skill/MCP 生态盘点（domestic-skill-mcp-ecosystem-wiki.md）归入 01（协议标准生态）而非 03（平台工具），是否合理？——按分类原则，生态盘点属于标准协议范畴，归入 01 更合适
- [ ] 04-docs-markup-tooling 主题目前只有 4 个 Wiki，是否考虑将 animejs-threejs-adapter-analysis.md（前端动画）归入 04？——animejs/threejs 属于前端图形/动画技术，与文档工具链关联较弱，仍归入 05 多模态内容更合适
- [ ] 是否需要在每个主题子目录下创建独立的 README.md？——初步决定：不创建，统一在根目录 README.md 和 CATEGORIES.md 维护导航，避免增加维护负担
