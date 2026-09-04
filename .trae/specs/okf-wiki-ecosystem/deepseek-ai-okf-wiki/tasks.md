# DeepSeek-AI 开源项目 OKF Wiki 教程生成 - Implementation Plan

## Task 1: 创建 deepseek 分组目录结构和分组索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `bundles/deepseek/` 目录
  - 创建 `bundles/deepseek/index.md`（含 okf_version frontmatter、分组描述、生态关系概览、知识束列表导航占位符）
  - 为 12 个子项目创建 bundle 目录骨架（index.md 占位 + concepts/ examples/ references/ spec/ 子目录）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: `bundles/deepseek/index.md` 存在且包含 `okf_version: "0.2"` frontmatter；evidence: 文件读取验证
  - `rule` TR-1.2: 12 个子项目 bundle 目录骨架完整（各含 concepts/ examples/ references/ spec/ 目录）；evidence: 目录列表验证

## Task 2: DeepEP - R阶段（事实采集）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 深入阅读 DeepEP 源码（`deep_ep/` Python包 + `csrc/` CUDA/C++代码）
  - 提取编号事实清单 F-001~F-xxx，写入 `bundles/deepseek/deep-ep/spec/facts.md`
  - 覆盖模块：Python API（__init__.py、buffers/、utils/）、CUDA kernels（elastic/、legacy/、backend/）、JIT 编译系统
  - 事实零推测，每条指向具体文件路径和行号
- **Acceptance Criteria Addressed**: AC-2, AC-4, NFR-1, NFR-5
- **Test Requirements**:
  - `rule` TR-2.1: facts.md 中无"用于"/"目的是"/"设计为"等推断词；evidence: 关键词搜索检查
  - `rule` TR-2.2: 每条事实包含源码文件路径；evidence: 抽样验证路径存在性
  - `rubric` TR-2.3: 事实覆盖完整性；scale 1-5；anchors 1=仅覆盖入口/5=覆盖所有主要模块和公开API；threshold >= 4；evidence: 模块清单对照检查

## Task 3: DeepEP - I阶段（架构洞察与知识地图）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 facts.md 提炼 3-5 个核心架构洞察（陈述+证据+反常识+行动四元组）
  - 设计知识地图：概念文档分组、文档依赖关系、学习路径
  - 确定文档清单：concepts/ 需要哪些文件、每个覆盖哪些 F-xxx 事实、examples/ 和 references/ 的内容
  - 写入 `bundles/deepseek/deep-ep/spec/insights.md`
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 每个洞察包含四元组（陈述/证据/反常识/行动）；evidence: 结构化检查
  - `rubric` TR-3.2: 知识地图合理性；scale 1-5；anchors 1=文档清单混乱/5=学习路径清晰、依赖关系合理、覆盖完整；threshold >= 4；evidence: 文档清单审查

## Task 4: DeepEP - E阶段（文档生成）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 4a. 生成 references/ 信源文件（信源先行）
  - 4b. 分批生成 concepts/ 概念文档（每批≤7），按学习路径编号
  - 4c. 生成 examples/ 示例文档（基于 tests/ 和实际 API 用法）
  - 4d. 生成各级 index.md（根index、concepts/index、examples/index、references/index）——最后生成
  - 所有文档遵循 OKF frontmatter 规范
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, NFR-2, NFR-3, NFR-4
- **Test Requirements**:
  - `rule` TR-4.1: references/ 文件先于 concepts/ 生成；evidence: 生成顺序记录
  - `rule` TR-4.2: 所有 .md 文件（非index）含完整 frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）；evidence: frontmatter 解析验证
  - `rule` TR-4.3: concepts/ 下文档数 ≥ 3；evidence: 文件计数
  - `rule` TR-4.4: 子目录 index.md 无 frontmatter；evidence: 文件首行检查

## Task 5: DeepEP - V阶段（独立验证）
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 结构检查 + Frontmatter检查
  - Grep 验证：文档中引用的每个类名/方法名在源码中存在
  - 链接检查：所有交叉链接目标文件存在
  - 代码示例检查：API调用签名与源码一致
  - Index 完整性检查
  - 输出检查报告，逐一修复问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: Grep 验证未发现虚构 API（发现后100%修复）；evidence: Grep验证输出+修复记录
  - `rule` TR-5.2: 断链数为0；evidence: 链接检查输出
  - `rule` TR-5.3: 检查报告所有问题已修复；evidence: 修复后复查记录

## Task 6: DeepGEMM - R→I→E→V 全流程
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 DeepGEMM 项目执行完整的 R→I→E→V 五阶段（同 Task 2-5 的流程）。DeepGEMM 是统一高性能 tensor core kernel 库，覆盖 csrc/apis/（gemm/attention/einsum/mega/hyperconnection/layout/runtime）、deep_gemm/ Python包（legacy/mega/testing/utils）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-6.1: 同 TR-2.1/2.2/4.1-4.4/5.1-5.3 检查项
  - `rubric` TR-6.2: 文档质量评分 >= 4；evidence: 独立审查评估

## Task 7: FlashMLA - R→I→E→V 全流程
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 FlashMLA 项目执行完整的 R→I→E→V 五阶段。FlashMLA 是 MLA 注意力解码 kernel 库，覆盖 csrc/api/（dense/sparse decode/fwd）、csrc/sm90/、csrc/sm100/、csrc/smxx/、flash_mla Python包、benchmark。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-7.1: 同 TR-2.1/2.2/4.1-4.4/5.1-5.3 检查项
  - `rubric` TR-7.2: 文档质量评分 >= 4；evidence: 独立审查评估

