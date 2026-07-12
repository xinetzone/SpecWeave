# 第一性原理交互式知识图谱 - Product Requirement Document

## Overview

- **Summary**: 构建一个基于第一性原理知识档案现有数据的交互式知识图谱可视化页面。通过Python脚本从06-concepts-glossary.md（24个核心概念）、07-timeline.md（19个历史节点、10位关键人物、4个时期）等Markdown文件中提取结构化数据（概念关系、人物传承、时间序列、文档引用），生成一个自包含的HTML文件（使用vis-network力导向图库），支持节点点击、悬停提示、按类型筛选、搜索、跳转到源文档等交互功能。

- **Purpose**: 当前知识档案包含12个Markdown文件、92个来源、24个核心概念、19个历史节点、10位关键人物，概念之间的关联通过file:///链接隐式表达，但读者无法在"一览全局"的层面看到整个知识网络结构。线性阅读无法直观呈现"第一性原理"概念从古希腊哲学→近代认识论→现代物理学→当代商业的跨领域传承关系，以及"演绎/归纳/类比"等核心概念之间的对立互补关系。知识图谱让这些隐性网络结构显性化、可探索，帮助读者建立系统性理解而非碎片化记忆。

- **Target Users**: 第一性原理知识档案的读者（哲学/理论研究者、物理/工程背景读者、商业/创新实践者、方法论研究者），以及档案维护者（图谱可作为内容完整性检查的辅助工具）。

## Goals

- 从现有Markdown文件中自动提取概念、人物、事件、时期、文档五类节点及其关系
- 生成单个自包含HTML文件（CSS/JS内联或CDN引用），双击即可在浏览器中打开
- 力导向图布局呈现知识网络，节点按类型/领域颜色编码
- 点击节点显示详情面板（定义/摘要、可信度评级、源文档链接）
- 按节点类型和领域筛选（显示/隐藏某类节点）
- 搜索节点名称快速定位
- 点击节点高亮其一跳邻居，便于追踪关系链
- 脚本可重复运行，当知识档案内容更新时重新生成即可

## Non-Goals (Out of Scope)

- 不做在线/服务端部署（纯静态HTML，本地打开使用）
- 不做图谱编辑功能（只读可视化，不支持增删改节点/关系）
- 不做自动语义关系提取（关系数据来源于已有结构化表格和人工补充，不做NLP/LLM自动提取）
- 不做引用网络可视化（92个来源之间的引用关系不在MVP范围内）
- 不做跨知识库扩展（仅覆盖first-principles目录，不扩展到其他知识领域）
- 不做复杂图谱分析算法（最短路径、社区发现、中心性计算等不在MVP范围）
- 不做移动端适配优先（桌面浏览器优先，移动端基本可用即可）

## Background & Context

知识档案当前结构：
- [06-concepts-glossary.md](../../../../docs/knowledge/learning/first-principles/06-concepts-glossary.md)：核心概念术语表，包含24个概念，表格中"相关概念"列通过file:///链接显式定义了概念间关系，"所属领域"列标注了哲学/物理学/方法论/认知科学等分类
- [07-timeline.md](../../../../docs/knowledge/learning/first-principles/07-timeline.md)：发展时间线，包含19个历史节点、4个时期、10位关键人物传承关系表，Mermaid流程图展示跨领域传承脉络
- [README.md](../../../../docs/knowledge/learning/first-principles/)：文件导航表，定义了12个文档的标题、简介、难度、阅读顺序
- [04-key-thinkers-quotes.md](../../../../docs/knowledge/learning/first-principles/04-key-thinkers-quotes.md)：核心人物论述

项目已有自包含HTML产物先例：[竹简悟道_完整版.html](../../../../apps/zhujian-wudao/竹简悟道_完整版.html)采用CSS/JS内联的单文件模式。

项目脚本开发规范见 [lib/README.md](../../../../.agents/scripts/lib/)，现有脚本如 [check-links.py](../../../../.agents/scripts/check-links.py) 可作为Python脚本结构参考。

## Functional Requirements

