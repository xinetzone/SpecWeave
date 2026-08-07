# OpenBLAS 修复与 ResNet50 性能验证 - The Implementation Plan

## [x] Task 1: 容器环境预检与 OpenBLAS 当前状态记录
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 检查 caffe-ffi-jupyter 容器是否运行
  - 记录当前 OpenBLAS 变体（pthreads/openmp）、版本、build string
  - 记录 numpy.show_config() BLAS 信息
  - 测试容器网络连通性（conda-forge/tuna）
  - 先运行一次 ResNet50 前向基准作为 baseline（记录延迟和警告输出）
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker ps` 显示 caffe-ffi-jupyter 容器在运行
  - `programmatic` TR-1.2: `conda list libopenblas` 输出记录到日志，确认当前为 pthreads 变体
  - `programmatic` TR-1.3: ResNet50 前向 baseline 运行成功，记录 mean/std 延迟和 stderr 警告
  - `programmatic` TR-1.4: 网络连通性测试结果记录（curl conda-forge/tuna 各一次）

## [x] Task 2: 执行 OpenBLAS openmp 变体替换（方案A conda 优先）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 rebuild-openblas-openmp.sh 脚本拷贝到容器内（或通过 docker exec 直接执行）
  - 执行 `bash scripts/rebuild-openblas-openmp.sh --method=A --verify`（有网络时）
  - 若容器无网络，使用本地 conda 缓存或尝试国内 tuna/bfsu 镜像
  - 若 conda 完全不可用（无缓存、无网络），标记失败并转 Task 2B
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 命令退出码为0
  - `programmatic` TR-2.2: `conda list libopenblas` 显示 build string 含 "openmp"
  - `programmatic` TR-2.3: `python -c "import caffe_ffi; import numpy"` 无报错

## [ ] Task 2B: 方案B源码编译（仅在 Task 2 失败时执行）
- **Priority**: high
- **Depends On**: Task 2 (failure)
- **Description**:
  - 安装编译依赖（build-essential, gfortran）
  - 下载 OpenBLAS 0.3.28 源码（tuna镜像优先）
  - 执行 `make USE_OPENMP=1 DYNAMIC_ARCH=1 TARGET=HASWELL NUM_THREADS=64 NO_AFFINITY=1 USE_LOCKING=1 -j$(nproc)`
  - `make PREFIX=/opt/conda/envs/caffe-ffi install`
  - 备份原有 libopenblas，更新符号链接，ldconfig
  - 记录完整编译日志和耗时
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-2B.1: make 和 make install 退出码为0
  - `programmatic` TR-2B.2: 新 libopenblas.so 已安装到 conda 环境 lib 目录
  - `programmatic` TR-2B.3: `strings libopenblas.so | grep -i openmp` 能找到 OpenMP 相关符号
  - `programmatic` TR-2B.4: 编译步骤、命令、输出、耗时记录完整

## [x] Task 3: 修复后验证（功能 + 警告消除 + 精度不变）
- **Priority**: high
- **Depends On**: Task 2 (or Task 2B)
- **Description**:
  - 运行脚本内置的 --verify 验证（numpy GEMM 测试 + caffe_ffi 导入测试）
  - 运行独立验证脚本：GEMM 大矩阵乘法（2048x2048 float32）+ ResNet50 前向推理
  - 捕获 stderr 检查是否有 OpenBLAS 警告
  - 对比修复前后 ResNet50 输出精度（Top-5是否一致，max_abs_err）
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: GEMM 测试运行成功，stderr 无 "OpenBLAS Warning"
  - `programmatic` TR-3.2: ResNet50 前向推理成功，stderr 无 "OpenBLAS Warning"
  - `programmatic` TR-3.3: ResNet50 Top-5 类别与修复前一致
  - `programmatic` TR-3.4: max_abs_err < 1e-5（允许因 BLAS 线程调度变化导致的微小数值差异）

## [x] Task 4: ResNet50 性能基准（修复后）与前后对比
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在修复后的环境中重新运行 ResNet50 前向性能基准（多次迭代取平均，设置 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4）
  - 对比 Task 1 中记录的 baseline 数据
  - 计算延迟变化比例和 FPS 变化
  - 额外测试不同线程数（1/2/4/8）下的性能曲线
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 修复后 ResNet50 前向 mean 延迟记录到结果文件
  - `programmatic` TR-4.2: 输出修复前 vs 修复后的延迟对比表（mean/std/min/max）
  - `programmatic` TR-4.3: 明确标注警告是否消失
  - `programmatic` TR-4.4: 输出性能变化百分比（加速比或减速比）

## [x] Task 5: 更新 gap_analysis_report.md
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 在报告九（总结）之前新增「十、Hub 模型实测验证（2026-08-06）」章节
  - 子章节包含：A-001 缺陷修复验证、30模型成功率、跨实现精度对比、性能基准、OpenBLAS线程模型问题与修复
  - 更新报告顶部日期为 2026-08-06
  - 在核心结论中补充实测结论
  - 保持原有报告风格和 Markdown 格式
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-5.1: 新章节结构清晰，数据可追溯（指向 results/ 目录中的具体文件）
  - `human-judgement` TR-5.2: 报告日期已更新
  - `programmatic` TR-5.3: 新增内容包含 A-001 验证数据、25/30 成功率、23/24 精度一致、几何平均延迟比、OpenBLAS 修复状态五个关键信息
  - `human-judgement` TR-5.4: 原有内容未被意外修改或删除
