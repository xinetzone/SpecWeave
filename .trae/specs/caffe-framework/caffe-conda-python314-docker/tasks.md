---
version: 1.0
---

# Caffe Conda Python 3.14 Docker 镜像 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 docker/conda-cpu 目录结构
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `d:\spaces\SpecWeave\external\chaos\caffe\docker\` 下创建 `conda-cpu/` 子目录
  - 确认目录结构正确，为后续文件创建做准备
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录 `d:\spaces\SpecWeave\external\chaos\caffe\docker\conda-cpu\` 存在
- **Notes**: 原有的 cpu/ 和 gpu/ 目录保留不动，新方案放在 conda-cpu/ 下

## [ ] Task 2: 调研并选择基础镜像和依赖版本
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 通过 Docker Hub 或网络搜索确认 Python 3.14 在 conda-forge 上的可用性
  - 选择基础镜像：优先使用 `condaforge/miniforge3`（mamba 更快，预装 conda-forge 源）
  - 确认 Caffe 所需系统依赖在 Debian/Ubuntu 基础镜像中的包名
  - 列出需要通过 conda 安装 vs apt 安装 vs pip 安装的依赖清单
  - 特别注意 Python 3.14 兼容性问题（protobuf 版本、Cython 版本、boost-python 等）
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 依赖清单完整，分类清晰（apt/conda/pip）
  - `human-judgement` TR-2.2: 基础镜像选择有明确理由
  - `programmatic` TR-2.3: 确认 conda-forge 上有 Python 3.14 包
- **Notes**: Python 3.14 很新，可能需要使用 pip 安装部分包而非 conda；如果 protobuf 版本有冲突，可能需要使用旧版 protobuf（3.x）

## [ ] Task 3: 编写 Dockerfile（单阶段版本先验证可行性）
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 基于 miniforge3 基础镜像
  - 安装系统依赖（apt-get）
  - 创建 conda 环境 `caffe`，Python=3.14
  - 安装 Python 依赖（先 conda 再 pip）
  - 复制本地 caffex/ 源码到容器内
  - 配置 Makefile.config（CPU_ONLY:=1，Python 路径指向 conda 环境）
  - 编译 Caffe 和 PyCaffe
  - 设置环境变量（CAFFE_ROOT, PYTHONPATH, PATH, LD_LIBRARY_PATH）
  - 设置工作目录 /workspace
  - 先写单阶段版本验证编译可行性，不急于做镜像优化
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-3.1: Dockerfile 语法正确（可通过 docker build 解析）
  - `human-judgement` TR-3.2: Dockerfile 有清晰的注释说明每个阶段
- **Notes**: 重点关注 Makefile.config 的配置，特别是 PYTHON_INCLUDE 和 PYTHON_LIB 路径需要指向 conda 环境；Caffe 旧代码可能需要处理 C++11/14/17 兼容性问题

## [ ] Task 4: 编写环境配置文件（environment.yml 或 requirements.txt）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 创建 `environment.yml` 定义 conda 环境的 Python 依赖
  - 对于 conda 无法安装的包，使用 `requirements-pip.txt`
  - 确保版本兼容 Python 3.14
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 依赖列表与 caffex/python/requirements.txt 对应
  - `human-judgement` TR-4.2: 版本约束合理，不锁死不必要的版本
- **Notes**: 优先使用 conda-forge 源的包；numpy 2.x 可能有 ABI 兼容性问题，需要注意

## [ ] Task 5: 在 WSL2 中执行首次构建并调试问题
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 编写 `build-docker.sh` 构建脚本
  - 在 WSL2 环境中执行 `docker build`
  - 记录编译错误并逐一修复
  - 常见问题可能包括：
    - Python.h 找不到（PYTHON_INCLUDE 路径配置错误）
    - boost-python 与 Python 版本不匹配
    - protobuf 版本冲突
    - C++ 标准兼容性问题（旧代码用 C++03，新 gcc 默认 C++17）
    - numpy 头文件路径问题
    - Cython 版本与 Python 3.14 不兼容
  - 每次错误修复后重新构建
  - 直到 Caffe 编译成功且 `import caffe` 无错误
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: `docker build` 成功完成，无错误
  - `programmatic` TR-5.2: 容器内 `python -c "import caffe"` 无错误
  - `programmatic` TR-5.3: `caffe --version` 正常输出
- **Notes**: 这是最耗时的阶段，可能需要多次迭代；遇到无法解决的 Python 3.14 兼容性问题时，记录问题并评估是否需要降级到 Python 3.12/3.13

## [ ] Task 6: 优化为多阶段构建以减小镜像体积
- **Priority**: medium
- **Depends On**: Task 5
- **Description**: 
  - 将 Dockerfile 改为多阶段构建：
    - Stage 1 (builder): 安装编译工具链、编译 Caffe
    - Stage 2 (runtime): 仅安装运行时依赖，从 builder 复制编译产物
  - 清理 apt 缓存（`rm -rf /var/lib/apt/lists/*`）
  - 清理 conda/pip 缓存（`conda clean -afy`，`pip cache purge`）
  - 移除不需要的编译头文件和静态库（可选）
  - 对比优化前后的镜像大小
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-6.1: 多阶段构建 Dockerfile 可成功构建
  - `programmatic` TR-6.2: `import caffe` 和 `caffe --version` 仍正常工作
  - `programmatic` TR-6.3: 镜像大小比单阶段版本显著减小（至少减小 30%）
- **Notes**: 多阶段构建中需要注意复制所有必要的动态库（.so 文件），不能漏掉运行时依赖；可用 `ldd` 检查 caffe 二进制依赖

## [ ] Task 7: 创建非 root 用户和权限配置
- **Priority**: low
- **Depends On**: Task 6
- **Description**: 
  - 在 runtime 阶段创建 `caffe` 用户（UID/GID 可配置）
  - 设置 /workspace 目录权限
  - 确保 conda 环境对 caffe 用户可访问
  - 配置用户环境变量
- **Acceptance Criteria Addressed**: [AC-5, AC-9]
- **Test Requirements**:
  - `programmatic` TR-7.1: 容器默认以非 root 用户运行
  - `programmatic` TR-7.2: 挂载本地目录后文件可读写
- **Notes**: 如果非 root 用户导致权限问题复杂，可先以 root 运行，后续再添加

## [ ] Task 8: 编写运行和验证脚本
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 创建 `run-docker.sh`：快速启动容器并挂载当前目录
  - 创建 `verify.sh`（容器内执行）：验证 Caffe 功能的脚本
  - 创建 `export-image.sh`：导出镜像为 tar 文件的脚本
  - 所有脚本应有 shebang 和可执行权限
  - 脚本支持参数传入（如自定义镜像标签）
- **Acceptance Criteria Addressed**: [AC-4, AC-7, AC-9]
- **Test Requirements**:
  - `programmatic` TR-8.1: `run-docker.sh` 能启动容器进入 bash
  - `programmatic` TR-8.2: `export-image.sh` 能生成 tar 文件
  - `human-judgement` TR-8.3: 脚本有使用说明注释
- **Notes**: 参考之前 XMNN 项目的 docker/entrypoint-runtime.sh 和 deploy.sh 脚本

## [ ] Task 9: WSL2 端到端验证测试
- **Priority**: high
- **Depends On**: Task 7, Task 8
- **Description**: 
  - 执行完整的构建流程
  - 运行验证脚本确认所有功能正常：
    - Python 版本 3.14
    - import caffe 成功
    - caffe 命令行可用
    - 环境变量正确
    - 目录挂载可读写
  - 测试运行一个简单的 Caffe 示例（如 MNIST lenet 测试，可选）
  - 记录镜像大小
  - 导出镜像 tar 文件
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-4, AC-5, AC-7, AC-8, AC-9]
- **Test Requirements**:
  - `programmatic` TR-9.1: 所有验证脚本通过
  - `programmatic` TR-9.2: 镜像大小 ≤ 3GB
  - `programmatic` TR-9.3: docker save 导出的 tar 文件可被 docker load 导入
- **Notes**: MNIST 训练测试可选做，因为需要下载数据集，耗时较长；PyCaffe import 测试作为最低验收标准

## [ ] Task 10: 编写 Dockerfile 使用说明文档
- **Priority**: medium
- **Depends On**: Task 9
- **Description**: 
  - 在 `docker/conda-cpu/` 下创建 README.md
  - 包含：构建方法、运行方法、环境变量说明、目录挂载说明、常见问题排查
  - 记录 Python 3.14 兼容性问题和解决方案
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 文档内容完整，步骤清晰
  - `human-judgement` TR-10.2: 常见问题有记录
- **Notes**: 文档中明确说明这是 Python 3.14 版本，如果需要更稳定的环境建议用 Python 3.10/3.11
