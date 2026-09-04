# TVM FFI 200 视角深度解读 - 产品需求文档

## Overview
- **Summary**: 对 `d:\AI\.chaos\libs\ffi` 目录下的 TVM FFI（Apache TVM Foreign Function Interface）代码库进行 200 种不同视角的深度解读，每种视角生成一份独立的 OKF v0.2 规范 Wiki 文档。文档内容必须基于源码事实，包含合理分析，并为每个相关视角给出 NPU（神经网络处理器）适配建议。最终产物按 15 个主题分类组织，存放在 `d:\AI\projects\docs` 中。
- **Purpose**: TVM FFI 是 ML 系统领域的关键基础设施，提供稳定的 C ABI、C++17 API、Python（Cython）和 Rust 绑定。通过 200 个视角的系统性解读，建立全面、可溯源、多维度的知识库，帮助开发者深入理解 FFI 设计哲学、实现细节、跨语言交互机制，并为 NPU 硬件适配提供实践指导。
- **Target Users**: ML 系统工程师、NPU 驱动开发者、编译器工程师、跨语言绑定开发者、对 FFI 设计感兴趣的架构师。

## Goals
- 生成恰好 200 份独立的 OKF Wiki 概念文档，覆盖 TVM FFI 的全部关键维度
- 每份文档内容真实可靠，所有 API 引用、类名、方法签名均经源码 Grep 验证
- 按 15 个主题分类合理组织，形成清晰的学习路径
- 为与硬件/加速器相关的视角提供具体的 NPU 适配建议
- 遵循 source-code-to-okf-wiki 工作流（R→I→E→V→C），杜绝虚构 API
- 遵循 seven-concepts 方法论编排（知识沉淀场景：R→I→E 链路）
- 每份文档符合 OKF v0.2 frontmatter 规范

## Non-Goals (Out of Scope)
- 不修改 `d:\AI\.chaos\libs\ffi` 中的任何源码（只读分析）
- 不构建或编译 TVM FFI 或 TVM
- 不运行测试套件
- 不生成视频、PPT 等非 Markdown 格式产出物
- 不为 200 个视角全部提供 NPU 建议——仅对与硬件加速、张量、设备、内核、运行时等相关的视角提供（约 50-80 个）
- 不翻译现有官方文档，而是基于源码生成原创解读
- 不创建 awesome-okf-xs 子项目内的 bundle（产出物在 projects/docs 独立目录）

## Background & Context

### 代码库结构
`d:\AI\.chaos\libs\ffi` 包含两个子项目：

