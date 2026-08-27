# Tasks: Jupyter Book v2 / MySTmd 生态系统 OKF Wiki 教程生成

> 工作流：R（事实采集）→ I（架构洞察）→ E（批量生成）→ V（独立验证）→ C（模式沉淀）
> 场景：知识沉淀（seven-concepts-cmd 场景4：R→I→E 链路）

## Phase R: 事实采集（所有知识束并行）

### Task R1: mystmd 核心引擎事实采集
- **Priority**: high
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 mystmd/packages 中 myst-parser、myst-transforms、myst-common、myst-config、myst-frontmatter、myst-spec、simple-validators、mystmd、mystmd-py、markdown-it-myst、citation-js-utils 的核心源码，提取编号事实清单
- **Test Requirements**:
  - **TR-R1-1 (rule)**: 输出 `bundles/jupyter-book/mystmd/spec/facts.md`，事实编号 F-001 起，无"用于"/"目的是"/"设计为"等推断词
  - **TR-R1-2 (rule)**: 覆盖核心导出类/函数/接口、模块依赖关系、数据流转路径、关键算法逻辑
  - **TR-R1-3 (rule)**: 每个事实标注源码路径（文件名+行号范围或函数名）

### Task R2: myst-cli 命令行工具事实采集
- **Priority**: high
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 myst-cli、myst-cli-utils、myst-migrate、myst-toc、myst-templates 源码，提取CLI命令、构建管线、项目加载、会话管理等事实
- **Test Requirements**:
  - **TR-R2-1 (rule)**: 输出 `bundles/jupyter-book/myst-cli/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R2-2 (rule)**: 覆盖 CLI 命令注册（commander/yargs）、build 多格式导出管线、start 开发服务器、init 模板、项目加载流程
  - **TR-R2-3 (rule)**: 每个事实标注源码路径

### Task R3: myst-syntax 语法扩展事实采集
- **Priority**: medium
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 myst-directives、myst-roles、8个 myst-ext-* 扩展包源码，提取指令注册、角色处理、UI组件实现等事实
- **Test Requirements**:
  - **TR-R3-1 (rule)**: 输出 `bundles/jupyter-book/myst-syntax/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R3-2 (rule)**: 覆盖指令插件架构、角色插件架构、每个核心指令/角色的 MDAST 节点类型、UI扩展组件props
  - **TR-R3-3 (rule)**: 每个事实标注源码路径

### Task R4: myst-exporters 多格式导出事实采集
- **Priority**: medium
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 myst-to-html/tex/docx/jats/md/typst、jtex、jats-to-myst、tex-to-myst 源码，提取各导出器实现和模板引擎事实
- **Test Requirements**:
  - **TR-R4-1 (rule)**: 输出 `bundles/jupyter-book/myst-exporters/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R4-2 (rule)**: 覆盖统一导出接口、各格式导出器核心类/函数、jtex模板渲染管线、导入转换器
  - **TR-R4-3 (rule)**: 每个事实标注源码路径

### Task R5: jupyter-book CLI事实采集
- **Priority**: medium
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 jupyter-book/py/jupyter_book/ 和 jupyter-book/ts/ 源码，提取Python入口、nodeenv管理、TS CLI命令等事实
- **Test Requirements**:
  - **TR-R5-1 (rule)**: 输出 `bundles/jupyter-book/jupyter-book/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R5-2 (rule)**: 覆盖 Python main() 函数、nodeenv 集成、TS CLI 命令（init/build/clean/site/templates）、与myst-cli的委托关系
  - **TR-R5-3 (rule)**: 每个事实标注源码路径

