# 模块职责

## 顶层模块职责矩阵

| 模块 | 路径 | 职责 | 关键文件 |
|---|---|---|---|
| 全局契约 | `AGENTS.md` | 智能体入口、全局规则、上下文路由 | `AGENTS.md` |
| 规范容器 | `.agents/` | 角色、提示词、协议、工作流、规则、脚本等机器可读规范 | `.agents/README.md` |
| 规格文档 | `.trae/specs/` | Spec-driven 开发过程资产 | `spec.md`、`tasks.md`、`checklist.md` |
| 应用工作区 | `apps/` | 稳定应用与共享模块承载区 | `apps/README.md` |
| 项目文档 | `docs/` | 面向人类读者的文档、知识库、复盘、模板、Code Wiki | `docs/README.md` |
| 提示词萃取系统 | `prompt_extraction/` | 可执行 Python 子项目，完成提示词处理与优化 | `pipeline.py`、`models.py` |

## `.agents/` 子模块职责

| 子目录 | 职责 | 说明 |
|---|---|---|
| `roles/` | 智能体角色定义 | 定义 orchestrator、architect、developer、reviewer、tester、co-founder 等角色职责与边界 |
| `modules/` | 自我演进模块 | 定义自我洞察、自我复盘、自我萃取、自我进化、自我迭代、自我验证、自我管理、自我发展 |
| `prompts/` | 系统提示词 | 按角色保存 `system-prompt.md` 和 `few-shot.md` |
| `tools/` | 工具调用规范 | 定义文件操作、代码执行、搜索、通信等工具使用规则 |
| `protocols/` | 协作协议 | 定义任务交接、消息传递、冲突解决、依赖管理、应用开发生命周期 |
| `workflows/` | 标准工作流 | 定义功能开发、代码审查、测试流程 |
| `templates/` | 模板资产 | 保存任务模板、交接模板 |
| `scripts/` | 验证与自动化脚本 | 提供 Git 忽略、链接、规格一致性、导航、溯源、权限等检查 |
| `teams/` | 团队管理 | 管理团队生命周期、权限系统、角色自动创建等 |
| `worlds/` | 协作执行与环境管理 | 管理多用户权限、协作编辑、环境变量、资源隔离、状态监控等 |
| `rules/` | 治理规则 | 保存硬编码识别、允许场景、替代方案、检测与执行规则 |

## `docs/` 子模块职责

| 子目录或文件 | 职责 |
|---|---|
| `docs/knowledge/` | 技术知识库，保存架构决策、运维经验、故障排查记录 |
| `docs/retrospective/` | 复盘文档体系，保存复盘报告、模式库、决策框架、概念与模板 |
| `docs/templates/` | 文档模板，如应用 README、库 README、Spec README 模板 |
| `docs/task-summaries/` | 任务执行总结 |
| `docs/code-wiki/` | 本 Code Wiki 文档集 |
| `docs/project-overview.md` | 项目定位与设计理念 |
| `docs/project-structure.md` | 项目目录结构说明 |
| `docs/tech-stack.md` | 技术栈与环境要求 |
| `docs/verification-automation.md` | 验证与自动化说明 |

## `prompt_extraction/` 子模块职责

### 模块总览

| 子模块 | 职责 | 典型输入 | 典型输出 |
|---|---|---|---|
| `input/` | 处理单条文本和批量文件输入 | 文本、CSV、JSON、TXT、Markdown | `PromptRecord` 列表 |
| `preprocessing/` | 清洗文本、提取 Markdown 结构、识别元数据、标准化文本 | 原始提示词文本 | 清洗文本、结构信息、元数据 |
| `extraction/` | 提取指令、约束、预期输出格式 | 清洗后文本、Markdown 结构 | `FeatureSet` |
| `assessment/` | 计算提示词质量评分 | 文本、`FeatureSet` | `QualityScore` |
| `optimization/` | 对低质量提示词生成优化版本 | `PromptRecord` | `OptimizationResult` |
| `constants/` | 统一保存阈值、关键词、正则、路径、样式常量 | 无业务输入 | 常量导出 |
| `messages/` | 统一保存错误文案、建议文案、UI 文案 | 无业务输入 | 文案常量 |
| `ui/` | Streamlit 可视化应用与组件 | 用户上传或输入 | 页面展示、导出按钮 |
| `tests/` | 单元测试与集成测试 | 测试样例 | 测试结果 |

