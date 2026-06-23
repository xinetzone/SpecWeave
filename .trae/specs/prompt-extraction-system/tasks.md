# Tasks

- [ ] Task 0: 项目骨架搭建与依赖配置
  - [ ] 创建 `prompt_extraction/` 目录结构及所有模块的 `__init__.py`
  - [ ] 创建 `requirements.txt`（依赖：streamlit, pandas, pytest, plotly 等）
  - [ ] 创建 `prompt_extraction/config.py` 配置文件（评分阈值、权重、输出目录等）
  - [ ] 创建 `prompt_extraction/models.py` 数据模型（PromptRecord, FeatureSet, QualityScore, OptimizationResult）

- [ ] Task 1: 提示词输入模块
  - [ ] 实现 `prompt_extraction/input/parser.py`：CSV/JSON/TXT/Markdown 文件解析器，支持自动检测字段映射；Markdown 按标题层级拆分区块
  - [ ] 实现 `prompt_extraction/input/input_handler.py`：统一输入处理入口，封装单条输入和批量导入逻辑
  - [ ] 编写 `prompt_extraction/tests/test_input.py`：覆盖正常文件解析、空文件、格式错误、编码异常等场景

- [ ] Task 2: 文本预处理模块
  - [ ] 实现 `prompt_extraction/preprocessing/cleaner.py`：空白规范化、格式标记去除、Markdown 结构保留、URL/email 识别与标记
  - [ ] 实现 `prompt_extraction/preprocessing/normalizer.py`：全角半角转换、标点规范化、字符集统一
  - [ ] 编写 `prompt_extraction/tests/test_preprocessing.py`：覆盖各类文本清洗和标准化场景

- [ ] Task 3: 特征提取模块
  - [ ] 实现 `prompt_extraction/extraction/extractor.py`：基于规则+关键词识别指令、约束条件、预期输出格式；利用 Markdown 结构（标题→分区、列表→约束/步骤、代码块→输出示例）辅助特征提取
  - [ ] 编写 `prompt_extraction/tests/test_extraction.py`：覆盖有特征、无特征、混合特征场景

- [ ] Task 4: 质量评估模块
  - [ ] 实现 `prompt_extraction/assessment/evaluator.py`：清晰度、完整性、可执行性三维度评分算法，综合评分与等级判定
  - [ ] 编写 `prompt_extraction/tests/test_assessment.py`：覆盖高分、低分、边界值、极端输入场景

- [ ] Task 5: 优化生成模块
  - [ ] 实现 `prompt_extraction/optimization/optimizer.py`：基于评估结果触发的模板化优化算法（补充要素、消歧、结构调整、对比生成）
  - [ ] 编写 `prompt_extraction/tests/test_optimization.py`：覆盖触发优化、不触发、优化结果对比场景

- [ ] Task 6: 流水线编排器
  - [ ] 实现 `prompt_extraction/pipeline.py`：Pipeline 类，串联 Input → Preprocessing → Extraction → Assessment → Optimization，实现 PromptRecord 在各模块间传递，含错误处理与日志
  - [ ] 编写 `prompt_extraction/tests/test_pipeline.py`：覆盖单条处理、批量处理、部分失败继续执行、全流程数据一致性

- [ ] Task 7: 可视化界面
  - [ ] 实现 `prompt_extraction/ui/app.py`：Streamlit 主应用，包含输入页（文件上传/文本输入）、结果列表页、详情页
  - [ ] 实现 `prompt_extraction/ui/components/`：雷达图组件、评分卡片组件、优化对比 diff 组件、导出按钮组件
  - [ ] 实现导出功能：CSV 导出（含原始、优化后、评分、特征）和纯优化提示词导出

- [ ] Task 8: 集成测试与验证
  - [ ] 编写 `prompt_extraction/tests/test_integration.py`：端到端流水线测试，使用多种类型提示词验证全流程
  - [ ] 运行全部测试，确认通过率 100%，验证系统稳定性

# Task Dependencies
- Task 1-5 依赖 Task 0（项目骨架）
- Task 4 依赖 Task 3（质量评估使用特征提取结果）
- Task 5 依赖 Task 4（优化触发依赖评估结果）
- Task 6 依赖 Task 1-5（流水线串联所有模块）
- Task 7 依赖 Task 6（UI 调用流水线）
- Task 8 依赖 Task 1-7（集成测试验证全系统）
- Task 1, 2, 3 可并行执行