### Task R6: myst-execute与thebe事实采集
- **Priority**: medium
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 myst-execute 和 thebe/packages/core/lite/react 源码，提取代码执行和交互式运行的事实
- **Test Requirements**:
  - **TR-R6-1 (rule)**: 输出 `bundles/jupyter-book/myst-execute/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R6-2 (rule)**: 覆盖 myst-execute 内核管理/缓存/执行管线、thebe core API/配置/Binder连接、thebe lite Pyodide、thebe react hooks/Provider
  - **TR-R6-3 (rule)**: 每个事实标注源码路径

### Task R7: jupyterlab-myst事实采集
- **Priority**: low
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 jupyterlab-myst/src/ 源码，提取JupyterLab插件架构和MyST渲染事实
- **Test Requirements**:
  - **TR-R7-1 (rule)**: 输出 `bundles/jupyter-book/jupyterlab-myst/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R7-2 (rule)**: 覆盖插件激活、MIME类型注册、渲染器组件、widget集成
  - **TR-R7-3 (rule)**: 每个事实标注源码路径

### Task R8: myst-theme主题系统事实采集
- **Priority**: medium
- **AC Coverage**: AC-3, AC-7
- **Depends on**: None
- **Description**: 阅读 myst-theme/ 下 themes/、styles/、template/ 源码，提取主题架构和CSS组件事实
- **Test Requirements**:
  - **TR-R8-1 (rule)**: 输出 `bundles/jupyter-book/myst-theme/spec/facts.md`，事实编号 F-001 起，零推测
  - **TR-R8-2 (rule)**: 覆盖 Book/Article 主题差异、Remix路由结构、CSS组件库入口、模板服务器
  - **TR-R8-3 (rule)**: 每个事实标注源码路径

## Phase I: 架构洞察（所有知识束，依赖Phase R完成）

### Task I1: mystmd 核心引擎洞察
- **Priority**: high
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R1
- **Description**: 基于事实清单，提炼mystmd核心引擎的3-5个架构洞察
- **Test Requirements**:
  - **TR-I1-1 (rule)**: 输出 `bundles/jupyter-book/mystmd/spec/insights.md`
  - **TR-I1-2 (rule)**: 每个洞察包含陈述+证据（引用F-xxx编号）+反常识+行动四元组
  - **TR-I1-3 (rule)**: 设计知识地图：概念文档分组（入门/核心/高级）、学习路径、文档间依赖关系
  - **TR-I1-4 (rubric)**: 洞察深度评分0-2，≥1.5通过（洞察揭示非显而易见的架构决策或设计模式）

### Task I2: myst-cli命令行工具洞察
- **Priority**: high
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R2
- **Description**: 基于事实清单，提炼myst-cli的3-5个架构洞察
- **Test Requirements**:
  - **TR-I2-1 (rule)**: 输出 `bundles/jupyter-book/myst-cli/spec/insights.md`
  - **TR-I2-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I2-3 (rubric)**: 洞察深度≥1.5

### Task I3: myst-syntax语法扩展洞察
- **Priority**: medium
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R3
- **Description**: 基于事实清单，提炼myst-syntax的3-5个架构洞察
- **Test Requirements**:
  - **TR-I3-1 (rule)**: 输出 `bundles/jupyter-book/myst-syntax/spec/insights.md`
  - **TR-I3-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I3-3 (rubric)**: 洞察深度≥1.5

### Task I4: myst-exporters多格式导出洞察
- **Priority**: medium
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R4
- **Description**: 基于事实清单，提炼myst-exporters的3-5个架构洞察
- **Test Requirements**:
  - **TR-I4-1 (rule)**: 输出 `bundles/jupyter-book/myst-exporters/spec/insights.md`
  - **TR-I4-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I4-3 (rubric)**: 洞察深度≥1.5

### Task I5: jupyter-book CLI洞察
- **Priority**: medium
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R5
- **Description**: 基于事实清单，提炼jupyter-book CLI的2-3个架构洞察
- **Test Requirements**:
  - **TR-I5-1 (rule)**: 输出 `bundles/jupyter-book/jupyter-book/spec/insights.md`
  - **TR-I5-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I5-3 (rubric)**: 洞察深度≥1.5

