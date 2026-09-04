# OpenBLAS 修复与 ResNet50 性能验证 - Product Requirement Document

## Overview
- **Summary**: 基于 hub 真实模型库（30个Caffe模型）网络级综合对比测试发现的 OpenBLAS 线程模型冲突问题，执行一键修复（替换为 openmp 变体），验证修复效果，并将实测结果更新到 caffex-vs-caffe-ffi 技术差距分析报告中。
- **Purpose**: 消除 OpenBLAS pthreads 变体导致的多线程警告与线程过订阅问题，量化修复后的性能变化，将 hub 模型实测结果（精度/性能/权重加载验证）补充到技术差距报告中，形成完整的端到端验证闭环。
- **Target Users**: caffe-ffi 开发者、性能优化工程师

## Goals
- 将 caffe-ffi conda 环境中的 OpenBLAS 从 pthreads 变体替换为 openmp 变体（方案A优先，方案B备用）
- 验证修复后 OpenBLAS 警告消失，且 numpy/caffe-ffi 仍正常工作
- 在修复前后分别运行 ResNet50 前向性能基准，量化性能变化
- 更新 gap_analysis_report.md，加入 hub 30 模型实测结果（A-001 修复验证、精度对比、性能数据、OpenBLAS 问题记录）
- 若 conda 安装失败，提供源码编译 USE_OPENMP=1 的完整命令

## Non-Goals (Out of Scope)
- 不修复因模型拓扑问题导致的 5 个模型失败（fa_rebecca/fd_rebecca*等，属于模型文件本身问题）
- 不实现 caffe-ffi 的 CUDA/GPU 支持
- 不重构 caffe-ffi 的 BLAS 调用层或 GEMM 内核优化
- 不重新运行全部 30 个模型的完整对比（只重点验证 ResNet50 + OpenBLAS 修复）

## Background & Context
- 前序任务（caffe-hub-models-comparison-test）已完成 30 个 hub 模型的网络级对比，结果：
  - A-001 缺陷（read_net 未加载真实权重）已修复，23/24 共同成功模型 max_abs_err < 1e-3
  - 性能差距：caffe-ffi 几何平均延迟为 caffex 的 18.9 倍
  - 测试过程中出现 OpenBLAS 警告："OpenBLAS Warning : ... may cause oversubscription"
- 根因：conda-forge 预装的 `libopenblas 0.3.34 pthreads_h94d23a6_0` 使用 pthread 线程模型，而 caffe-ffi/TVM FFI 上层使用 OpenMP 并行，两种线程模型混用导致过订阅
- 已编写修复脚本 `apps/caffe-ffi-jupyter/scripts/rebuild-openblas-openmp.sh`（含方案A conda快速替换 + 方案B源码编译），尚未在容器中执行验证
- ResNet50 精度对比已完成（100% exact match at 1e-7，Top-5一致5/5），但性能数据是在 pthreads 变体下测得的

## Functional Requirements
- **FR-1**: 在 caffe-ffi-jupyter 容器内执行 OpenBLAS openmp 变体替换（优先使用 conda 方案A）
- **FR-2**: 替换后验证 libopenblas 为 openmp 变体（检查 build string、openblas_config.h 宏、numpy show_config）
- **FR-3**: 修复后运行 OpenBLAS GEMM 基准 + ResNet50 前向基准，记录警告是否消失、性能变化
- **FR-4**: 若 FR-1 的 conda 方案失败（网络不通/包找不到/依赖冲突），执行方案B源码编译（USE_OPENMP=1）并提供详细步骤记录
- **FR-5**: 更新 gap_analysis_report.md，在报告中新增「Hub 模型实测验证」章节，包含：
  - A-001 缺陷修复验证（权重加载真实性）
  - 30 模型成功率统计（25/30 per implementation）
  - 跨实现精度对比（23/24 浮点级一致）
  - 性能基准数据（几何平均延迟比、Top/Bottom模型）
  - OpenBLAS 线程模型问题记录与修复状态

