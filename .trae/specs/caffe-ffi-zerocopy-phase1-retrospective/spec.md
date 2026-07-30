# caffe-ffi Split层零拷贝优化 Phase 1 里程碑复盘报告 - Product Requirement Document

## Overview
- **Summary**: 使用七概念方法论（R→I→E→C链路）对 caffe-ffi 项目 Split 层零拷贝优化 Phase 1（N=1 零拷贝捷径）进行系统性里程碑复盘，产出包含客观事实清单、核心洞察、可复用模式、原子行动项的结构化复盘报告。
- **Purpose**: 
  - 还原 Phase 1 从零拷贝设计到验证通过的完整过程
  - 识别开发过程中的关键决策点、踩坑经验和本质问题
  - 沉淀"基于 TVM FFI 引用计数的零拷贝张量共享"可复用模式
  - 为 Phase 2 (N≥2 COW) 提供经验指导和风险预警
  - 输出标准化复盘报告供团队参考
- **Target Users**: caffe-ffi 开发团队、性能优化工程师、后续 Phase 2 实施者

## Goals
- G1: 采集≥20条 Phase 1 开发过程的客观事实（时间线、文件变更、Bug、修复、测试结果），无因果推断词
- G2: 产出≥3条核心洞察（每条含现象描述/根因分析/影响评估/改进建议四元组）
- G3: 萃取1-2个可复用模式（FFI零拷贝共享模式 + Windows DLL 环境调试模式），包含触发场景/核心步骤/反模式/迁移验证
- G4: 产出≥3个原子行动项（针对Phase 2 COW实施的预防性建议），每个可独立验证
- G5: 导出完整结构化复盘报告到 caffe-ffi/docs/ 目录，包含所有阶段产出

## Non-Goals (Out of Scope)
- 不实现 Phase 2 COW 代码（本次仅为复盘+规划指导）
- 不修改 caffe-ffi 子项目内的源代码文件（仅在 SpecWeave 主权区 docs/ 下产出报告）
- 不进行代码提交（本次任务无代码变更，C阶段为导出报告而非 atomic commit）
- 不重新运行完整构建测试（基于已验证的测试结果进行复盘）
- 不覆盖 Phase 2 COW 的详细设计实现（已有独立设计草稿 SPLIT_COW_PHASE2_DESIGN_DRAFT.md）

## Background & Context
- **前置工作**：已完成 Split 层 Phase 1 N=1 零拷贝优化，包括：
  - Blob 类新增 ShareData()/ShareDiff()/SharesDataWith()/SharesDiffWith() 方法
  - SplitLayer::Forward_cpu() N=1 路径走零拷贝捷径（refcount 共享替代 memcpy）
  - C++ 单元测试（test_blob_zerocopy.cpp）验证指针共享和引用计数
  - Python P2-B 回归测试 29 项通过
  - CSV 性能日志确认 Δmem=-64B（N=1 场景内存节省）
  - Windows 一键回归测试脚本（run_p2b_regression.cmd）
  - CMake 集成测试目标
  - Phase 2 COW 设计草稿已完成
- **技术栈**：C++17, TVM FFI (v0.1.13rc3), CMake, Ninja, Python 3.14, pytest, Conda
- **关键挑战**：
  - TypeTraits 重复定义导致的编译错误
  - ObjectPtr 与原始指针 API 兼容性
  - Windows DLL 加载路径问题（tvm_ffi.dll, OpenMP KMP_DUPLICATE_LIB_OK）
  - CMake Unity Build 模板实例化顺序问题
- **相关文档**：
  - `projects/xuanspace/libs/caffe-ffi/docs/SPLIT_ZEROCOPY_DESIGN_DRAFT.md`（原始设计草稿）
  - `projects/xuanspace/libs/caffe-ffi/docs/P1_OPTIMIZATION_REPORT_20260729.md`（P1优化报告）
  - `projects/xuanspace/libs/caffe-ffi/docs/SPLIT_COW_PHASE2_DESIGN_DRAFT.md`（Phase 2 COW 设计草稿）

## Functional Requirements
- **FR-1**: R阶段（复盘）必须采集客观事实清单，覆盖以下维度：
  - 时间线：各关键节点的时间顺序
  - 文件变更：新增/修改的文件列表及变更内容
  - Bug记录：编译错误、运行时错误、DLL加载失败等问题
  - 修复记录：每个问题的解决方案和修改点
  - 测试结果：C++单元测试和Python测试的结果数据
  - 性能数据：ZEROCOPY日志、CSV性能日志的关键指标
- **FR-2**: I阶段（洞察）必须包含≥3条结构化洞察，每条必须有四元组：
  - 现象描述：发生了什么（引用事实编号）
  - 根因分析：为什么会发生（5Why追问到本质）
  - 影响评估：造成了什么影响（时间/质量/复杂度）
  - 改进建议：下次如何预防/改进