## Task 8: TileKernels - R→I→E→V 全流程
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 TileKernels 项目执行完整的 R→I→E→V 五阶段。TileKernels 是基于 TileLang DSL 的 kernel 集合，覆盖 tile_kernels/ 下 moe/（12个kernel）、quant/（14个kernel）、mhc/（8个kernel）、engram/、transpose/、modeling/ 高层封装、torch/ 参考实现。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-8.1: 同 TR-2.1/2.2/4.1-4.4/5.1-5.3 检查项
  - `rubric` TR-8.2: 文档质量评分 >= 4；evidence: 独立审查评估

## Task 9: LPLB - R→I→E→V 全流程
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 LPLB 项目执行完整的 R→I→E→V 五阶段。LPLB 是基于线性规划的 MoE 负载均衡器，覆盖 lplb/ Python包（planner.py、eplb.py）、csrc/ CUDA plugin、resources/csrc-tmpl/ LP求解器模板。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-9.1: 同 TR-2.1/2.2/4.1-4.4/5.1-5.3 检查项
  - `rubric` TR-9.2: 文档质量评分 >= 4；evidence: 独立审查评估

## Task 10: DeepSpec - R→I→E→V 全流程
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 对 DeepSpec 项目执行完整的 R→I→E→V 五阶段。DeepSpec 是投机解码训练评估全栈，覆盖 deepspec/ 下 data/、eval/（dspark/eagle3）、modeling/（dspark/eagle3）、trainer/、utils/ 模块。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-10.1: 同 TR-2.1/2.2/4.1-4.4/5.1-5.3 检查项
  - `rubric` TR-10.2: 文档质量评分 >= 4；evidence: 独立审查评估

## Task 11: DualPipe - R→I→E→V 全流程
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 对 DualPipe 项目执行完整的 R→I→E→V 五阶段。DualPipe 是双向流水线并行调度算法参考实现，代码量轻量，覆盖 dualpipe/（dualpipe.py、dualpipev.py、comm.py、utils.py）和 examples/。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-11.1: 同 TR-2.1/2.2/4.1-4.4/5.1-5.3 检查项
  - `rubric` TR-11.2: 文档质量评分 >= 4；evidence: 独立审查评估

## Task 12: DeepSeek-OCR - 轻量 bundle 生成
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 为 DeepSeek-OCR 生成适当深度的 OKF bundle：项目概述、模型架构概念文档（视觉编码器"上下文光学压缩"设计）、vLLM/HF 推理使用示例、信源参考。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-12.1: bundle 包含 index.md、至少 1 篇概念文档覆盖模型架构、references/ 信源文件；evidence: 文件检查
  - `rule` TR-12.2: frontmatter 规范合规、链接无断裂；evidence: 格式和链接检查

## Task 13: DeepSeek-OCR-2 - 轻量 bundle 生成
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 为 DeepSeek-OCR-2（视觉因果流）生成 OKF bundle：项目概述、与 V1 的架构差异（动态分辨率、因果流设计）、推理示例、信源参考。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-13.1: bundle 包含 index.md、至少 1 篇概念文档覆盖 V2 架构演进、references/ 信源文件；evidence: 文件检查
  - `rule` TR-13.2: frontmatter 规范合规、链接无断裂；evidence: 格式和链接检查

## Task 14: awesome-deepseek-agent - 资源列表 bundle 生成
- **Status**: `pending`
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 为 awesome-deepseek-agent 生成轻量 reference bundle：项目概述、工具分类索引（编码助手/Chat客户端/CLI工具/移动应用）、各工具配置参考信源。无概念文档（纯资源列表性质）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-14.1: bundle 包含 index.md 和 references/ 信源索引；evidence: 文件检查

## Task 15: DeepSeek-Math-V2 和 Engram - 论文 bundle 生成
- **Status**: `pending`
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 为 DeepSeek-Math-V2 和 Engram 生成轻量 reference bundle：每个项目一个 bundle，包含论文概述、核心思想、推理/demo代码说明、信源参考。无深度概念文档（paper-only 项目）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-15.1: 两个 bundle 各包含 index.md 和 references/ 信源文件；evidence: 文件检查

## Task 16: 更新 bundles/index.md 总索引
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
- **Description**:
  - 更新 bundles/index.md：将 groups 从 10 改为 11，total_bundles 从 36 改为 48
  - 在分组导航表中添加 deepseek 行
  - 在生态关系概览图中添加 deepseek 分组
  - 在推荐入门路径中适当位置添加 deepseek 相关路径
  - 添加"🧠 DeepSeek-AI 基础设施"分组详情节
  - 更新 deepseek/index.md 的知识束列表（替换占位符为实际链接）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-16.1: bundles/index.md 中 groups: 11、total_bundles: 48；evidence: frontmatter 字段验证
  - `rule` TR-16.2: 分组导航表包含 deepseek 链接；evidence: 内容检查
  - `rule` TR-16.3: deepseek/index.md 中的所有知识束链接指向存在的文件；evidence: 链接检查

## Task 17: 全局最终验证
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 16
- **Description**:
  - 对所有 12 个 bundle 执行最终全局检查：frontmatter、链接、API 真实性、index 完整性
  - 确认 bundles/index.md 和 deepseek/index.md 的所有链接有效
  - 确认文件名风格一致（kebab-case）
  - 确认所有文档语言为中文，交叉链接使用 / 开头路径
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-17.1: 全局零断链、零虚构API、frontmatter全部合规；evidence: 全局检查脚本输出
  - `rubric` TR-17.2: 整体文档质量一致性；scale 1-5；anchors 1=风格混乱/5=风格统一、质量一致；threshold >= 4；evidence: 全局审查
