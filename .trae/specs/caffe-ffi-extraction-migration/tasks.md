# Caffe-FFI 萃取迁移与Docker化 - 实施计划

## [x] Task 1: 复制项目文件到libs/caffe-ffi
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 使用xcopy/robocopy或cp命令将vendor/caffe/caffe-ffi的所有内容复制到libs/caffe-ffi/
  - 排除.git目录和__pycache__等临时文件
  - 验证所有核心文件已复制：CMakeLists.txt, pyproject.toml, include/, src/, python/, proto/, cmake/, tests/, examples/, docs/
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: libs/caffe-ffi/CMakeLists.txt存在
  - `programmatic` TR-1.2: libs/caffe-ffi/pyproject.toml存在
  - `programmatic` TR-1.3: libs/caffe-ffi/include/caffe_ffi/目录存在且包含.hpp文件
  - `programmatic` TR-1.4: libs/caffe-ffi/src/caffe_ffi/目录存在且包含.cpp/.cc文件
  - `programmatic` TR-1.5: libs/caffe-ffi/python/caffe_ffi/目录存在且包含.py文件
- **Notes**: 在Windows PowerShell中使用Copy-Item或robocopy执行复制

## [x] Task 2: 修改CMake构建系统（Dependencies.cmake路径独立化）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改cmake/Dependencies.cmake：将默认查找改为find_package(tvm_ffi CONFIG REQUIRED)
  - 添加CAFFE_FFI_TVM_FFI_DIR缓存选项作为开发模式覆盖
  - 保留自动检测：当选项未设置且检测到本地tvm-ffi源码目录时自动使用（从libs/caffe-ffi视角检测../tvm-ffi）
  - 更新注释说明开发模式和发布模式的区别
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: Dependencies.cmake包含find_package(tvm_ffi CONFIG REQUIRED)默认路径
  - `programmatic` TR-2.2: Dependencies.cmake包含CAFFE_FFI_TVM_FFI_DIR选项
  - `human-judgement` TR-2.3: 自动检测路径从vendor视角(../../tvm-ffi)更新为libs视角(../tvm-ffi)
- **Notes**: 参考npu-ffi的CMakeLists.txt中find_package的写法

## [x] Task 3: 添加CMakePresets.json
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 参考npu-ffi/CMakePresets.json创建caffe-ffi的预设配置
  - 包含release、debug、developer三个预设
  - 配置正确的build目录和CMake参数
- **Acceptance Criteria Addressed**: AC-1, AC-10
- **Test Requirements**:
  - `programmatic` TR-3.1: CMakePresets.json存在且为有效JSON
  - `human-judgement` TR-3.2: 预设配置与npu-ffi风格一致

## [x] Task 4: 创建scripts/开发脚本
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建scripts/dev.sh（Linux/WSL）：环境检查、conda激活、cmake配置、编译、安装
  - 创建scripts/dev.ps1（Windows）：环境检查、cmake配置、编译、安装
  - 创建scripts/check_ffi_prefix.py：参考npu-ffi检查FFI函数命名前缀
  - 创建scripts/verify_install.py：安装后验证脚本（import检查、版本检查、基础功能测试）
  - 创建scripts/gen_proto.py：protobuf文件生成脚本
- **Acceptance Criteria Addressed**: AC-1, AC-10
- **Test Requirements**:
  - `programmatic` TR-4.1: scripts/dev.sh存在且有可执行权限标记
  - `programmatic` TR-4.2: scripts/dev.ps1存在
  - `programmatic` TR-4.3: scripts/verify_install.py可运行（基本语法检查）
  - `human-judgement` TR-4.4: 脚本风格与npu-ffi参考一致

## [x] Task 5: 创建conda.recipe/打包配置
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 
  - 参考npu-ffi/conda.recipe/创建meta.yaml、build.sh、bld.bat
  - 配置正确的包名caffe-ffi、版本0.1.0、依赖项
  - 配置构建脚本（cmake + ninja + pip install）
- **Acceptance Criteria Addressed**: AC-1, AC-10
- **Test Requirements**:
  - `programmatic` TR-5.1: conda.recipe/meta.yaml存在
  - `programmatic` TR-5.2: conda.recipe/build.sh存在
  - `programmatic` TR-5.3: conda.recipe/bld.bat存在

## [x] Task 6: 更新pyproject.toml和environment.yml
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 更新pyproject.toml：添加sdist配置（include所有必要文件），完善项目信息（URL、classifiers）
  - 更新environment.yml：移除硬编码`-e ../../tvm-ffi`，改为注释说明开发模式如何editable安装tvm-ffi
  - 添加必要的可选依赖组
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: environment.yml中无硬编码的`-e ../../tvm-ffi`
  - `programmatic` TR-6.2: pyproject.toml包含[tool.scikit-build] sdist配置
  - `human-judgement` TR-6.3: 配置项与npu-ffi/pyproject.toml风格一致

