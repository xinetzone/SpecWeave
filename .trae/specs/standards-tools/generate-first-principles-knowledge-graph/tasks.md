# 第一性原理交互式知识图谱 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 知识图谱数据模型与Markdown解析器
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建Python脚本 `.agents/scripts/generate-knowledge-graph.py` 的基础框架
  - 定义数据模型：Node类/字典（id, label, type, domain, definition, source_url, rating）、Edge类/字典（source_id, target_id, relation_type）
  - 定义5种节点类型：Concept（概念）、Person（人物）、Event（事件）、Document（文档）、Period（时期）
  - 定义6种关系类型：related_to（概念相关）、influenced（影响/传承）、preceded（时序先后）、belongs_to（归属）、defined_in（定义于文档）、contributed（人物贡献于概念）
  - 实现06-concepts-glossary.md的概念表解析函数：解析Markdown表格，提取24个概念的名称、英文名、定义（截断为前100字作为摘要）、领域、可信度、相关概念链接
  - 实现07-timeline.md的时间节点表（第9节）解析：提取19个事件的时间、名称、时期、重要程度
  - 实现07-timeline.md的关键人物表（第6节）解析：提取10位人物的姓名、时期、核心贡献
  - 实现README.md的文件导航表解析：提取12个文档的文件名、标题、简介
  - 容错处理：表格格式变化时输出警告而非崩溃
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-1.1: 解析06-concepts-glossary.md返回≥24个Concept节点，每个节点包含label/type/domain字段
  - `programmatic` TR-1.2: 解析07-timeline.md返回≥19个Event节点和≥10个Person节点
  - `programmatic` TR-1.3: 解析README.md返回≥12个Document节点
  - `programmatic` TR-1.4: 相关概念列解析后产生≥30条related_to边
  - `human-judgement` TR-1.5: 解析输出中概念名称与术语表一致（无截断错误、无乱码）
- **Notes**: 概念表中"相关概念"列包含Markdown链接，需要提取链接文本（概念名）；file:///链接用于source_url，链接文本用于匹配目标节点

## [x] Task 2: 补充关系数据与图数据组装
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在脚本中定义4个Period节点（古希腊哲学时期、近代哲学与科学革命、现代科学时期、当代商业与方法论时期）
  - 手工编码Mermaid流程图中的influenced传承关系（约15条，从07-timeline.md第4节跨领域脉络图提取）
  - 手工编码人物→概念的contributed关系（如：亚里士多德→第一性原理、费曼→费曼学习法+草包族科学、马斯克→第一性原理商业应用等）
  - 建立belongs_to关系：Event→Period、Person→Period
  - 建立defined_in关系：Concept→Document（根据概念主要出现在哪个文档中）
  - 建立preceded时序关系：Event之间的前后顺序（从时间线推断）
  - 组装完整的nodes列表和edges列表，去重处理
  - 输出统计信息：各类型节点数、各类型边数、孤立节点警告
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: 总节点数≥65（24概念+10人物+19事件+12文档+4时期≈69）
  - `programmatic` TR-2.2: 总边数≥80（30概念关系+15传承+29归属+12文档归属+8时序≈94）
  - `programmatic` TR-2.3: 无孤立节点（度数为0的节点输出警告）
  - `human-judgement` TR-2.4: 核心传承链正确（亚里士多德→欧几里得→笛卡尔→牛顿→康德→量子力学→费曼→DFT→马斯克）

## [x] Task 3: HTML模板与vis-network可视化渲染
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 设计HTML模板结构：header（标题+图例）、主图区域（vis-network容器）、详情面板、筛选控制面板、搜索栏
  - 引入vis-network via jsDelivr CDN（含integrity hash或降级检测）
  - 定义节点颜色方案：
    - Concept-哲学: #8B4513（棕色）
    - Concept-物理学: #1E88E5（蓝色）
    - Concept-方法论: #43A047（绿色）
    - Concept-认知科学: #FB8C00（橙色）
    - Concept-通用: #757575（灰色）
    - Person: #E53935（红色）
    - Event: #8E24AA（紫色）
    - Document: #00897B（青色）
    - Period: #546E7A（蓝灰色，较大节点）
  - 定义节点大小：Period节点最大（30px），Person/Event中等（20px），Concept/Document标准（16px），A级可信度Concept略大
  - 定义边样式：related_to（实线，灰色）、influenced（箭头，深蓝色，粗）、preceded（箭头，浅灰色，细）、belongs_to（虚线，浅灰）、defined_in（点线，绿色）、contributed（箭头，橙色）
  - 配置vis-network physics：使用forceAtlas2Based solver，合理配置弹簧参数避免过度震荡
  - 配置交互：hover显示tooltip、click选中节点、drag拖拽节点固定、zoom/pan
- **Acceptance Criteria Addressed**: AC-4, AC-12
- **Test Requirements**:
  - `human-judgement` TR-3.1: 浏览器打开HTML后力导向图在5秒内稳定渲染，节点不重叠
  - `human-judgement` TR-3.2: 5种节点类型颜色区分明显，图例说明清楚
  - `human-judgement` TR-3.3: 节点大小有层次区分（Period > Person/Event > Concept）
  - `human-judgement` TR-3.4: 支持拖拽节点、缩放、平移操作
  - `programmatic` TR-3.5: HTML文件大小≤200KB

