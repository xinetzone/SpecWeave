---
status: "draft"
id: onnx-ecosystem-okf-wiki-spec
title: ONNX 生态系统 OKF Wiki 教程生成 - PRD
date: 2026-08-22
category: spec
maturity: L0-draft
---

# ONNX 生态系统 OKF Wiki 教程 - Product Requirement Document

## Problem Statement

ONNX（Open Neural Network Exchange）生态包含多个子项目（核心标准、IR、优化器、编译器、转换器、后端等），代码分散在 13 个子目录中，缺乏系统化的中文源码级教程。现有官方文档以 API 参考和英文用户指南为主，缺少从源码架构角度的深度解析，导致开发者理解 ONNX 内部机制、扩展算子、调试模型转换问题时学习成本高。

## Users

- **深度学习推理工程师**：需要理解 ONNX 计算图内部结构以进行模型优化和调试
- **框架转换器开发者**：需要理解 ONNX IR、算子定义、类型系统以开发模型转换器
- **编译器/后端开发者**：需要理解 ONNX-MLIR、ONNX-TensorRT 等编译后端的实现原理
- **AI 基础设施工程师**：需要理解 ONNX 模型检查、序列化、优化 passes 的实现机制

## Goals

- 使用 `source-code-to-okf-wiki` 技能（R→I→E→V→C 五阶段链路）系统化学习 `external/libs/models/onnx/` 下所有有实质代码的子项目源码
- 在 `projects/awesome-okf-xs/bundles/onnx/` 下创建 OKF v0.2 规范的知识束（Bundle），产出结构化中文源码教程
- 通过 `seven-concepts-cmd` 方法论编排知识沉淀链路，确保质量门 G1-G4 全部通过
- 每个知识束遵循 concepts/examples/references 三层结构，frontmatter 完整，交叉引用正确
- 所有文档中的 API/类名/方法名经过 Grep 级源码验证，杜绝虚构内容

## Non-Goals (Out of Scope)

- 不做官方文档的完整翻译或复述
- 不覆盖每个 ONNX 算子的逐一定义（算子数量 200+，聚焦算子注册机制和类型系统）
- 不深入 ONNX Runtime（ORT）推理引擎（独立项目，不在当前源码目录内）
- 不覆盖 backend-scoreboard（网站应用，非核心库）、digestai（PyQt GUI 应用）、models（模型仓库）、tutorials（示例集）、sigs（会议文档）等无实质库代码的子项目
- 不修改 awesome-okf-xs 子项目的 `.agents/` 规范文件（走子项目流程）
- 不生成 git 提交（用户未要求）

## Source Code Inventory