1. **tvm-ffi/** — 独立的 FFI 库（核心分析对象）
   - `include/tvm/ffi/`: C++ 公开头文件（any.h, c_api.h, cast.h, dtype.h, enum.h, error.h 等）
   - `src/ffi/`: C++ 实现（backtrace.cc, container.cc, dtype.cc, error.cc, function.cc, init_once.cc, object.cc, tensor.cc, extra/module.cc）
   - `python/tvm_ffi/`: Python 包（core.pyi, error.py, py.typed）
   - `rust/tvm-ffi/`: Rust crate（any.rs, lib.rs, Cargo.toml, build.rs）
   - `tests/cpp/`: 10 个 GoogleTest 文件
   - `3rdparty/dlpack/`: DLPack 依赖

2. **tvm/** — TVM 编译器框架（FFI 的主要消费者）
   - 完整的 IR 系统（arith, ir, relax, s_tir, tirx, te, topi）
   - 运行时（vm, rpc, thread_pool, module）
   - 目标代码生成（CUDA, LLVM, Metal, OpenCL, ROCm, Vulkan, Hexagon）
   - Python/TypeScript/JVM 绑定
   - `3rdparty/tvm-ffi/` 作为子模块

### 关键架构概念
- **Any/AnyView**: 类型擦除值容器（AnyView 非拥有，Any 拥有）
- **Object 系统**: 引用计数堆对象（ObjectObj 数据 + ObjectRef 包装器）
- **Function**: 类型擦除可调用对象，packed 调用约定
- **TVMFFIAny**: 16 字节 C 结构体，包含 type_index + union
- **Global Registry**: 按字符串名注册函数，跨语言访问
- **Containers**: Array/List/Map/Dict/String/Tensor/Shape/Tuple/Variant
- **Reflection**: ObjectDef 构建器，def_field/def_method
- **DLPack**: 零拷贝张量交换协议

### 方法论选择
根据 seven-concepts-cmd 决策树，本任务属于**场景4：知识沉淀**，链路为 R→I→E：
- R（复盘）：采集源码事实，建立编号事实清单
- I（洞察）：提炼核心架构洞察，设计知识地图
- E（萃取/执行）：批量生成 OKF 文档

source-code-to-okf-wiki 技能提供五阶段工作流：R→I→E→V→C，本任务完整执行。

## Functional Requirements

- **FR-1**: 产出 200 份独立的 OKF Wiki 概念文档，每份文档有唯一编号（001-200）和明确标题
- **FR-2**: 文档按 15 个主题分类组织，每个分类有独立的 bundle 目录和 index.md
- **FR-3**: 每份文档包含：概述、源码分析（含具体文件/行号引用）、设计解读、相关概念链接
- **FR-4**: 与硬件/加速器相关的文档必须包含"NPU 建议"章节
- **FR-5**: 每份文档遵循 OKF v0.2 frontmatter 规范（type, title, description, tags, generated, verified, status, sources）
- **FR-6**: 文档正文使用中文，文件名使用 kebab-case 纯英文
- **FR-7**: 创建总索引 index.md 链接所有 15 个分类和 200 份文档
- **FR-8**: 每个分类 bundle 包含 concepts/、examples/（可选）、references/ 子目录
- **FR-9**: references/ 信源文件先于 concepts/ 生成（信源先行原则）
- **FR-10**: 各级 index.md 最后生成

## Non-Functional Requirements

- **NFR-1**: 所有文档引用的类名、方法名、结构体字段必须能在源码中通过 Grep 验证存在
- **NFR-2**: 文档中不得出现虚构的 API、不存在的文件路径或编造的设计决策
- **NFR-3**: 每份概念文档长度 800-3000 字，确保深度但不冗余
- **NFR-4**: 代码块标注语言（cpp/python/rust/c）
- **NFR-5**: 交叉链接使用 `/` 开头的 bundle-relative 路径
- **NFR-6**: 每批生成文档不超过 7 份（防止上下文过载）
- **NFR-7**: V 阶段对每份文档的 API 引用进行 Grep 级验证

## Constraints

- **Technical**:
  - 源码路径：`d:\AI\.chaos\libs\ffi\tvm-ffi` 和 `d:\AI\.chaos\libs\ffi\tvm`
  - 产出路径：`d:\AI\projects\docs`
  - 文档格式：Markdown + YAML frontmatter（OKF v0.2）
  - 操作系统：Windows（路径分隔符注意事项）
- **Business**:
  - 不修改源码（只读分析）
  - 内容必须基于 Apache 2.0 许可的 TVM FFI 源码
- **Dependencies**:
  - source-code-to-okf-wiki skill 的 R→I→E→V→C 工作流
  - seven-concepts-cmd 的方法论编排
  - Grep 工具用于 API 验证

## Assumptions

- TVM FFI 源码版本为 v0.1.13（从 c_api.h 中 TVM_FFI_VERSION_PATCH=13 推断）
- TVM 目录是 TVM 的一个 fork，包含 tirx（Tensor IR Extended）扩展
- 用户具备 C++、Python、Rust 和 FFI 概念的基础知识
- NPU 建议基于通用 NPU 架构模式（参考 VTA、npu-ffi 项目），不针对特定厂商硬件
- `d:\AI\projects\docs` 目录不存在或为空，可自由创建

## Acceptance Criteria

### AC-1: 文档数量完整性
- **Given**: 产出目录 `d:\AI\projects\docs`
- **When**: 统计所有分类下的概念文档数量
- **Then**: 概念文档总数恰好为 200 份
- **Verification**: `programmatic`

### AC-2: 主题分类覆盖
- **Given**: 15 个主题分类
- **When**: 检查每个分类的文档数量
- **Then**: 每个分类至少有 10 份文档，总数为 200
- **Verification**: `programmatic`

### AC-3: API 真实性
- **Given**: 文档中引用的所有 C++ 类名、方法名、结构体字段
- **When**: 在源码目录中执行 Grep 搜索
- **Then**: 每个引用的符号均能在源码中找到匹配（排除标准库/第三方库符号）
- **Verification**: `programmatic`

### AC-4: Frontmatter 规范性
- **Given**: 每份概念文档
- **When**: 检查 YAML frontmatter
- **Then**: 包含 type/title/description/tags/generated/verified/status/sources 字段，格式符合 OKF v0.2
- **Verification**: `programmatic`

### AC-5: 链接完整性
- **Given**: 所有 Markdown 交叉链接
- **When**: 检查链接目标是否存在
- **Then**: 无断裂链接
- **Verification**: `programmatic`

### AC-6: NPU 建议覆盖
- **Given**: 与硬件/加速器相关的文档（张量、设备、内核、运行时、代码生成等类别）
- **When**: 检查文档内容
- **Then**: 每份相关文档包含"## NPU 建议"章节，提供具体可操作的建议
- **Verification**: `human-judgment`

### AC-7: 内容深度与质量
- **Given**: 每份概念文档
- **When**: 审查文档内容
- **Then**: 包含概述、源码引用（含文件路径和行号）、设计分析、相关概念，内容有实质深度
- **Verification**: `human-judgment`

### AC-8: 索引完整性
- **Given**: 总索引和各分类索引
- **When**: 检查索引链接
- **Then**: 总索引链接所有 15 个分类，每个分类索引列出其下所有概念文档
- **Verification**: `programmatic`

### AC-9: 信源先行
- **Given**: 每个 bundle 目录
- **When**: 检查文件生成顺序和 references/ 内容
- **Then**: references/ 信源文件存在且被 concepts/ 文档的 sources 字段引用
- **Verification**: `programmatic`

### AC-10: 中文撰写
- **Given**: 所有文档正文
- **When**: 检查语言
- **Then**: 正文使用规范现代汉语，技术术语首次出现时附英文注释
- **Verification**: `human-judgment`

## Open Questions

- [ ] NPU 建议是否需要针对特定 NPU 硬件（如华为昇腾、寒武纪）？当前假设为通用 NPU 架构建议。
- [ ] 是否需要为每份文档生成 examples/ 示例代码？当前假设 examples/ 为可选，仅在必要时创建。
- [ ] TVM 编译器部分（tirx/relax/topi）的分析深度如何把握？当前假设聚焦于 FFI 机制在 TVM 中的应用，不深入编译器优化算法。
