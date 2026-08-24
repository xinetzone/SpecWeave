# Executable Books 生态 OKF Wiki 教程 - Product Requirements Document

## Overview
- **Summary**: 为 Executable Books 组织（executablebooks）下的全部实质性开源子项目生成 OKF v0.2 规范的系统化中文源码 Wiki 教程，放置在 `projects/awesome-okf-xs/bundles/myst/` 分组下。
- **Purpose**: Executable Books 是 Jupyter Book、MyST Markdown 等现代技术文档工具链的核心组织，其项目涵盖 Markdown 解析、Sphinx 扩展、Notebook 执行缓存、主题设计等关键组件。通过源码级深度阅读生成可验证的中文 Wiki，填补中文生态对这一工具链的系统化知识空白。
- **Target Users**: 需要理解 MyST Markdown 原理、开发 Sphinx 扩展、定制 Jupyter Book、使用 Executable Books 工具链构建技术文档的中文开发者和技术写作者。

## Goals
- 为 Executable Books 下 19 个实质性子项目（排除纯组织文档的 `meta`）生成 OKF v0.2 规范 Wiki
- 创建新分组 `myst/`（MyST Markdown 与 Executable Books 生态），包含分组 index.md
- 每个子项目生成独立 bundle，包含 concepts/、examples/、references/、spec/（facts.md + insights.md）、index.md、log.md
- 所有 API 引用经 Grep 级源码验证，杜绝虚构 API
- 更新 bundles/index.md 总索引，加入 myst 分组

## Non-Goals
- 不为 `meta` 子项目生成 bundle（纯组织文档仓库，无实质代码）
- 不修改 vendor/ 下的源码（只读学习）
- 不生成英文文档（仅中文）
- 不对已存在于 sphinx/ 分组的项目做重复迁移（executablebooks 的 Sphinx 扩展统一放在 myst/ 分组下，保持生态内聚性）
- 不做 C 阶段模式萃取入库（本次任务以文档生成为主，模式沉淀可作为后续任务）

## Background & Context
- 源码位置：`external/libs/ai/executablebooks/`（git submodule，只读）
- 输出位置：`projects/awesome-okf-xs/bundles/myst/`
- 已有参考：onnx/ 分组 8 个 bundle（150 文件）、sphinx/ 分组 10 个 bundle 均已按 OKF v0.2 规范完成
- 方法论：使用 `source-code-to-okf-wiki` Skill 的 R→I→E→V→C 五阶段链路，由 `seven-concepts-cmd` 元编排引擎协调
- 参考模板：onnx/onnx/、sphinx/alabaster/ 等已完成 bundle 的结构和格式

### 子项目分类与分层

Executable Books 19 个子项目按技术层次分为 5 组：

**1. MyST 解析核心层（Markdown 解析基础设施）**
| 项目 | 一句话定位 |
|------|-----------|
| markdown-it-py | Python 版 markdown-it 解析器（CommonMark 兼容，MyST 的 Markdown 解析底座） |
| mdurl | Markdown URL 编码/解码/格式化工具库 |
| mdit-py-plugins | markdown-it-py 插件集合（GFM、脚注、容器等） |

**2. MyST Sphinx 集成层（Sphinx 中的 Markdown + Notebook）**
| 项目 | 一句话定位 |
|------|-----------|
| MyST-Parser | MyST Markdown 的 Sphinx 解析器扩展（docutils+Sphinx 集成） |
| MyST-NB | MyST 对 Jupyter Notebook 的支持（执行缓存+渲染+Glue 跨单元格引用） |

**3. 格式化与迁移工具层**
| 项目 | 一句话定位 |
|------|-----------|
| mdformat-myst | mdformat 的 MyST 语法支持插件 |
| mdformat-footnote | mdformat 的脚注语法支持插件 |
| rst-to-myst | reStructuredText → MyST Markdown 转换工具 |