### Task I6: myst-execute与thebe洞察
- **Priority**: medium
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R6
- **Description**: 基于事实清单，提炼myst-execute与thebe的3-5个架构洞察
- **Test Requirements**:
  - **TR-I6-1 (rule)**: 输出 `bundles/jupyter-book/myst-execute/spec/insights.md`
  - **TR-I6-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I6-3 (rubric)**: 洞察深度≥1.5

### Task I7: jupyterlab-myst洞察
- **Priority**: low
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R7
- **Description**: 基于事实清单，提炼jupyterlab-myst的2-3个架构洞察
- **Test Requirements**:
  - **TR-I7-1 (rule)**: 输出 `bundles/jupyter-book/jupyterlab-myst/spec/insights.md`
  - **TR-I7-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I7-3 (rubric)**: 洞察深度≥1.5

### Task I8: myst-theme主题系统洞察
- **Priority**: medium
- **AC Coverage**: AC-7, AC-9
- **Depends on**: R8
- **Description**: 基于事实清单，提炼myst-theme的3-5个架构洞察
- **Test Requirements**:
  - **TR-I8-1 (rule)**: 输出 `bundles/jupyter-book/myst-theme/spec/insights.md`
  - **TR-I8-2 (rule)**: 每个洞察包含四元组，设计知识地图
  - **TR-I8-3 (rubric)**: 洞察深度≥1.5

## Phase E: 批量生成OKF文档（依赖Phase I完成，信源先行、分批生成）

### Task E0: 创建Bundle目录结构与生态索引
- **Priority**: high
- **AC Coverage**: AC-1, AC-2
- **Depends on**: None（可与R/I并行准备）
- **Description**: 创建所有8个bundle的目录骨架和根索引
- **Test Requirements**:
  - **TR-E0-1 (rule)**: 创建 `bundles/jupyter-book/` 目录结构
  - **TR-E0-2 (rule)**: 每个子bundle包含 index.md、log.md、concepts/、examples/、references/、spec/ 目录
  - **TR-E0-3 (rule)**: 根 `bundles/jupyter-book/index.md` 含 okf_version frontmatter 和生态概览图（AC-1）
  - **TR-E0-4 (rule)**: 每个子bundle创建 log.md 初始版本

### Task E1: mystmd references信源生成（信源先行！）
- **Priority**: high
- **AC Coverage**: AC-3, AC-10
- **Depends on**: I1
- **Description**: 生成mystmd核心引擎的references信源文档
- **Test Requirements**:
  - **TR-E1-1 (rule)**: 生成 references/index.md（无frontmatter）
  - **TR-E1-2 (rule)**: 生成 5-8 个信源文档，每个文档 frontmatter 含 type: reference
  - **TR-E1-3 (rule)**: 信源文档覆盖核心源文件入口，含源码路径和关键API摘要
  - **TR-E1-4 (rule)**: 分批生成，每批≤7文件

### Task E2: mystmd concepts概念文档生成（分批）
- **Priority**: high
- **AC Coverage**: AC-3, AC-4, AC-10
- **Depends on**: E1
- **Description**: 按知识地图分2批生成mystmd概念文档
- **Test Requirements**:
  - **TR-E2-1 (rule)**: 生成 concepts/index.md（无frontmatter）
  - **TR-E2-2 (rule)**: 第一批（5-7篇）：整体架构、unified/micromark插件体系、MyST解析器、MDAST转换管线、公共类型
  - **TR-E2-3 (rule)**: 第二批（5-7篇）：配置系统、Frontmatter解析、MyST规范、验证器、Python绑定、markdown-it兼容层
  - **TR-E2-4 (rule)**: 每篇文档 frontmatter 完整，sources指向references/
  - **TR-E2-5 (rubric)**: 文档结构清晰、中文流畅、概念按学习路径递进≥1.5

