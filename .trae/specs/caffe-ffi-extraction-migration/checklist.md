# Caffe-FFI 萃取迁移与Docker化 - 验证检查清单

## 项目文件结构验证
- [x] libs/caffe-ffi/CMakeLists.txt存在
- [x] libs/caffe-ffi/pyproject.toml存在
- [x] libs/caffe-ffi/environment.yml存在
- [x] libs/caffe-ffi/AGENTS.md存在（项目级智能体路由表）
- [x] libs/caffe-ffi/.agents/目录存在（智能体规范容器）
- [x] libs/caffe-ffi/.temp/目录存在且包含.gitkeep
- [x] libs/caffe-ffi/include/caffe_ffi/目录存在且包含.hpp头文件
- [x] libs/caffe-ffi/src/caffe_ffi/目录存在且包含.cpp/.cc源文件
- [x] libs/caffe-ffi/src/caffe_ffi/layers/目录存在且包含层实现
- [x] libs/caffe-ffi/python/caffe_ffi/目录存在且包含.py文件
- [x] libs/caffe-ffi/proto/caffe/proto/caffe.proto存在
- [x] libs/caffe-ffi/cmake/目录包含9个.cmake模块文件（Options/Dependencies/CompilerConfig/ProtoCompile/TargetBuild/WindowsDllCopy/Tests/Install/DetectBLAS）+ README.md
- [x] libs/caffe-ffi/tests/cpp/存在且包含C++测试
- [x] libs/caffe-ffi/tests/python/存在且包含Python测试
- [x] libs/caffe-ffi/examples/存在且包含示例
- [x] libs/caffe-ffi/docs/存在且包含文档
- [x] libs/caffe-ffi/scripts/目录存在
- [x] libs/caffe-ffi/conda.recipe/目录存在