- **FR-1**: 脚本能够从06-concepts-glossary.md的概念术语表中提取24个概念节点（名称、英文名、定义摘要、所属领域、可信度评级、源文档锚点）
- **FR-2**: 脚本能够从06-concepts-glossary.md的"相关概念"列提取概念间的`related_to`关系（通过解析file:///链接和锚点匹配概念名）
- **FR-3**: 脚本能够从07-timeline.md的时间线节点索引表中提取19个事件节点（时间、名称、所属时期、重要程度）
- **FR-4**: 脚本能够从07-timeline.md的关键人物传承表中提取10位人物节点（姓名、时期、核心贡献）
- **FR-5**: 脚本能够从07-timeline.md的跨领域Mermaid流程图中提取人物/事件间的`influenced`传承关系
- **FR-6**: 脚本能够从README.md文件导航表中提取12个文档节点（文件名、标题、简介、难度）
- **FR-7**: 脚本需包含人工补充的关系数据模块（用于Mermaid图表中无法自动解析的跨文档概念-文档归属关系、人物-概念贡献关系），以Python字典形式内嵌在脚本中
- **FR-8**: 生成自包含HTML文件，使用vis-network.js（CDN引入）渲染力导向图
- **FR-9**: 节点按类型和领域进行颜色编码：Concept按领域（哲学/物理/方法论/认知科学=4色），Person/Event/Document/Period各一种颜色
- **FR-10**: 点击节点显示详情面板：概念节点显示定义摘要+可信度+相关概念列表+源文档链接；人物节点显示核心贡献+时期+源链接；事件节点显示时间+时期+重要程度+源链接
- **FR-11**: 悬停节点显示Tooltip（名称+类型标签）
- **FR-12**: 支持按节点类型筛选（复选框控制显示/隐藏Concept/Person/Event/Document/Period）
- **FR-13**: 支持按概念领域筛选（哲学/物理/方法论/认知科学/通用）
- **FR-14**: 支持搜索框按名称模糊搜索定位节点
- **FR-15**: 点击节点高亮其一跳邻居节点和边，淡化非关联节点
- **FR-16**: 点击源文档链接可跳转到对应的Markdown文件锚点位置
- **FR-17**: 图布局使用vis-network的force-directed physics（物理仿真），支持拖拽节点固定位置
- **FR-18**: 脚本输出信息报告（提取到的节点数、关系数、警告信息如无法匹配的链接）

## Non-Functional Requirements

- **NFR-1**: HTML文件在浏览器中打开后5秒内完成初始渲染（约50-70个节点、100-150条边的规模）
- **NFR-2**: 生成的HTML文件大小不超过200KB（不含CDN库，CDN加载失败时显示友好提示）
- **NFR-3**: 脚本遵循现有Python脚本规范：使用标准库（urllib不需要，本次为纯文本解析，使用re/json/pathlib/argparse即可），复用lib.cli输出函数
- **NFR-4**: 脚本幂等：相同输入产生相同输出（不依赖网络、不依赖时间戳）
- **NFR-5**: CDN不可用时（离线环境）显示提示信息告知用户需要联网加载vis-network库，并提供Mermaid静态图降级方案
- **NFR-6**: 代码遵循"不超过500行"规则，如逻辑复杂则提取为lib/模块

## Constraints

- **Technical**: Python 3.x 标准库（不引入第三方Python包）；前端使用vis-network.js（通过CDN引入，MIT许可）；输出为单个HTML文件；脚本遵循[.agents/scripts/lib/README.md](../../../../.agents/scripts/lib/)规范
- **Business**: 输出文件放在`docs/knowledge/learning/first-principles/`目录下，文件名为`12-knowledge-graph.html`；README.md文件导航表需要更新以包含新文件
- **Dependencies**: 依赖现有知识档案Markdown文件结构不发生破坏性变更（表格列顺序、标题层级变化会影响解析，脚本需有容错处理）；依赖vis-network CDN可用性

## Assumptions

- vis-network CDN（unpkg或jsDelivr）在用户浏览器环境中可访问
- 用户使用现代桌面浏览器（Chrome/Firefox/Edge）打开HTML文件
- 知识档案的Markdown表格结构短期内不会大幅变动
- file:///协议链接在浏览器中可正常打开本地Markdown文件（部分浏览器可能限制，需提示）
- MVP阶段概念间关系以显式链接为主，不追求关系网的绝对完整性，缺失关系可在后续迭代中补充