### 输入模块

`input/` 由 `parser.py` 和 `input_handler.py` 组成。

| 文件 | 职责 |
|---|---|
| `parser.py` | 根据文件扩展名识别格式，解析 CSV、JSON、TXT、Markdown 文件 |
| `input_handler.py` | 将单条文本或批量文件统一转换为 `PromptRecord` |

支持格式：

- CSV：自动识别提示词列，优先匹配 `prompt`、`text` 等关键词。
- JSON：要求顶层为对象数组，自动识别提示词字段。
- TXT：每个非空行视为一条提示词。
- Markdown：按一级或二级标题拆分区块；无标题时整体作为一条记录。

### 预处理模块

`preprocessing/` 包含两个文件：

| 文件 | 职责 |
|---|---|
| `cleaner.py` | 空白规范化、Markdown/HTML 标记去除、Markdown 结构提取、URL/email/代码块识别 |
| `normalizer.py` | 全角字符转半角、中文标点标准化 |

重要设计点：Markdown 结构和元数据会在去除格式标记前提取，以避免结构信息在清洗过程中丢失。

### 特征提取模块

`extraction/extractor.py` 提取三类核心特征：

| 特征 | 来源 | 说明 |
|---|---|---|
| 指令 | 指令关键词、祈使句、Markdown 标题 | 表示用户希望完成的核心动作 |
| 约束 | 约束关键词、Markdown 列表项 | 表示格式、内容、风格等限制条件 |
| 预期输出 | 输出关键词、代码块、格式关键词 | 表示希望返回的结构或类型 |

### 质量评估模块

`assessment/evaluator.py` 从三个维度评分：

| 维度 | 评分逻辑 |
|---|---|
| 清晰度 | 从 100 分起扣，考虑文本长度、结构层次、歧义词 |
| 完整性 | 从 0 分起加，考虑指令、约束、上下文、示例、输出格式五要素 |
| 可执行性 | 从 0 分起加，考虑动作动词、约束可验证性、输出可判定性 |

综合评分按照权重计算，并基于等级阈值判定“优、良、中、差”。

### 优化模块

`optimization/optimizer.py` 在综合评分低于质量阈值时触发优化，依次执行：

1. 补充缺失要素。
2. 消除歧义表达。
3. 重组为标准 Markdown 结构。
4. 生成优化前后 diff。

### UI 模块

`ui/app.py` 是 Streamlit 应用入口，提供：

- 输入方式选择。
- 文件上传。
- 手动输入。
- 处理结果表格。
- 评分卡。
- 雷达图。
- 优化差异展示。
- 导出按钮。

`ui/components/` 保存可复用 UI 组件：

| 组件 | 职责 |
|---|---|
| `score_card.py` | 展示质量评分卡 |
| `radar_chart.py` | 使用 Plotly 绘制评分雷达图 |
| `diff_viewer.py` | 展示优化前后差异 |
| `export_button.py` | 提供结果导出按钮 |

## 自动化脚本模块职责

| 脚本 | 职责 |
|---|---|
| `check-gitignore.py` | 验证临时依赖路径是否被 `.gitignore` 覆盖 |
| `check-links.py` | 扫描 Markdown 链接，校验本地文件引用和可选外部 URL |
| `check-spec-consistency.py` | 检查 `spec.md`、`tasks.md`、`checklist.md` 一致性 |
| `generate-nav.py` | 生成并更新 README 和 docs README 的导航表 |
| `check-move.py` | 移动 Markdown 文件时调整相对链接并可更新引用 |
| `check-source-traceability.py` | 扫描 `source` 溯源字段，建立源文件到派生产物索引 |
| `check-role-permissions.py` | 校验角色 frontmatter 中权限字段完整性 |
| `ci-check.ps1` / `ci-check.sh` | 组合运行主要验证任务 |