### Task E3: mystmd examples示例文档生成
- **Priority**: high
- **AC Coverage**: AC-3, AC-4
- **Depends on**: E2
- **Description**: 生成mystmd实战示例
- **Test Requirements**:
  - **TR-E3-1 (rule)**: 生成 examples/index.md（无frontmatter）
  - **TR-E3-2 (rule)**: 生成 3-5 个示例文档，代码示例基于实际源码API
  - **TR-E3-3 (rule)**: 每个示例有完整可运行的代码片段和解释

### Task E4: myst-cli references+concepts+examples
- **Priority**: high
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I2
- **Description**: myst-cli信源先行，分2批概念+示例
- **Test Requirements**:
  - **TR-E4-1 (rule)**: references/ 先于 concepts/ 生成（3-5个信源）
  - **TR-E4-2 (rule)**: concepts/ 8-10篇（分2批，每批≤7）：CLI架构、build管线、start服务器、init、clean、项目加载与TOC、模板系统、版本迁移、会话缓存
  - **TR-E4-3 (rule)**: examples/ 3-4篇：初始化项目、构建站点、开发服务器、迁移项目
  - **TR-E4-4 (rule)**: 所有文档frontmatter完整，API引用Grep验证

### Task E5: myst-syntax references+concepts+examples
- **Priority**: medium
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I3
- **Description**: myst-syntax信源+概念+示例
- **Test Requirements**:
  - **TR-E5-1 (rule)**: references/ 3-4个信源
  - **TR-E5-2 (rule)**: concepts/ 7-9篇（分2批）：指令架构、角色架构、核心指令、核心角色、按钮卡片、网格标签图标、证明练习、响应式
  - **TR-E5-3 (rule)**: examples/ 2-3篇：使用核心指令、自定义指令、UI组件
  - **TR-E5-4 (rule)**: 所有文档frontmatter完整

### Task E6: myst-exporters references+concepts+examples
- **Priority**: medium
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I4
- **Description**: myst-exporters信源+概念+示例
- **Test Requirements**:
  - **TR-E6-1 (rule)**: references/ 3-4个信源
  - **TR-E6-2 (rule)**: concepts/ 7-9篇（分2批）：导出架构、HTML导出、LaTeX/PDF导出、DOCX导出、JATS导出、Markdown导出、Typst导出、jtex模板引擎、导入转换
  - **TR-E6-3 (rule)**: examples/ 2-3篇：多格式导出、自定义jtex模板、LaTeX导入
  - **TR-E6-4 (rule)**: 所有文档frontmatter完整

### Task E7: jupyter-book references+concepts+examples
- **Priority**: medium
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I5
- **Description**: jupyter-book信源+概念+示例
- **Test Requirements**:
  - **TR-E7-1 (rule)**: references/ 2-3个信源
  - **TR-E7-2 (rule)**: concepts/ 4-6篇：v2架构、Python入口与nodeenv、TS CLI命令、与myst-cli关系、模板系统
  - **TR-E7-3 (rule)**: examples/ 2篇：创建Book、构建发布
  - **TR-E7-4 (rule)**: 所有文档frontmatter完整

### Task E8: myst-execute references+concepts+examples
- **Priority**: medium
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I6
- **Description**: myst-execute+thebe信源+概念+示例
- **Test Requirements**:
  - **TR-E8-1 (rule)**: references/ 3-4个信源
  - **TR-E8-2 (rule)**: concepts/ 6-8篇（分2批）：执行架构、myst-execute内核管理、执行缓存、Thebe核心API、Thebe配置、Binder连接、Thebe Lite、React集成
  - **TR-E8-3 (rule)**: examples/ 2-3篇：配置Notebook执行、Thebe交互、Thebe Lite
  - **TR-E8-4 (rule)**: 所有文档frontmatter完整