## [x] Task 7: 创建基础配置文件（.gitignore, LICENSE, CHANGELOG.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 检查.gitignore是否存在，不存在则参考npu-ffi创建（排除build/, dist/, __pycache__, *.pyc, .pytest_cache等）
  - 检查LICENSE是否存在，不存在则创建BSD-2-Clause许可证（与pyproject.toml中声明一致）
  - 创建CHANGELOG.md初始版本记录
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-7.1: .gitignore存在
  - `programmatic` TR-7.2: LICENSE存在且包含BSD-2-Clause
  - `programmatic` TR-7.3: CHANGELOG.md存在

## [x] Task 8: 创建libs/caffe-ffi/README.md
- **Priority**: medium
- **Depends On**: Tasks 2-7
- **Description**: 
  - 编写README.md包含：项目简介、特性、系统要求（Python 3.14+、CMake、BLAS）、安装方式（pip install from source、conda环境）、快速开始示例、开发指南（WSL环境设置、编译命令、测试命令）、项目结构说明
  - 包含WSL环境下的完整操作步骤
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `human-judgement` TR-8.1: README包含安装步骤
  - `human-judgement` TR-8.2: README包含WSL环境说明
  - `human-judgement` TR-8.3: README包含测试运行命令

## [x] Task 8.1: 项目规范完善（AGENTS.md + .agents/ + .temp/ + .gitignore修复）
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 创建AGENTS.md：项目级智能体路由表，包含技术栈（C++17/Python 3.14+/CMake 3.26+）、目录结构、开发约定、代码规范、临时文件规则、CMake命名约束、关键项目记忆
  - 创建.agents/README.md：智能体规范目录入口
  - 创建.temp/目录及.gitkeep：临时文件统一存放位置
  - 修复.gitignore：移除过于宽泛的`*.cmake`规则（导致cmake/模块文件被忽略），改为精确路径忽略CMake生成文件；.temp/目录使用`.temp/*` + `!.temp/.gitkeep`例外规则
  - 将conda_build.sh/conda_build.bat从项目根目录移动到scripts/目录
  - 更新README.md：目录结构补充AGENTS.md/.agents/.temp，添加conda_build脚本使用说明，添加临时文件约定
- **Acceptance Criteria Addressed**: AC-1
- **Notes**: 补提交了cmake/目录下9个.cmake模块文件（之前被*.cmake规则错误忽略）

## [x] Task 9: 创建apps/caffe-ffi-jupyter目录结构和AGENTS.md
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成 (2026-03-29)
- **Description**: 
  - 创建apps/caffe-ffi-jupyter/目录
  - 创建AGENTS.md（遵循apps区域规范，嵌套优先，引用父级apps/AGENTS.md）
  - 创建目录结构：scripts/
  - 创建.dockerignore
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-9.1: apps/caffe-ffi-jupyter/AGENTS.md存在 ✅
  - `programmatic` TR-9.2: apps/caffe-ffi-jupyter/.dockerignore存在 ✅
  - `human-judgement` TR-9.3: AGENTS.md遵循apps规范（包含启动协议、路由表） ✅
- **Artifacts**:
  - apps/caffe-ffi-jupyter/AGENTS.md (7996 bytes)
  - apps/caffe-ffi-jupyter/scripts/ 目录
  - apps/caffe-ffi-jupyter/Dockerfile.dockerignore (1813 bytes)

## [x] Task 10: 创建Dockerfile
- **Priority**: high
- **Depends On**: Task 9, Task 1-8（需要libs/caffe-ffi源码）
- **Status**: ✅ 已完成 (2026-03-29)
- **Description**: 
  - 基于jupyter-ssh-base镜像创建Dockerfile（双阶段构建：builder + runtime）
  - 切换到root安装系统编译依赖：build-essential, cmake, ninja-build, libopenblas-dev, libprotobuf-dev, protobuf-compiler, wget
  - 安装Miniconda3到/opt/conda
  - 创建Python 3.14 conda环境（caffe-ffi）
  - 在conda环境中安装Python依赖：numpy>=2.3, protobuf>=7, scikit-build-core, pytest, apache-tvm-ffi, ipykernel
  - COPY projects/xuanspace/libs/caffe-ffi源码到/tmp/caffe-ffi
  - 在conda环境中pip install编译安装caffe-ffi
  - 注册conda环境为Jupyter内核：python -m ipykernel install --name caffe-ffi --display-name "Python 3.14 (caffe-ffi)"
  - 配置SSH登录时自动激活conda环境（/etc/profile.d/ + .bashrc双重配置）
  - Runtime阶段仅安装运行时依赖（libopenblas0, libprotobuf32t64），COPY builder阶段的conda环境
  - 清理编译缓存和apt缓存减小镜像体积
  - 不设置USER jupyteruser（由base image的entrypoint.sh处理用户切换）
- **Acceptance Criteria Addressed**: AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: Dockerfile存在 ✅
  - `human-judgement` TR-10.2: Dockerfile基于jupyter-ssh-base（FROM jupyter-ssh-base） ✅
  - `human-judgement` TR-10.3: Dockerfile安装Miniconda和Python 3.14环境 ✅
  - `human-judgement` TR-10.4: Dockerfile预装caffe-ffi ✅
  - `human-judgement` TR-10.5: Dockerfile注册Jupyter内核 ✅
  - `human-judgement` TR-10.6: Dockerfile保留jupyter-ssh-base的USER和ENTRYPOINT（未设USER jupyteruser，由entrypoint处理） ✅