## Acceptance Criteria

### AC-1: 概念节点正确提取
- **Given**: 06-concepts-glossary.md包含24个概念术语表
- **When**: 运行生成脚本
- **Then**: HTML中包含24个Concept类型节点，每个节点有名称、领域、可信度颜色标记
- **Verification**: `programmatic`
- **Notes**: 通过脚本stdout输出"提取到24个概念节点"确认

### AC-2: 概念关系正确提取
- **Given**: 概念术语表中"相关概念"列包含file:///链接
- **When**: 脚本解析"相关概念"列
- **Then**: 概念间生成related_to类型边，未匹配的链接输出警告但不中断
- **Verification**: `programmatic`
- **Notes**: 如"第一性原理"关联"本原"、"公理"等，边的数量≥30条

### AC-3: 时间线节点与人物提取
- **Given**: 07-timeline.md包含19个节点和10位人物
- **When**: 脚本解析时间线
- **Then**: HTML中包含19个Event节点和10个Person节点，归属到4个Period节点
- **Verification**: `programmatic`

### AC-4: HTML文件自包含且可直接打开
- **Given**: 脚本运行成功生成HTML文件
- **When**: 用户双击HTML文件在浏览器中打开
- **Then**: 页面加载后显示力导向知识图谱，无JS报错（CDN加载成功时）
- **Verification**: `human-judgment`

### AC-5: 点击节点显示详情
- **Given**: 知识图谱已加载
- **When**: 点击任意节点
- **Then**: 侧边/弹出面板显示节点详情（定义/摘要、类型、源链接），点击源链接可跳转
- **Verification**: `human-judgment`

### AC-6: 类型筛选功能
- **Given**: 知识图谱已加载
- **When**: 取消勾选"Person"类型复选框
- **Then**: 所有Person类型节点从图中隐藏，其相关边也隐藏；重新勾选则恢复显示
- **Verification**: `human-judgment`

### AC-7: 搜索定位功能
- **Given**: 知识图谱已加载
- **When**: 在搜索框输入"费曼"
- **Then**: "费曼"节点被高亮/居中显示，其他节点淡化
- **Verification**: `human-judgment`

### AC-8: 节点邻居高亮
- **Given**: 知识图谱已加载
- **When**: 点击"第一性原理"概念节点
- **Then**: 与其直接相连的节点（本原、公理、演绎推理、类比推理等）保持高亮，其他节点淡化
- **Verification**: `human-judgment`

### AC-9: 脚本输出信息完整
- **Given**: 脚本正常运行
- **When**: 脚本执行完毕
- **Then**: stdout输出包含节点统计（各类型数量）、边统计、警告/错误数，使用print_pass/print_warn/print_error格式
- **Verification**: `programmatic`

### AC-10: 离线降级提示
- **Given**: 浏览器无法访问CDN（离线环境）
- **When**: 打开HTML文件
- **Then**: 页面显示友好提示"请联网加载可视化库，或查看下方静态关系概览"，并显示一个简化的文本版概念关系列表
- **Verification**: `human-judgment`

### AC-11: README导航更新
- **Given**: HTML文件已生成
- **When**: 检查first-principles/README.md
- **Then**: 文件导航表包含12-knowledge-graph.html条目，快速链接表包含知识图谱入口
- **Verification**: `programmatic`

### AC-12: 领域颜色编码一致性
- **Given**: 知识图谱已加载
- **When**: 观察不同领域的概念节点
- **Then**: 哲学概念为统一色调、物理学概念为统一色调、方法论概念为统一色调、认知科学概念为统一色调，图例说明颜色含义
- **Verification**: `human-judgment`

## Open Questions

- [ ] vis-network.js使用哪个CDN源更可靠？（unpkg vs jsDelivr vs cdnjs，建议jsDelivr多节点镜像）
- [ ] Mermaid流程图中的influenced关系是手工编码在脚本中，还是通过解析Mermaid代码自动提取？（建议MVP阶段手工编码，因为Mermaid解析复杂度高且关系仅约15条）
- [ ] file:///链接在浏览器中的兼容性如何？是否需要改为相对路径链接？
- [ ] 是否需要在图谱中显示可信度评级的视觉区分（如A级节点更大/更亮，B级稍暗）？