### Task E9: jupyterlab-myst references+concepts+examples
- **Priority**: low
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I7
- **Description**: jupyterlab-myst信源+概念+示例
- **Test Requirements**:
  - **TR-E9-1 (rule)**: references/ 2个信源
  - **TR-E9-2 (rule)**: concepts/ 4-5篇：扩展架构、MyST渲染器、MIME处理、Widget集成、JupyterLab集成
  - **TR-E9-3 (rule)**: examples/ 1-2篇：在JupyterLab中使用MyST
  - **TR-E9-4 (rule)**: 所有文档frontmatter完整

### Task E10: myst-theme references+concepts+examples
- **Priority**: medium
- **AC Coverage**: AC-3, AC-4
- **Depends on**: I8
- **Description**: myst-theme信源+概念+示例
- **Test Requirements**:
  - **TR-E10-1 (rule)**: references/ 2-3个信源
  - **TR-E10-2 (rule)**: concepts/ 5-7篇：主题架构、Book主题、Article主题、CSS组件库、Remix路由、模板服务器、主题定制
  - **TR-E10-3 (rule)**: examples/ 2篇：定制Book主题、使用Article主题
  - **TR-E10-4 (rule)**: 所有文档frontmatter完整

### Task E11: 生成所有子bundle最终index.md（Index最后写！）
- **Priority**: high
- **AC Coverage**: AC-2
- **Depends on**: E2,E3,E4,E5,E6,E7,E8,E9,E10
- **Description**: 所有内容文档定稿后，统一更新各子bundle的concepts/index.md、examples/index.md、references/index.md和根index.md
- **Test Requirements**:
  - **TR-E11-1 (rule)**: 每个子bundle的 concepts/index.md 列出所有概念文档（无frontmatter）
  - **TR-E11-2 (rule)**: 每个子bundle的 examples/index.md 列出所有示例文档（无frontmatter）
  - **TR-E11-3 (rule)**: 每个子bundle的 references/index.md 列出所有信源文档（无frontmatter）
  - **TR-E11-4 (rule)**: 每个子bundle的 index.md 更新文档统计
  - **TR-E11-5 (rule)**: 确保无遗漏文档、无列出不存在文件

## Phase V: 独立验证（依赖Phase E完成）

### Task V1: Frontmatter规范检查
- **Priority**: high
- **AC Coverage**: AC-4
- **Depends on**: E11
- **Description**: 逐文件检查YAML frontmatter完整性和规范性
- **Test Requirements**:
  - **TR-V1-1 (rule)**: 每个非index.md/log.md的.md文件包含可解析YAML frontmatter
  - **TR-V1-2 (rule)**: frontmatter含 type/title/description/tags/generated/verified/status/stale_after/sources 字段
  - **TR-V1-3 (rule)**: type值为 concept/example/reference 之一
  - **TR-V1-4 (rule)**: 子目录index.md不含frontmatter，根index.md含okf_version
  - **TR-V1-5 (rule)**: 发现问题逐一修复

### Task V2: Grep级API真实性验证
- **Priority**: high
- **AC Coverage**: AC-5
- **Depends on**: E11
- **Description**: 对文档中引用的关键类名/函数名/接口名在源码中Grep验证
- **Test Requirements**:
  - **TR-V2-1 (rule)**: 每个知识束随机抽取≥10个引用的TS类/函数/接口/导出在源码中Grep验证
  - **TR-V2-2 (rule)**: 命中率100%，发现虚构API立即修正
  - **TR-V2-3 (rule)**: 记录验证结果（验证的API列表+Grep结果）

### Task V3: 交叉引用链接检查
- **Priority**: high
- **AC Coverage**: AC-6
- **Depends on**: E11
- **Description**: 检查所有内部交叉引用目标文件存在
- **Test Requirements**:
  - **TR-V3-1 (rule)**: 所有 /concepts/xxx.md、/examples/xxx.md、/references/xxx.md 链接目标存在
  - **TR-V3-2 (rule)**: 发现断链立即修复
  - **TR-V3-3 (rule)**: 路径使用 / 开头bundle-relative格式，无 ../ 相对路径