- **Artifacts**:
  - apps/caffe-ffi-jupyter/Dockerfile (15387 bytes)

## [x] Task 11: 创建Docker构建脚本和docker-compose.yml
- **Priority**: medium
- **Depends On**: Task 10
- **Status**: ✅ 已完成 (2026-03-29)
- **Description**: 
  - 创建scripts/build.sh：一键构建脚本，支持APT_MIRROR/PIP_MIRROR/CONDA_MIRROR参数（国内镜像源--cn），构建上下文为SpecWeave根目录
  - 构建前检查jupyter-ssh-base基础镜像是否存在
  - 支持--verify参数构建后自动验证（SSH/Jupyter/caffe-ffi导入/kernel注册）
  - 创建docker-compose.yml：包含服务定义、端口映射(2222:22, 8888:8888)、环境变量、volume挂载、healthcheck
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-11.1: scripts/build.sh存在 ✅
  - `programmatic` TR-11.2: docker-compose.yml存在 ✅
  - `human-judgement` TR-11.3: build.sh使用正确的构建上下文（SpecWeave根目录） ✅
  - `human-judgement` TR-11.4: docker-compose.yml端口映射正确 ✅
- **Artifacts**:
  - apps/caffe-ffi-jupyter/scripts/build.sh (7737 bytes)
  - apps/caffe-ffi-jupyter/docker-compose.yml (928 bytes)

## [x] Task 12: 创建apps/caffe-ffi-jupyter/README.md
- **Priority**: medium
- **Depends On**: Tasks 10-11
- **Status**: ✅ 已完成 (2026-03-29)
- **Description**: 
  - 编写README.md包含：镜像简介、基于jupyter-ssh-base、功能特性（SSH+Jupyter+Python3.14+caffe-ffi）
  - 前置条件：WSL、Docker、先构建jupyter-ssh-base
  - 构建命令（包括国内镜像源选项--cn）
  - 运行命令（docker run和docker-compose两种方式）
  - SSH连接说明
  - Jupyter访问说明（URL和token）
  - caffe-ffi使用示例
  - 开发模式（volume挂载源码+editable安装）
  - 测试验证步骤
  - 常见问题FAQ
  - 镜像架构图
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `human-judgement` TR-12.1: README包含构建命令 ✅
  - `human-judgement` TR-12.2: README包含运行命令 ✅
  - `human-judgement` TR-12.3: README包含SSH和Jupyter访问说明 ✅
  - `human-judgement` TR-12.4: README包含开发模式volume挂载说明 ✅
  - `human-judgement` TR-12.5: README包含测试验证步骤 ✅
- **Artifacts**:
  - apps/caffe-ffi-jupyter/README.md (6938 bytes)

## [x] Task 13: 静态验证（文件结构检查）
- **Priority**: high
- **Depends On**: Tasks 1-12
- **Status**: ✅ 已完成 (2026-03-29)
- **Description**: 
  - 验证libs/caffe-ffi所有预期文件存在（AC-1检查清单）
  - 验证apps/caffe-ffi-jupyter所有预期文件存在
  - 验证Dockerfile指令合法性（基本语法检查）
  - 验证docker-compose.yml配置正确
  - 验证AGENTS.md符合apps规范
  - 验证build.sh包含必要参数
  - 7大类共38项检查全部通过
- **Acceptance Criteria Addressed**: AC-1, AC-10
- **Test Requirements**:
  - `programmatic` TR-13.1: libs/caffe-ffi所有AC-1清单文件存在 ✅
  - `programmatic` TR-13.2: Python脚本py_compile通过 ✅（前次会话已验证）
  - `programmatic` TR-13.3: apps/caffe-ffi-jupyter所有6个核心文件存在且内容正确 ✅
- **Notes**: 此任务在Windows环境执行静态检查；动态编译/测试在Task 14（WSL验证）中执行

## [ ] Task 14: WSL环境动态验证（需用户在WSL中执行）
- **Priority**: high
- **Depends On**: Task 13
- **Description**: 
  - 生成WSL验证脚本或命令清单
  - 预期验证步骤：
    1. 在WSL中进入xuanspace目录
    2. 构建jupyter-ssh-base基础镜像（如未构建）
    3. 构建caffe-ffi-jupyter镜像
    4. 运行容器
    5. 验证SSH连接
    6. 验证Jupyter访问
    7. 验证import caffe_ffi
    8. 运行pytest
  - 由于当前Windows环境无法直接执行WSL命令，本任务为生成验证脚本和文档化步骤
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-14.1: 生成WSL验证脚本scripts/wsl-verify.sh或在README中列出完整命令序列
  - `human-judgement` TR-14.2: 验证步骤覆盖所有programmatic AC
- **Notes**: 实际WSL执行和测试通过由用户在WSL环境中完成，本任务负责生成可执行的验证命令/脚本