## 项目规范验证
- [x] AGENTS.md包含技术栈、目录结构、开发约定、代码规范
- [x] .agents/README.md存在
- [x] .temp/.gitkeep存在，.temp/*内容被.gitignore忽略
- [x] .gitignore无过于宽泛的*.cmake规则（不忽略cmake/模块文件）
- [x] .gitignore使用精确路径忽略CMake生成文件（/CMakeCache.txt, /CMakeFiles/等）
- [x] conda_build.sh/conda_build.bat已移至scripts/目录

## CMake构建系统验证
- [x] cmake/Dependencies.cmake默认使用find_package(tvm_ffi CONFIG REQUIRED)
- [x] cmake/Dependencies.cmake包含CAFFE_FFI_TVM_FFI_DIR选项
- [x] cmake/Dependencies.cmake自动检测路径从../../tvm-ffi更新为../tvm-ffi（libs视角）
- [x] 顶层CMakeLists.txt保持精简模块化include结构
- [x] CMakePresets.json存在且包含release/debug/developer预设

## 标准配置文件验证
- [x] scripts/dev.sh存在（Linux/WSL开发脚本）
- [x] scripts/dev.ps1存在（Windows开发脚本）
- [x] scripts/conda_build.sh存在（Linux/WSL Conda环境一键构建）
- [x] scripts/conda_build.bat存在（Windows Conda环境一键构建）
- [x] scripts/check_ffi_prefix.py存在
- [x] scripts/verify_install.py存在
- [x] scripts/gen_proto.py存在
- [x] conda.recipe/meta.yaml存在
- [x] conda.recipe/build.sh存在
- [x] conda.recipe/bld.bat存在
- [x] environment.yml无硬编码-e ../../tvm-ffi路径
- [x] pyproject.toml包含sdist include配置
- [x] .gitignore存在且正确（无过于宽泛规则，.temp/正确忽略）
- [x] LICENSE存在且为BSD-2-Clause
- [x] CHANGELOG.md存在

## Docker应用验证
- [x] apps/caffe-ffi-jupyter/目录存在
- [x] apps/caffe-ffi-jupyter/AGENTS.md存在且遵循apps规范
- [x] apps/caffe-ffi-jupyter/Dockerfile存在
- [x] apps/caffe-ffi-jupyter/.dockerignore存在（Dockerfile.dockerignore，BuildKit专用）
- [x] apps/caffe-ffi-jupyter/scripts/build.sh存在
- [x] apps/caffe-ffi-jupyter/docker-compose.yml存在
- [x] apps/caffe-ffi-jupyter/README.md存在

## Dockerfile内容验证
- [x] Dockerfile FROM jupyter-ssh-base（双阶段构建：builder + runtime）
- [x] Dockerfile安装build-essential, wget, bzip2, ca-certificates, git（编译基础工具+conda安装前置）
- [x] Dockerfile通过conda-forge安装cmake>=3.26, ninja>=1.13, libprotobuf>=7.0.0, protobuf>=7.0.0, libopenblas, numpy（避免apt源protobuf版本过旧）
- [x] Dockerfile安装Miniconda3到/opt/conda
- [x] Dockerfile创建Python 3.14 conda环境（名为caffe-ffi，路径/opt/conda/envs/caffe-ffi/）
- [x] Dockerfile在conda环境中安装numpy, protobuf, scikit-build-core, pytest, apache-tvm-ffi, ipykernel
- [x] Dockerfile COPY projects/xuanspace/libs/caffe-ffi源码（构建上下文为SpecWeave根目录）
- [x] Dockerfile使用 `pip install --no-build-isolation` 编译安装caffe-ffi（防止pip构建隔离导致运行时链接tvm-ffi失败）
- [x] Dockerfile通过SKBUILD_CMAKE_ARGS启用RPATH（CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON, CMAKE_BUILD_RPATH_USE_ORIGIN=ON）
- [x] Dockerfile builder阶段使用ldd验证_caffe_ffi.so共享库依赖
- [x] Dockerfile设置ENV LD_LIBRARY_PATH包含conda环境lib目录
- [x] Dockerfile runtime阶段动态配置/etc/ld.so.conf.d/caffe-ffi.conf注册tvm_ffi和caffe_ffi的site-packages路径并执行ldconfig
- [x] Dockerfile在runtime阶段（非builder）注册Jupyter内核到/usr/local/share/jupyter/kernels/（--prefix=/usr/local），确保/opt/venv中的Jupyter可发现
- [x] Dockerfile runtime阶段仅安装libgomp1（OpenMP运行时），protobuf/openblas/BLAS通过conda环境提供（从builder COPY完整conda环境）
- [x] Dockerfile runtime阶段使用ldd验证_caffe_ffi.so运行时共享库解析
- [x] Dockerfile配置SSH登录自动激活conda环境（/etc/profile.d/conda-caffe-ffi.sh + .bashrc双重配置 + LD_LIBRARY_PATH导出）
- [x] Dockerfile清理apt缓存和临时文件（apt-get clean + /var/lib/apt/lists/* 删除）
- [x] Dockerfile未显式设置USER jupyteruser（由jupyter-ssh-base的entrypoint.sh处理用户切换，保持一致性）

## 文档验证
- [x] libs/caffe-ffi/README.md包含安装步骤
- [x] libs/caffe-ffi/README.md包含WSL环境说明
- [x] libs/caffe-ffi/README.md包含测试运行命令
- [x] libs/caffe-ffi/README.md包含conda_build脚本使用说明
- [x] libs/caffe-ffi/README.md包含.temp/临时文件约定说明
- [x] libs/caffe-ffi/README.md项目结构包含AGENTS.md/.agents/.temp/
- [x] apps/caffe-ffi-jupyter/README.md包含构建命令（bash scripts/build.sh [--cn]）
- [x] apps/caffe-ffi-jupyter/README.md包含运行命令（docker run和docker-compose两种方式）
- [x] apps/caffe-ffi-jupyter/README.md包含SSH连接说明（ssh -p 2222 jupyteruser@localhost）
- [x] apps/caffe-ffi-jupyter/README.md包含Jupyter访问说明（http://localhost:8888/?token=...）
- [x] apps/caffe-ffi-jupyter/README.md包含开发模式volume挂载说明（-v挂载源码 + pip install -e .）
- [x] apps/caffe-ffi-jupyter/README.md包含测试验证步骤
- [x] apps/caffe-ffi-jupyter/README.md包含完整验证命令序列（见README"测试验证步骤"章节）

## 风格一致性验证（human-judgment）
- [x] libs/caffe-ffi顶层目录结构与npu-ffi一致（include/src/python/proto/cmake/tests/examples/scripts/docs/conda.recipe）
- [x] 开发脚本风格与npu-ffi参考一致
- [x] CMakePresets.json配置与npu-ffi风格一致
- [x] conda.recipe配置与npu-ffi风格一致
- [x] pyproject.toml配置风格与npu-ffi一致
- [x] apps/caffe-ffi-jupyter/AGENTS.md遵循apps/AGENTS.md规范（嵌套优先、路由表、启动协议）
- [x] apps/AGENTS.md路由表已更新包含caffe-ffi-jupyter条目

## 构建脚本验证
- [x] scripts/build.sh包含WSL/Linux环境检测警告
- [x] scripts/build.sh包含--verify参数，验证SSH/Jupyter服务状态、caffe_ffi导入、_caffe_ffi.so共享库ldd解析、Jupyter kernelspec、numpy/protobuf导入

## 静态语法验证（programmatic）
- [x] 所有Python文件py_compile通过（无语法错误）
- [x] Dockerfile基本语法检查通过（FROM/RUN/COPY/CMD等指令合法）
- [x] JSON文件（CMakePresets.json）语法有效
- [x] YAML文件（environment.yml, docker-compose.yml）语法有效
- [x] vendor/caffe/caffe-ffi原始文件未被修改或删除