**4. Sphinx 扩展套件（Jupyter Book 生态 UI/UX 组件）**
| 项目 | 一句话定位 |
|------|-----------|
| sphinx-book-theme | Jupyter Book 主题（基于 pydata-sphinx-theme 深度定制） |
| sphinx-design | 设计组件扩展（卡片/网格/标签页/下拉/徽章/按钮） |
| sphinx-copybutton | 代码块一键复制按钮 |
| sphinx-togglebutton | 内容折叠/切换按钮 |
| sphinx-tabs | 标签页组件 |
| sphinx-exercise | 练习/答案指令环境 |
| sphinx-proof | 证明/定理/推论/公理等数学环境 |
| sphinx-external-toc | 外部目录（_toc.yml 驱动站点导航结构） |

**5. 基础设施工具层**
| 项目 | 一句话定位 |
|------|-----------|
| jupyter-cache | Jupyter Notebook 执行缓存（MyST-NB 的执行后端依赖） |
| github-activity | GitHub 活动 changelog CLI 生成工具 |
| web-compile | Web 资源编译器（SCSS→CSS、JS 压缩，主题开发用） |

## Functional Requirements
- **FR-1**: 为 19 个子项目各生成一个 OKF v0.2 bundle，包含标准目录结构（concepts/、examples/、references/、spec/）
- **FR-2**: 每个 bundle 的 spec/ 目录包含 facts.md（编号事实清单 F-xxx，零推测）和 insights.md（3-5 个架构洞察四元组）
- **FR-3**: 每个 bundle 的 references/ 目录包含信源登记文件，先于 concepts/ 生成
- **FR-4**: 每个 bundle 的 concepts/ 包含按学习路径编号的概念文档（00-introduction 起步）
- **FR-5**: 每个 bundle 的 examples/ 包含可运行的实战示例文档
- **FR-6**: 创建 myst/ 分组根 index.md，包含生态概览、知识束表格、推荐学习路径、生态关系图
- **FR-7**: 更新 bundles/index.md 总索引，将 myst 分组加入分组导航和分组详情
- **FR-8**: 文档交叉链接统一使用 `/` 开头的 bundle-relative 路径
- **FR-9**: 每个内容文档（concepts/examples/references 下非 index.md）包含完整 YAML frontmatter（type、title、description、tags、generated、verified、status、stale_after、sources）

## Non-Functional Requirements
- **NFR-1**: 所有 API 引用必须经 Grep 源码验证存在性，零虚构 API
- **NFR-2**: 内部链接零断链（link-check 验证）
- **NFR-3**: frontmatter 字段完整率 100%（所有非保留 .md 文件含有效 YAML frontmatter 和非空 type 字段）
- **NFR-4**: 文档正文使用中文撰写，英文技术术语首次出现时括号注释
- **NFR-5**: 每批生成文档数 ≤ 7，防止上下文过载
- **NFR-6**: 每个 bundle 的内容文档数（concepts + examples + references 非 index 文件）根据项目规模调整：核心项目（markdown-it-py、MyST-Parser、MyST-NB、sphinx-book-theme、sphinx-design、jupyter-cache）15-30 篇；中等项目 8-15 篇；小型工具项目 3-8 篇

## Constraints
- **Technical**: 源码位于 git submodule 中（external/libs/ai/executablebooks/），只读访问；输出写入 projects/awesome-okf-xs/bundles/myst/
- **Business**: 遵循 OKF v0.2 规范；遵循 awesome-okf-xs 项目的 frontmatter 规范和目录约定
- **Dependencies**: source-code-to-okf-wiki Skill 五阶段流程、seven-concepts-cmd 元编排、Grep API 验证、link-check 链接检查

## Assumptions
- executablebooks 各子项目的 git submodule 已初始化且可访问
- 用户同意创建新分组 `myst/` 而非将 executablebooks 的 Sphinx 扩展放入已有 sphinx/ 分组
- 小型工具项目（mdformat-footnote、mdformat-myst、mdurl、github-activity、web-compile、sphinx-copybutton、sphinx-togglebutton）生成精简版 bundle（3-5 篇概念+示例+1-2 篇信源即可）
- 核心项目（markdown-it-py、MyST-Parser、MyST-NB、sphinx-book-theme、sphinx-design、jupyter-cache）生成完整版 bundle