## [x] Task 4: 交互功能实现（详情面板、筛选、搜索、邻居高亮）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 实现点击节点显示详情面板：
    - Concept节点：名称+英文名+定义摘要+领域标签+可信度标记+"源文档"链接
    - Person节点：姓名+时期+核心贡献+相关概念列表
    - Event节点：时间+名称+时期+重要程度+"详细说明"链接
    - Document节点：标题+简介+难度+文件链接
    - Period节点：时期名称+时间范围+包含节点数
  - 实现筛选复选框：按节点类型（Concept/Person/Event/Document/Period）显示/隐藏
  - 实现领域筛选复选框：按概念领域（哲学/物理/方法论/认知科学/通用）筛选
  - 实现搜索框：输入关键词模糊匹配节点label，匹配节点高亮居中，不匹配节点淡化
  - 实现邻居高亮：点击节点后，一跳邻居保持高亮（opacity=1.0），其他节点淡化（opacity=0.2），边同样处理；点击空白处恢复
  - 实现离线降级：CDN加载失败时检测并显示提示信息+简化的文本概念关系列表
  - 实现图例面板：展示所有节点类型颜色和边类型样式说明
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-8, AC-10, AC-12
- **Test Requirements**:
  - `human-judgement` TR-4.1: 点击"第一性原理"节点，详情面板显示其定义、领域、源链接
  - `human-judgement` TR-4.2: 取消Person复选框后所有人物节点隐藏，勾选后恢复
  - `human-judgement` TR-4.3: 搜索"费曼"能定位到费曼节点并高亮
  - `human-judgement` TR-4.4: 点击节点后邻居高亮，非邻居淡化
  - `human-judgement` TR-4.5: 断网环境下打开HTML显示降级提示而非白屏

## [x] Task 5: 脚本集成与CLI入口
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 实现CLI参数：`--input-dir`（知识档案目录，默认docs/knowledge/learning/first-principles/）、`--output`（输出HTML路径）、`--json`（输出JSON数据供调试）
  - 使用lib.cli.add_common_args、print_pass/print_warn/print_error/print_summary
  - 使用lib.project.resolve_project_root解析项目根路径
  - 脚本头部添加标准docstring、sys.path设置、shebang
  - 脚本主函数串联：解析所有Markdown→组装图数据→生成HTML→输出统计
  - 脚本完成后运行check-duplication.py确认无重复代码
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-5.1: 脚本从项目根目录运行 `python .agents/scripts/generate-knowledge-graph.py` 成功生成HTML文件
  - `programmatic` TR-5.2: 脚本使用lib.cli输出格式，末尾有pass/warn/error统计
  - `programmatic` TR-5.3: check-duplication.py无新增重复代码警告
  - `human-judgement` TR-5.4: --help参数显示清晰的使用说明

## [x] Task 6: 单元测试
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 创建测试文件 `.agents/scripts/tests/test_generate_knowledge_graph.py`
  - 测试Markdown表格解析函数（使用小型测试Markdown片段）
  - 测试概念名称提取和相关概念链接解析
  - 测试节点去重逻辑
  - 测试HTML生成输出（验证包含vis-network CDN引用、包含节点数据JSON）
  - 测试CLI参数解析
  - 不测试浏览器渲染（属于人工验证范畴）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 所有单元测试通过
  - `programmatic` TR-6.2: 解析函数对格式异常的Markdown表格优雅降级（返回空+警告）

## [x] Task 7: 知识档案集成与README更新
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 运行脚本生成12-knowledge-graph.html到first-principles目录
  - 在README.md文件导航表中添加第12号条目（序号调整：原11→12，新增知识图谱为12或按顺序编号）
  - 在README.md快速链接表中添加"🕸️ 知识图谱"链接
  - 在README.md资料概览部分更新文件总数（12→13）
  - 验证HTML文件在浏览器中可正常打开和交互
  - 验证file:///链接在浏览器中可跳转到对应Markdown文件
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `programmatic` TR-7.1: README.md文件导航表包含12-knowledge-graph.html条目
  - `programmatic` TR-7.2: README.md快速链接表包含知识图谱入口
  - `human-judgement` TR-7.3: 浏览器打开生成的HTML，核心交互（点击/筛选/搜索）正常工作
  - `human-judgement` TR-7.4: 视觉效果：布局清晰、颜色协调、文字可读、无明显遮挡

## [x] Task 8: 收尾与原子提交
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**:
  - 运行ci-check相关检查（链接检查不涉及HTML中的CDN链接）
  - 确认脚本可重复运行（幂等性验证：运行两次输出一致）
  - 使用git-commit技能或原子提交流程提交所有变更
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: 连续运行两次脚本，生成的HTML文件diff无随机差异
  - `human-judgement` TR-8.2: 代码审查通过，脚本逻辑清晰，无过度复杂的正则
