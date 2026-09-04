---
id: caffex-ops-test-execution-report
title: Caffex算子库Docker环境全面测试与标准化报告生成
source: 用户指令 /spec
created: 2026-07-28
---

# Caffex 算子库 Docker 环境全面测试与标准化报告生成 - Product Requirement Document

## Overview
- **Summary**: 在 `docker/origin` 的 `caffe-cpu:origin-runtime` Docker 镜像环境中，对 `caffex` 算子库（`tests/ops/`）执行全面测试（功能正确性、性能基准、边界条件、兼容性），并生成标准化 Markdown 测试报告，保存至 `tests/.temp/` 目录。报告需包含测试用例详情、通过率、性能指标、错误日志及分析结果，确保测试过程可复现。
- **Purpose**: 现有测试框架（utils.py + pytest markers + Docker脚本）已静态准备就绪，但尚未在真实 Docker 环境中完整运行并生成结构化报告。本任务将完成从测试执行到报告产出的完整闭环，为 caffex 算子库提供可审计的质量基线。
- **Target Users**: caffex 开发者、算法工程师、质量保证团队、CI/CD 维护者

## Goals
- 在 Docker origin 环境中按类别（correctness/performance/edge/all）运行算子测试
- 采集四类测试数据：功能正确性验证结果、性能基准数据、边界条件测试结果、兼容性覆盖情况
- 解析 pytest JUnit XML 输出和原始日志，提取结构化数据
- 生成标准化 Markdown 测试报告（含环境信息、摘要统计、详细结果、性能排名、失败分析）
- 将报告及原始数据文件保存到 `tests/.temp/` 目录
- 确保测试命令和参数可复现（记录在报告中）

## Non-Goals (Out of Scope)
- 不新建或重写算子测试用例（使用现有 tests/ops/ 下的32个测试文件）
- 不修改 caffex/ 目录下的 BVLC 原始源码
- 不做 GPU/CUDA 测试（origin 镜像为 CPU-only）
- 不做训练/Solver相关测试（仅推理/前向算子测试）
- 不做性能优化（只测量和记录，不调优）
- 不修复发现的算子 bug（仅记录和定位，修复作为后续任务）
- networks/ 目录下的端到端模型测试不在范围内

## Background & Context
- **项目位置**:
  - caffex 源码: `projects/xuanspace/vendor/caffe/caffex/`
  - 算子测试: `projects/xuanspace/vendor/caffe/tests/ops/`（32个 test_*.py 文件）
  - origin Docker: `projects/xuanspace/vendor/caffe/docker/origin/`
  - 报告输出: `projects/xuanspace/vendor/caffe/tests/.temp/`
- **已有基础设施**:
  - Docker 镜像: `caffe-cpu:origin-runtime`（Ubuntu 22.04 + Python 3.10 + numpy 1.x + protobuf 3.20.3）
  - 测试框架: pytest，markers 定义（caffe/slow/edge/correctness/performance/memory）
  - 工具库: `tests/ops/utils.py`（含 Timer、assert_op_correct、check_memory_leak、TestResultCollector）
  - 运行脚本: `docker/origin/run_ops_tests.sh`（支持5种测试类型，输出 JUnit XML 到 test-results/）
- **当前缺口**:
  - `run_ops_tests.sh` 默认结果目录为 `docker/origin/test-results/`，需适配到 `tests/.temp/`
  - 缺少 `test_memory.py`（内存专项测试文件）
  - 缺少性能基准测试的专项测试文件（现有各测试文件中部分带有 @pytest.mark.slow 标记）
  - 缺少报告生成脚本（generate_report.py 不存在）
  - 从未在 Docker 中完整运行过测试套件
- **测试文件清单**（32个）:
  激活函数类: test_relu, test_sigmoid, test_tanh, test_prelu, test_power, test_elu, test_swish, test_exp, test_log, test_clip, test_threshold
  卷积池化类: test_convolution, test_deconvolution, test_pooling
  归一化正则化: test_batchnorm, test_lrn, test_dropout, test_scale
  形状操作类: test_concat, test_slice, test_reshape, test_flatten, test_permute, test_crop, test_tile
  其他算子: test_eltwise, test_inner_product, test_softmax, test_reduction, test_embed, test_argmax

## Functional Requirements
- **FR-1**: 环境验证 - 在运行测试前验证 Docker 镜像存在、caffe可导入、pytest可运行，输出环境信息
- **FR-2**: 测试执行编排 - 依次运行 correctness、edge、performance（slow标记）三类测试；如 test_memory.py 不存在则跳过内存专项但记录
- **FR-3**: 结果目录适配 - 修改或创建运行脚本，将测试输出（JUnit XML、日志、coverage）定向到 `tests/.temp/`
- **FR-4**: 数据采集 - 从 JUnit XML 解析测试用例详情（名称、状态、耗时、错误信息），从 stdout 提取性能计时数据
- **FR-5**: 报告生成 - 创建报告生成脚本（generate_report.py），从原始数据生成结构化 Markdown 报告
- **FR-6**: 报告内容 - 报告必须包含：
  1. 测试元信息（时间、环境、镜像版本、命令复现步骤）
  2. 执行摘要（总用例数、通过/失败/跳过/错误数、总耗时、整体通过率）
  3. 分类型结果（correctness/edge/performance 各自的通过率）
  4. 算子维度汇总（每个算子的测试状态）
  5. 性能基准表（如有性能数据：各算子平均耗时、排名）
  6. 失败用例详情（失败的测试名、错误消息、traceback 摘要、复现步骤）
  7. 边界条件测试覆盖情况
  8. 兼容性测试说明（多形状/多维度覆盖情况）
  9. 问题清单与初步分析
  10. 附录（原始日志路径、复现命令）