- **FR-3**: E阶段（萃取）必须产出≥1个可复用模式：
  - 模式名称和概述
  - 触发场景（什么情况下适用）
  - 核心步骤（按执行顺序）
  - 反模式（什么情况下不该用/常见错误）
  - 迁移验证（如何验证模式应用成功）
- **FR-4**: C阶段（导出报告）必须产出完整复盘报告：
  - 报告包含执行摘要、事实清单、洞察分析、模式萃取、行动项、Phase 2 风险预警
  - 使用 Markdown 格式，带 YAML frontmatter
  - 存放在 `projects/xuanspace/libs/caffe-ffi/docs/` 目录
  - 包含文件交叉引用（使用相对路径链接到相关代码文件）

## Non-Functional Requirements
- **NFR-1**: 事实清单无因果推断词（"因为"、"导致"、"所以"、"错误"、"失误"），G1质量门
- **NFR-2**: 洞察四元组完整且引用事实编号，G2质量门
- **NFR-3**: 模式可迁移到至少1个非当前场景（如其他层的零拷贝优化），G3质量门
- **NFR-4**: 行动项满足原子化标准（单一职责、可独立验证、有明确验收标准），G4质量门
- **NFR-5**: 报告语言为中文（与用户输入语言一致）
- **NFR-6**: 所有代码引用使用 clickable 绝对路径格式

## Constraints
- **Technical**: 
  - 不修改 caffe-ffi 子项目内的代码文件（仅新增报告文档到 docs/ 目录）
  - 基于现有会话上下文和已验证结果进行复盘，不重新编译构建
  - 遵循 caffe-ffi 子项目文档规范（frontmatter、相对路径引用）
- **Business**: 
  - 复盘报告需为 Phase 2 COW 实施提供可操作的指导
- **Dependencies**:
  - 依赖七概念方法论编排规范（seven-concepts-cmd）
  - 依赖已有的测试结果和性能数据
  - 依赖 export-report-cmd 用于最终报告导出

## Assumptions
- A1: 会话上下文中包含 Phase 1 开发过程的足够信息（文件变更、Bug修复、测试结果）
- A2: Phase 1 零拷贝优化已被验证为正确（C++/Python测试通过，CSV日志确认内存节省）
- A3: 无需进行额外的对抗审查（V阶段），因为本次是标准里程碑复盘（depth=standard，单模块复盘可跳过V）
- A4: 报告存放在 caffe-ffi/docs/ 目录是可接受的（属于子项目的文档产出）

## Acceptance Criteria

### AC-1: 客观事实清单完整性
- **Given**: Phase 1 零拷贝优化已完成
- **When**: 执行 R（复盘）阶段
- **Then**: 产出≥20条客观事实，覆盖时间线/文件变更/Bug/修复/测试/性能6个维度，无因果推断词
- **Verification**: `programmatic`（检查事实数量和因果词过滤）
- **Notes**: 事实必须可追溯到具体文件或日志

### AC-2: 核心洞察四元组完整性
- **Given**: 客观事实清单已通过 G1 质量门
- **When**: 执行 I（洞察）阶段
- **Then**: 产出≥3条洞察，每条包含现象描述（引用事实编号）、根因分析（5Why）、影响评估、改进建议四个要素
- **Verification**: `human-judgment`（检查四元组完整性和根因深度）

### AC-3: 可复用模式可迁移性
- **Given**: 核心洞察已通过 G2 质量门
- **When**: 执行 E（萃取）阶段
- **Then**: 产出≥1个结构化模式，包含触发场景/核心步骤/反模式/迁移验证四要素，且能迁移到≥1个非Split层场景
- **Verification**: `human-judgment`（评审模式抽象层级和迁移性）

### AC-4: 原子行动项可执行性
- **Given**: 模式萃取已通过 G3 质量门
- **When**: 执行 C（行动项/报告导出）阶段
- **Then**: 产出≥3个原子行动项，每个满足单一职责、可独立验证、有明确验收标准
- **Verification**: `human-judgment`（检查行动项原子性）

### AC-5: 复盘报告完整性和格式规范
- **Given**: 所有阶段产出已通过对应质量门
- **When**: 导出最终报告
- **Then**: 报告包含执行摘要/事实清单/洞察/模式/行动项/Phase2风险预警6个章节，Markdown格式正确，frontmatter完整，代码引用使用可点击路径
- **Verification**: `human-judgment`（整体报告质量评审）

### AC-6: 报告文件正确存放
- **Given**: 报告内容已生成
- **When**: 写入文件系统
- **Then**: 报告文件存放在 `projects/xuanspace/libs/caffe-ffi/docs/` 目录下，文件名包含日期标识
- **Verification**: `programmatic`（检查文件存在性和路径）

## Open Questions
- [ ] 是否需要在本次复盘中加入对抗审查（V阶段）？（当前假设为不需要，单模块标准复盘）
- [ ] 报告文件名命名规范：是使用 `ZEROCOPY_PHASE1_RETROSPECTIVE_20260731.md` 还是其他格式？
- [ ] 行动项是否需要分配优先级和预估工时？