### Task V4: bundles总索引更新
- **Priority**: high
- **AC Coverage**: AC-8
- **Depends on**: V1,V2,V3
- **Description**: 更新bundles总索引，新增Jupyter Book生态分组
- **Test Requirements**:
  - **TR-V4-1 (rule)**: `bundles/index.md` 新增"📖 Jupyter Book v2 / MySTmd 生态"分组行
  - **TR-V4-2 (rule)**: 更新total_bundles计数（+8）和groups计数（+1，若新增分组）
  - **TR-V4-3 (rule)**: 分组详情表列出8个知识束简介
  - **TR-V4-4 (rule)**: 生态关系概览ASCII图更新，添加jupyter-book分支

### Task V5: 文档质量抽评
- **Priority**: medium
- **AC Coverage**: AC-9
- **Depends on**: V1,V2,V3
- **Description**: 从每个bundle中随机抽取2-3篇文档进行质量评估
- **Test Requirements**:
  - **TR-V5-1 (rubric)**: 文档可读性、结构清晰度、知识地图合理性评分0-2，平均≥1.5
  - **TR-V5-2 (rule)**: 中文表达流畅，术语首次出现有英文注释
  - **TR-V5-3 (rule)**: TypeScript类型签名准确，代码块标注语言
  - **TR-V5-4 (rule)**: 发现质量问题逐一修复

## Phase C: 模式沉淀（依赖Phase V通过）

### Task C1: 更新log.md变更日志
- **Priority**: low
- **AC Coverage**: AC-2
- **Depends on**: V5
- **Description**: 为每个子bundle的log.md添加本次生成记录
- **Test Requirements**:
  - **TR-C1-1 (rule)**: 每个log.md添加日期分组条目，记录知识束初始生成
  - **TR-C1-2 (rule)**: 包含生成方法（source-code-to-okf-wiki）和覆盖范围

---

## 任务依赖图

```
R1 ──┐  R2 ──┐  R3 ──┐  R4 ──┐  R5 ──┐  R6 ──┐  R7 ──┐  R8 ──┐
│     │  │     │  │     │  │     │  │     │  │     │  │     │  │     │
▼     ▼  ▼     ▼  ▼     ▼  ▼     ▼  ▼     ▼  ▼     ▼  ▼     ▼  ▼     ▼
I1    I2    I3    I4    I5    I6    I7    I8
│     │     │     │     │     │     │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
      │
      ▼
E0（目录结构，可与R/I并行）
      │
E1──►E2──►E3   E4   E5   E6   E7   E8   E9   E10
                  │
                  ▼
                E11（Index最后写）
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
       V1        V2        V3
        └─────────┼─────────┘
                  ▼
            V4 ──► V5
                  │
                  ▼
                 C1
```

## 执行顺序建议

1. **第一阶段（R）**：R1-R8 可并行委派（8个独立事实采集任务）
2. **第二阶段（I）**：I1-I8 可在对应R完成后并行
3. **第三阶段（E）**：
   - 先执行E0创建目录结构
   - 按依赖顺序：每个bundle先生成references（信源先行），再分2批concepts，最后examples
   - 最后执行E11统一写index
   - 8个bundle的E任务可并行委派（分批内串行，跨bundle并行）
4. **第四阶段（V）**：V1-V3可并行，V4依赖前三步，V5最后
5. **第五阶段（C）**：C1收尾

## 完成定义（DoD）

所有任务完成 + 所有TR通过 + Review结果为pass，且：
- 8个知识束共 ≥91 个内容文档（概念+示例+信源）
- 所有API引用经Grep验证无虚构
- 所有交叉引用无断链
- frontmatter 100% 合规
- bundles/index.md 总索引已更新