源码根目录：`d:\spaces\SpecWeave\external\libs\models\onnx\`

| 子项目 | 语言 | 代码规模 | 包含级别 | 说明 |
|--------|------|---------|---------|------|
| onnx/ | Python + C++ | 大（核心项目） | Tier 1 | ONNX 标准本体：protobuf 定义、C++ IR、算子定义（defs/）、检查器、Python API（helper/checker/compose/parser/printer/serialization）、参考后端 |
| ir-py/ | Python | 中 | Tier 1 | ONNX 纯 Python IR 实现：_core/_enums/_io/_tape/serde，支持零拷贝张量、图变换、序列化 |
| optimizer/ | C++ + Python | 中 | Tier 2 | ONNX 模型优化器：预打包优化 passes、C++ 优化库 |
| onnxmltools/ | Python | 中 | Tier 2 | 多工具包转换器：CoreML/LightGBM/XGBoost/CatBoost/H2O 等转 ONNX |
| sklearn-onnx/ | Python | 中 | Tier 2 | scikit-learn 模型/pipeline 转 ONNX 转换器 |
| tensorflow-onnx/ | Python | 中 | Tier 2 | TensorFlow/Keras/tflite 模型转 ONNX 转换器（tf2onnx） |
| onnx-mlir/ | C++ | 大（编译器项目） | Tier 3 | ONNX-MLIR 编译器：基于 LLVM/MLIR 的 ONNX 编译栈，使用分层采样策略 |
| onnx-tensorrt/ | C++ | 中 | Tier 3 | TensorRT 后端 ONNX 解析器 |

**排除子项目**：backend-scoreboard（仅 LICENSE 和网站脚本）、digestai（PyQt GUI 工具）、models（模型 zoo 仓库）、tutorials（示例配置）、sigs（SIG 会议文档）。

## Functional Requirements

### FR-1: 创建 ONNX 生态分类目录
- 在 `bundles/onnx/` 下创建分类索引 `index.md`，列出所有子项目知识束
- 分类索引包含 `okf_version: "0.2"` frontmatter 和生态关系概览图

### FR-2: onnx/ 核心项目知识束（Tier 1，最高深度）
- 创建 `bundles/onnx/onnx/` 目录
- **concepts/**（10-14 篇）：覆盖 ONNX 整体架构、Protobuf IR 与计算图模型、张量类型系统、算子定义与注册机制（OpSchema）、形状推断、模型检查器（Checker）、Helper API、序列化/反序列化、组合（Compose）、解析器（Parser）、打印器（Printer）、参考后端、C++ 核心 IR（ir.h/Graph/Node/Value）、版本转换器
- **examples/**（3-5 篇）：从零构建线性回归模型、模型加载与检查、形状推断实战、图变换/优化 passes 使用、算子扩展示例
- **references/**（5-8 篇）：onnx.proto 信源、helper.py 核心 API、checker.py/cc 源码、defs/schema 算子注册、C++ common/ir.h 核心类

### FR-3: ir-py/ Python IR 知识束（Tier 1）
- 创建 `bundles/onnx/ir-py/` 目录
- **concepts/**（6-8 篇）：IR 整体设计、核心实体（Model/Graph/Node/Value）、类型系统枚举、序列化/反序列化（serde）、Tape 图变换机制、零拷贝张量与 mmap、名称管理（NameAuthority）、链表迭代器
- **examples/**（2-3 篇）：使用 IR 构建计算图、图遍历与变换、序列化到 protobuf
- **references/**（3-4 篇）：_core.py 核心类、_enums.py 类型定义、_tape.py/serde.py 关键模块

### FR-4: optimizer/ 优化器知识束（Tier 2）
- 创建 `bundles/onnx/optimizer/` 目录
- **concepts/**（5-7 篇）：优化器架构、Pass 系统、常用优化 passes（常量折叠/死代码消除/算子融合）、命令行 API、C++ 优化 Pass 基类
- **examples/**（2 篇）：使用预打包优化 passes、自定义优化 Pass
- **references/**（2-3 篇）：优化 Pass 基类、Python API 入口

### FR-5: onnxmltools/ 转换工具知识束（Tier 2）
- 创建 `bundles/onnx/onnxmltools/` 目录
- **concepts/**（5-7 篇）：转换工具架构、CoreML 转换器、LightGBM/XGBoost 转换器、转换器注册机制、Pipeline 转换
- **examples/**（2-3 篇）：XGBoost 模型转 ONNX、Pipeline 转换实战
- **references/**（2-3 篇）：转换器基类、各工具包转换入口

### FR-6: sklearn-onnx/ 转换器知识束（Tier 2）
- 创建 `bundles/onnx/sklearn-onnx/` 目录
- **concepts/**（5-7 篇）：sklearn-onnx 架构、算子映射机制、Pipeline 转换、自定义转换器注册、类型推断
- **examples/**（2-3 篇）：分类器转 ONNX、Pipeline 完整转换、自定义模型转换
- **references/**（2-3 篇）：转换器核心 API、算子映射表

### FR-7: tensorflow-onnx/ (tf2onnx) 知识束（Tier 2）
- 创建 `bundles/onnx/tensorflow-onnx/` 目录
- **concepts/**（5-7 篇）：tf2onnx 架构、TF 算子到 ONNX 映射、图替换机制、命令行转换 API、动态形状处理
- **examples/**（2-3 篇）：Keras 模型转换、SavedModel 转换、自定义算子映射
- **references/**（2-3 篇）：转换器入口、图优化器

### FR-8: onnx-mlir/ 编译器知识束（Tier 3，分层采样）
- 创建 `bundles/onnx/onnx-mlir/` 目录
- **concepts/**（4-6 篇）：ONNX-MLIR 整体架构、ONNX Dialect、编译流程（ONNX→MLIR→LLVM）、运行时接口、编译选项
- **examples/**（1-2 篇）：编译 ONNX 模型为共享库、使用 Python 运行时
- **references/**（2 篇）：驱动入口 onnx-mlir.cpp、编译流程核心模块
- **注意**：使用分层采样策略（架构文档→核心接口→按需深入），不逐文件阅读全部 C++ 源码

### FR-9: onnx-tensorrt/ 后端知识束（Tier 3）
- 创建 `bundles/onnx/onnx-tensorrt/` 目录
- **concepts/**（3-5 篇）：ONNX-TensorRT 解析器架构、算子支持矩阵、解析器 API、插件机制
- **examples/**（1-2 篇）：使用解析器加载 ONNX 模型到 TensorRT
- **references/**（2 篇）：解析器核心类、ShapedWeights/OnnxAttrs 工具类

### FR-10: 每个知识束的 OKF 结构完整性
- 每个 bundle 包含：`index.md`（根索引，含 okf_version）、`log.md`（变更日志）、`concepts/index.md`（概念索引，无 frontmatter）、`examples/index.md`（示例索引）、`references/index.md`（信源索引）
- 每个内容文档包含完整 YAML frontmatter：`type`、`title`、`description`、`tags`、`generated`、`verified`、`status`、`stale_after`、`sources`
- 子目录 `index.md` 不含 frontmatter

### FR-11: 方法论遵循
- 每个知识束严格遵循 source-code-to-okf-wiki 五阶段流程：R（事实采集）→ I（架构洞察）→ E（批量生成）→ V（独立验证）→ C（模式沉淀）
- 通过 seven-concepts-cmd 编排知识沉淀场景链路（R→I→E）
- R 阶段：每个子项目提取编号事实清单（F-xxx），写入各 bundle 的 `spec/facts.md`，零推测
- I 阶段：每个子项目提炼 3-5 个核心洞察（陈述+证据+反常识+行动四元组），写入 `spec/insights.md`
- E 阶段：信源先行（references/ 先生成）、分批生成（每批≤7 文件）、index 最后写
- V 阶段：Grep 级 API 真实性验证、链接检查、frontmatter 检查
- 所有事实和洞察的中间产物存放于 `.trae/specs/okf-wiki-ecosystem/onnx-ecosystem-okf-wiki/` 下对应子项目的 spec 子目录

### FR-12: 更新 bundles 总索引
- 在 `bundles/index.md` 中新增"🧠 ONNX 机器学习生态"分组
- 更新 total_bundles 和 groups 计数

## Non-Functional Requirements

- **NFR-1（语言）**：所有文档正文使用中文，技术术语保留英文并在首次出现时括号注释
- **NFR-2（文件命名）**：文件名使用 kebab-case 纯英文，概念文档按学习路径编号（00-xxx.md, 01-xxx.md, ...）
- **NFR-3（路径引用）**：交叉引用使用 `/` 开头的 bundle-relative 绝对路径
- **NFR-4（溯源）**：每个文档的 `sources` 字段指向对应 references/ 信源文件和事实编号
- **NFR-5（真实性）**：所有引用的类名、方法名、API 签名必须能在源码中通过 Grep 验证存在
- **NFR-6（代码示例）**：代码块标注语言，Python 代码示例基于实际源码 API 编写，不凭记忆编造
- **NFR-7（原子性）**：每个概念文档聚焦单一主题，控制在合理长度（避免单文件过长）
- **NFR-8（stale_after）**：统一设置为 `2027-12-31`（ONNX 核心架构稳定，大版本变更需重新评估）

## Constraints

- **规范约束**：产出物必须符合 OKF v0.2 规范（参考 `bundles/meta/okf-spec/`）和 awesome-okf-xs frontmatter 规范
- **格式参考**：以现有 `bundles/cmake/cmake/` 为格式范本
- **源码路径**：源码位于 `external/libs/models/onnx/`，为第三方代码（禁止修改）
- **目标路径**：产出物位于 `projects/awesome-okf-xs/bundles/onnx/`，该子项目是 git submodule
- **禁止修改范围**：不修改 awesome-okf-xs 子项目的 `.agents/` 目录、AGENTS.md 等规范文件
- **分批约束**：E 阶段每批生成不超过 7 个文件，防止上下文过载
- **验证约束**：V 阶段必须对每个文档中引用的关键类名/方法名执行 Grep 验证

## Dependencies

- `source-code-to-okf-wiki` Skill：提供 R→I→E→V→C 五阶段工作流和质量门
- `seven-concepts-cmd` Skill：提供知识沉淀场景的方法论编排
- 现有 OKF 规范文档：`bundles/meta/okf-spec/` 作为格式标准
- 现有 CMake bundle：`bundles/cmake/cmake/` 作为格式参考范本

## Assumptions

- 源码目录 `external/libs/models/onnx/` 已通过 git submodule 初始化，代码可读取
- ONNX 主项目使用 Apache-2.0 许可证，文档生成属于合理使用
- 用户已有 Python 和机器学习基础，了解基本的神经网络概念
- 不需要安装 ONNX 或运行代码（静态源码分析为主），V 阶段通过 Grep 验证而非运行时测试
- 每个 Tier 1 子项目预计产出 18-27 个内容文档，Tier 2 预计 9-13 个，Tier 3 预计 6-10 个，总计约 80-120 个内容文档

## Acceptance Criteria

### AC-1: ONNX 生态分类目录创建
- **type**: rule
- **Pass condition**: `bundles/onnx/index.md` 存在，包含 `okf_version: "0.2"` frontmatter，列出所有 8 个子项目知识束
- **Evidence source**: 文件系统检查 + 文件内容检查

### AC-2: 8 个子项目知识束结构完整
- **type**: rule
- **Pass condition**: 每个 `bundles/onnx/<project>/` 目录包含 index.md、log.md、concepts/、examples/、references/ 五个必要部分，子目录下均有 index.md
- **Evidence source**: 文件系统检查（8 bundles × 5 结构要素 = 40 项）

### AC-3: 内容文档数量达标
- **type**: rule
- **Pass condition**:
  - onnx/: ≥18 内容文档（≥10 concepts + ≥3 examples + ≥5 references）
  - ir-py/: ≥11 内容文档（≥6 concepts + ≥2 examples + ≥3 references）
  - optimizer/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
  - onnxmltools/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
  - sklearn-onnx/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
  - tensorflow-onnx/: ≥9 内容文档（≥5 concepts + ≥2 examples + ≥2 references）
  - onnx-mlir/: ≥7 内容文档（≥4 concepts + ≥1 examples + ≥2 references）
  - onnx-tensorrt/: ≥6 内容文档（≥3 concepts + ≥1 examples + ≥2 references）
- **Evidence source**: 文件系统统计

### AC-4: Frontmatter 规范合规
- **type**: rule
- **Pass condition**: 每个非 index.md/log.md 的 .md 文件包含可解析的 YAML frontmatter，含 type/title/description/tags/generated/verified/status/stale_after/sources 字段；type 值为 concept/example/reference 之一
- **Evidence source**: 逐文件 frontmatter 检查

### AC-5: 无虚构 API（Grep 验证）
- **type**: rule
- **Pass condition**: 每个知识束随机抽取 ≥10 个引用的类名/方法名/函数名在源码中 Grep 验证，命中率 100%；对于发现虚构的情况必须修正
- **Evidence source**: Grep 命令验证记录

### AC-6: 交叉引用无断链
- **type**: rule
- **Pass condition**: 所有内部交叉引用（/concepts/xxx.md, /examples/xxx.md, /references/xxx.md）目标文件存在
- **Evidence source**: 链接检查

### AC-7: 七概念质量门通过
- **type**: rule
- **Pass condition**:
  - G1（R 阶段）：每个子项目 facts.md 存在，事实编号 F-xxx，无"用于"/"目的是"等推断词
  - G2（I 阶段）：每个子项目 insights.md 存在，洞察包含陈述/证据/反常识/行动四元组
  - G3（E 阶段）：references/ 先于 concepts/ 生成，分批≤7 文件，index 最后写
  - G4（V 阶段）：Grep 验证、链接检查、frontmatter 检查全部通过
- **Evidence source**: 各阶段质量门检查记录

### AC-8: bundles 总索引更新
- **type**: rule
- **Pass condition**: `bundles/index.md` 中新增 ONNX 生态分组，total_bundles 和 groups 计数正确
- **Evidence source**: 文件内容检查

### AC-9: 文档质量（中文表达与结构清晰度）
- **type**: rubric
- **Dimension**: 文档可读性、结构清晰度、知识地图合理性
- **Scale**: 0-2
  - 0: 文档结构混乱、中文表达不通顺、概念排列无逻辑
  - 1: 文档基本可读，概念排列有基本逻辑，但有少量表述不清或跳跃
  - 2: 文档结构清晰、中文表达流畅、概念按学习路径递进、有架构图/表格辅助理解
- **Pass threshold**: ≥1.5（平均每个 bundle 的抽评文档）
- **Evidence source**: 独立审查抽评

## Open Questions

1. onnx-mlir 作为超大 C++ 项目，分层采样的深度是否合适？（当前方案：聚焦架构和编译流程，不深入每个 Dialect Op 的实现细节）
2. 是否需要在 onnx/ 核心 bundle 中包含 C++ backend/test 目录中的算子实现？（当前方案：不逐一覆盖算子实现，聚焦算子注册机制和 Schema 系统）
3. 是否需要生成 bundle 间交叉引用（如 onnxmltools 引用 sklearn-onnx 和 tensorflow-onnx）？（当前方案：在相关概念文档中添加交叉链接）