## Acceptance Criteria

### AC-1: myst 分组结构完整性
- **Type**: `rule`
- **Given**: 所有 19 个子项目的 bundle 已生成
- **When**: 检查 myst/ 目录结构
- **Then**: myst/ 下包含 19 个子项目目录（markdown-it-py、mdurl、mdit-py-plugins、MyST-Parser、MyST-NB、mdformat-myst、mdformat-footnote、rst-to-myst、sphinx-book-theme、sphinx-design、sphinx-copybutton、sphinx-togglebutton、sphinx-tabs、sphinx-exercise、sphinx-proof、sphinx-external-toc、jupyter-cache、github-activity、web-compile），每个包含 index.md、log.md、concepts/、examples/、references/、spec/
- **Pass Condition**: 19 个 bundle 目录均存在且包含标准 OKF 子目录和文件
- **Evidence**: 文件系统目录列表

### AC-2: 事实与洞察质量
- **Type**: `rule`
- **Given**: R 阶段事实采集和 I 阶段架构洞察已完成
- **When**: 检查每个 bundle 的 spec/facts.md 和 spec/insights.md
- **Then**: 每个 facts.md 包含编号事实 F-xxx，零推断性表述（无"用于"/"目的是"等）；每个 insights.md 包含 3-5 个洞察四元组（陈述+证据+反常识+行动）
- **Pass Condition**: 19 个 facts.md 和 19 个 insights.md 均存在且符合质量门 G1、G2
- **Evidence**: 文件内容检查

### AC-3: API 真实性验证
- **Type**: `rule`
- **Given**: E 阶段文档生成完成
- **When**: 对文档中引用的每个类名、函数名、方法名执行 Grep 源码验证
- **Then**: 所有引用的 API 在源码中可找到，零虚构
- **Pass Condition**: Grep 验证通过率 100%，发现虚构 API 立即修复
- **Evidence**: Grep 验证命令输出记录

### AC-4: 链接有效性
- **Type**: `rule`
- **Given**: 所有文档已生成
- **When**: 执行链接检查
- **Then**: 所有内部交叉链接可解析，零断链
- **Pass Condition**: link-check 报告零断链
- **Evidence**: link-check 输出

### AC-5: Frontmatter 合规性
- **Type**: `rule`
- **Given**: 所有 .md 文件已生成
- **When**: 解析每个非保留 .md 文件的 YAML frontmatter
- **Then**: 每个文件包含可解析 YAML frontmatter，type 字段非空，保留文件（index.md 仅 bundle 根带 okf_version、log.md）遵循对应结构
- **Pass Condition**: 100% 文件 frontmatter 合规
- **Evidence**: frontmatter 解析验证结果

### AC-6: 文档质量与学习路径合理性
- **Type**: `rubric`
- **Dimension**: 知识组织的清晰度与学习价值
- **Scale**: 1-5
- **Anchors**: 1 = 文档堆砌无结构、概念跳跃难以理解；3 = 结构基本清晰但有部分逻辑断层、示例与概念脱节；5 = 概念层层递进、示例紧贴概念、交叉引用准确、读完后能独立使用该项目
- **Pass Threshold**: >= 4
- **Evidence**: 独立评审抽样阅读 3 个核心项目 + 2 个小型项目的文档，评估知识组织和学习路径

### AC-7: 总索引更新
- **Type**: `rule`
- **Given**: myst/ 分组完成
- **When**: 检查 bundles/index.md
- **Then**: bundles/index.md 包含 myst 分组条目，分组计数更新，生态关系图中体现 myst 位置
- **Pass Condition**: bundles/index.md 中 groups 数量从 11 更新为 12，total_bundles 从 44 更新为 63
- **Evidence**: bundles/index.md 内容检查

## Open Questions
- [ ] 是否需要为 mdformat-footnote 和 mdformat-myst 这两个非常小的插件项目（各自仅几十行代码）生成完整版 bundle，还是合并为一个 mdformat-plugins bundle？