- **FR-7**: 可复现性 - 报告中记录完整的 docker run 命令、pytest 参数、随机种子设置，确保他人可复现

## Non-Functional Requirements
- **NFR-1**: 报告格式 - Markdown，使用表格、代码块、分级标题，便于阅读和版本控制
- **NFR-2**: 数据完整性 - 原始 JUnit XML 和 pytest 日志必须随报告一起保存到 .temp/ 目录
- **NFR-3**: 健壮性 - 即使部分测试失败，报告生成也不应中断；测试退出码非0时报告仍需生成（标注失败状态）
- **NFR-4**: 中文报告 - 报告主体使用中文，技术术语保留英文
- **NFR-5**: 幂等性 - 重复运行测试不会破坏已有报告（使用时间戳目录或覆盖机制）

## Constraints
- **Technical**:
  - 必须使用 `docker/origin` 的 `caffe-cpu:origin-runtime` 镜像
  - 必须在 Docker 容器内运行测试（通过 docker run 或 wslc）
  - 容器内 Python 3.10 + protobuf 3.20.3 + numpy 1.x 环境
  - 不修改 caffex/ 源码；测试代码修改仅限 tests/ops/ 和 docker/origin/ 下
  - 宿主机为 Windows，Docker 运行脚本需考虑 PowerShell/WSL 兼容
- **Business**:
  - 报告保存到 `tests/.temp/` 目录
  - 四类测试必须都覆盖（功能/性能/边界/兼容性）
- **Dependencies**:
  - Docker Desktop 运行中
  - caffe-cpu:origin-runtime 镜像已构建（或可现场构建）
  - pytest + pytest-cov 在容器内可通过 pip 安装

## Assumptions
- Docker 在宿主机可用且 `docker info` 正常
- caffe-cpu:origin-runtime 镜像存在或 `build.sh` 可成功构建
- 现有32个测试文件语法正确、导入无误（已静态验证通过）
- 容器内可以访问阿里云 PyPI 镜像（pip install 源已在 Dockerfile 中配置）
- Windows 环境可以通过 PowerShell 调用 docker 命令或通过 WSL 运行 .sh 脚本

## Acceptance Criteria

### AC-1: Docker 测试环境就绪
- **Given**: Docker Desktop 运行中，caffe-cpu:origin-runtime 镜像存在
- **When**: 执行环境验证步骤（docker run --rm 镜像 verify-caffe.sh）
- **Then**: Caffe 可正常导入，版本信息正确，12项验证全部通过
- **Verification**: `programmatic`

### AC-2: 功能正确性测试完成执行
- **Given**: Docker 环境就绪
- **When**: 运行 correctness 类型测试（pytest -m "correctness and not slow"）
- **Then**: JUnit XML 结果文件生成，包含所有 correctness 标记的测试用例结果
- **Verification**: `programmatic`

### AC-3: 边界条件测试完成执行
- **Given**: Docker 环境就绪
- **When**: 运行 edge 类型测试（pytest -m "edge"）
- **Then**: 所有 edge 标记的测试用例执行完毕，结果记录到 JUnit XML
- **Verification**: `programmatic`

### AC-4: 性能基准测试完成执行
- **Given**: Docker 环境就绪
- **When**: 运行 slow/performance 标记测试（pytest -m "slow"）
- **Then**: 性能测试执行完毕，耗时数据采集完整
- **Verification**: `programmatic`
- **Notes**: 若性能测试用例数量不足，在报告中说明覆盖范围

### AC-5: 测试输出正确保存到 tests/.temp/
- **Given**: 测试执行完毕
- **When**: 检查 tests/.temp/ 目录
- **Then**: 包含 junit XML 文件、pytest 完整日志、覆盖率报告（如有）、生成的 Markdown 报告
- **Verification**: `programmatic`

### AC-6: 标准化测试报告生成
- **Given**: 所有测试数据已采集
- **When**: 运行报告生成脚本
- **Then**: 生成 Markdown 报告，包含 FR-6 要求的全部10个章节
- **Verification**: `human-judgment`

### AC-7: 报告数据准确性
- **Given**: 报告已生成
- **When**: 人工核对报告中的通过率、失败数量与 JUnit XML 数据
- **Then**: 报告统计数据与原始测试结果一致，失败用例列表完整
- **Verification**: `human-judgment`

### AC-8: 测试可复现
- **Given**: 报告已生成
- **When**: 按照报告中记录的命令步骤重新执行
- **Then**: 可以在相同环境下复现测试过程（结果可能因随机性有微小差异，但命令可运行）
- **Verification**: `human-judgment`

## Open Questions
- [ ] 宿主机是 Windows，run_ops_tests.sh 是 bash 脚本，需要确认是通过 WSL/git-bash 运行还是创建 PowerShell 版本？
- [ ] 完整测试（含 performance/slow）的预期执行时间？是否需要设置超时？
- [ ] 如果镜像不存在，是否需要在任务中先执行 `build.sh` 构建镜像？
- [ ] 报告文件名是否需要包含时间戳（避免覆盖）还是固定文件名？
