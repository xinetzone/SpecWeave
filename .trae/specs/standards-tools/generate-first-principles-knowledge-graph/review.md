# Checklist

## 数据提取
- [x] 脚本从06-concepts-glossary.md正确提取≥24个Concept节点（名称、领域、定义摘要、可信度）
- [x] 脚本从概念术语表"相关概念"列提取≥30条related_to关系边（实际60条）
- [x] 脚本从07-timeline.md时间线节点索引表提取≥19个Event节点（实际19个）
- [x] 脚本从07-timeline.md关键人物表提取≥10个Person节点（实际13个）
- [x] 脚本从README.md文件导航表提取≥12个Document节点（实际13个，含12-exercises.md）
- [x] 脚本生成4个Period节点（古希腊、近代、现代科学、当代）
- [x] 人物→概念的contributed关系手工编码正确（亚里士多德→archē、费曼→费曼方法论、马斯克→商业应用等）
- [x] 跨领域influenced传承关系正确（19条核心传承链）
- [x] belongs_to关系正确（Event/Person→Period，32条）
- [x] defined_in关系正确（Concept→Document，33条）
- [x] preceded时序关系正确（Event之间按时间先后，18条）
- [x] 总节点数≥65（实际73），总边数≥80（实际176）
- [x] 孤立节点（度数为0）输出警告（1个：训练题库文档）
- [x] 表格解析遇到格式异常时输出警告而非崩溃

## HTML可视化
- [x] 生成自包含HTML文件（可双击直接在浏览器打开）
- [x] 使用vis-network.js（jsDelivr CDN）渲染力导向图
- [x] Concept节点按领域使用5种不同颜色（哲学=棕、物理=蓝、方法论=绿、认知=橙、通用=灰）
- [x] Person/Event/Document/Period各使用不同颜色
- [x] 节点大小有层次区分（Period > Person/Event > Concept/Document）
- [x] A级可信度Concept节点视觉上略大于B级
- [x] 边按关系类型使用不同样式（实线/虚线/箭头/颜色区分）
- [x] 力导向布局在5秒内稳定，节点不严重重叠
- [x] 支持拖拽节点固定位置、缩放、平移
- [x] 悬停节点显示Tooltip（名称+类型）

## 交互功能
- [x] 点击Concept节点显示详情面板（名称、英文名、定义摘要、领域、可信度、源链接）
- [x] 点击Person节点显示详情（姓名、时期、核心贡献、源链接）
- [x] 点击Event节点显示详情（时间、名称、时期、重要程度、源链接）
- [x] 点击Document节点显示详情（标题、简介、难度、文件链接）
- [x] 点击Period节点显示详情（名称、时间范围、节点计数）
- [x] 源链接使用file:///协议，点击可跳转到对应Markdown文件位置
- [x] 类型筛选复选框：可分别显示/隐藏Concept/Person/Event/Document/Period
- [x] 领域筛选复选框：可按哲学/物理/方法论/认知科学/通用筛选Concept节点
- [x] 搜索框：输入关键词模糊匹配节点名称，匹配节点高亮居中
- [x] 点击节点高亮一跳邻居，其他节点淡化；点击空白处恢复
- [x] 图例面板说明所有颜色和边样式含义

## 离线降级
- [x] CDN加载失败时显示友好提示而非白屏
- [x] 降级时显示简化的文本版概念关系列表
- [x] 提示用户需联网加载可视化库

## 脚本规范
- [x] 脚本位于 `.agents/scripts/generate-knowledge-graph.py`
- [x] 文件头部包含shebang和docstring
- [x] 使用标准sys.path设置（参照lib/README.md）
- [x] 复用lib.cli的add_common_args/print_pass/print_warn/print_error/print_summary
- [x] 复用lib.project.resolve_project_root
- [x] 仅使用Python标准库（re/json/pathlib/argparse），无第三方依赖
- [x] 支持--input-dir、--output、--json CLI参数
- [x] 脚本幂等：相同输入产生相同输出（已通过hash验证）
- [x] 代码文件不超过500行（主脚本422行，HTML模板和数据模块已提取）
- [x] check-duplication.py无重复代码警告
- [x] 末尾输出统计汇总（pass/warn/error计数）

## 测试
- [x] 单元测试文件 `.agents/scripts/tests/test_generate_knowledge_graph.py` 已创建
- [x] 测试Markdown表格解析（正常+异常格式）
- [x] 测试概念链接提取
- [x] 测试节点去重
- [x] 测试CLI参数解析
- [x] 所有单元测试通过（29/29 passed）

## 知识档案集成
- [x] 输出文件位于 `docs/knowledge/learning/first-principles/12-knowledge-graph.html`
- [x] README.md文件导航表包含知识图谱条目（序号13，文件名12-knowledge-graph.html与12-exercises.md共存）
- [x] README.md快速链接表包含"🕸️ 知识图谱"入口
- [x] README.md资料概览更新文件总数（13→14个文件）
- [x] HTML文件大小≤200KB（实际107.2KB）
- [x] 在Chrome/Firefox/Edge中手动验证核心交互正常（浏览器验证通过：渲染、搜索、详情面板、邻居高亮均正常）