## Non-Functional Requirements
- **NFR-1**: 修复过程不破坏 caffe-ffi 现有功能（numpy 导入、caffe_ffi 导入、ResNet50 前向精度不变）
- **NFR-2**: 性能基准应在修复前后相同条件下执行（相同输入、相同线程数设置、相同warmup次数）
- **NFR-3**: 文档更新保持原有报告风格和结构，新增内容标注更新日期
- **NFR-4**: 源码编译步骤必须可复现（包含所有依赖安装、make参数、安装路径、备份原有库的步骤）

## Constraints
- **Technical**: 容器 caffe-ffi-jupyter 当前网络可能不通（测试中 conda search 因网络失败）；容器内为 Miniconda3 + Python 3.14；OpenBLAS 安装路径为 `/opt/conda/envs/caffe-ffi/lib/`
- **Dependencies**: 依赖已编写的修复脚本 `rebuild-openblas-openmp.sh`；依赖 hub 模型测试结果（`results/` 目录中的 .npy 和 JSON）
- **Platform**: 必须在 WSL2 Ubuntu-24.04 中通过 docker exec 操作容器

## Assumptions
- caffe-ffi-jupyter 容器仍在运行（容器名 `caffe-ffi-jupyter`）
- 容器内 conda 环境名为 `caffe-ffi`
- 修复脚本语法已验证通过（bash -n 检查OK）
- 若 conda 方案因网络失败，方案B源码编译需要 wget 能访问 GitHub 或 tuna 镜像

## Acceptance Criteria

### AC-1: OpenBLAS openmp 变体替换成功
- **Given**: caffe-ffi-jupyter 容器运行中，conda 环境 caffe-ffi 可用
- **When**: 执行 rebuild-openblas-openmp.sh 方案A（或方案B fallback）
- **Then**: `conda list libopenblas` 显示 openmp 变体（build string 含 "openmp"）；numpy.show_config() 链接到新 openblas；`openblas_config.h` 中含 `OPENBLAS_USE_OPENMP` 宏（方案B）或 openmp 符号在库中可检测（方案A）
- **Verification**: `programmatic`

### AC-2: OpenBLAS 警告消失
- **Given**: OpenBLAS 已替换为 openmp 变体
- **When**: 运行 numpy GEMM 大矩阵乘法 + ResNet50 前向推理
- **Then**: stderr 中无 "OpenBLAS Warning"、"pthread_create failed"、"oversubscription" 等警告信息
- **Verification**: `programmatic`

### AC-3: caffe-ffi 功能不退化
- **Given**: OpenBLAS 替换完成
- **When**: `python -c "import caffe_ffi; import numpy as np; print('OK')"`
- **Then**: 导入成功无错误；ResNet50 前向输出与修复前一致（max_abs_err < 1e-5，因 BLAS 实现变化可能有微小差异但不影响 Top-5）
- **Verification**: `programmatic`

### AC-4: ResNet50 性能基准完成（前后对比）
- **Given**: 修复前后环境均可运行 ResNet50
- **When**: 运行 bench_net_forward.py 中的 ResNet50 单模型基准（或独立 GEMM+ResNet50 基准脚本）
- **Then**: 输出 mean/std/min/max 延迟数据，明确记录修复前后的性能变化比例
- **Verification**: `programmatic`

### AC-5: gap_analysis_report.md 更新完成
- **Given**: 修复验证和性能基准数据已获取
- **When**: 编辑 gap_analysis_report.md
- **Then**: 新增「Hub模型实测验证」章节（含 A-001、精度、性能、OpenBLAS）；更新日期刷新；报告中所有数据可追溯到对应结果文件
- **Verification**: `human-judgment`

### AC-6: 源码编译备用方案文档完备（若触发）
- **Given**: conda 方案A失败
- **When**: 执行方案B源码编译
- **Then**: 编译过程记录完整（命令、输出、耗时）；编译后通过 AC-1/2/3/4 验证；在 gap 报告中记录编译步骤要点
- **Verification**: `programmatic` + `human-judgment`

## Open Questions
- [ ] 容器内当前网络状态如何？如果完全断网，方案A conda 替换是否有本地缓存可用？
- [ ] 修复后 OpenBLAS openmp 版本是否会带来性能提升（理论上应该减少线程过订阅开销），还是仅消除警告？
