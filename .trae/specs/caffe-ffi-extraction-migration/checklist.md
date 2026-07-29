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
- [ ] apps/caffe-ffi-jupyter/目录存在
- [ ] apps/caffe-ffi-jupyter/AGENTS.md存在且遵循apps规范
- [ ] apps/caffe-ffi-jupyter/Dockerfile存在
- [ ] apps/caffe-ffi-jupyter/.dockerignore存在
- [ ] apps/caffe-ffi-jupyter/scripts/build.sh存在
- [ ] apps/caffe-ffi-jupyter/docker-compose.yml存在
- [ ] apps/caffe-ffi-jupyter/README.md存在

## Dockerfile内容验证
- [ ] Dockerfile FROM jupyter-ssh-base
- [ ] Dockerfile安装build-essential, cmake, ninja-build, libopenblas-dev, libprotobuf-dev, protobuf-compiler
- [ ] Dockerfile安装Miniconda3到/opt/conda
- [ ] Dockerfile创建Python 3.14 conda环境（名为caffe-ffi或base）
- [ ] Dockerfile在conda环境中安装numpy, protobuf, scikit-build-core, pytest, apache-tvm-ffi, ipykernel
- [ ] Dockerfile COPY libs/caffe-ffi源码
- [ ] Dockerfile在conda环境中pip install caffe-ffi
- [ ] Dockerfile注册Jupyter内核（"Python 3.14 (caffe-ffi)"）
- [ ] Dockerfile配置SSH登录自动激活conda环境（.bashrc）
- [ ] Dockerfile清理apt缓存和临时文件
- [ ] Dockerfile最终USER为jupyteruser（继承jupyter-ssh-base）

## 文档验证
- [x] libs/caffe-ffi/README.md包含安装步骤
- [x] libs/caffe-ffi/README.md包含WSL环境说明
- [x] libs/caffe-ffi/README.md包含测试运行命令
- [x] libs/caffe-ffi/README.md包含conda_build脚本使用说明
- [x] libs/caffe-ffi/README.md包含.temp/临时文件约定说明
- [x] libs/caffe-ffi/README.md项目结构包含AGENTS.md/.agents/.temp/
- [ ] apps/caffe-ffi-jupyter/README.md包含构建命令
- [ ] apps/caffe-ffi-jupyter/README.md包含运行命令（docker run和docker-compose）
- [ ] apps/caffe-ffi-jupyter/README.md包含SSH连接说明
- [ ] apps/caffe-ffi-jupyter/README.md包含Jupyter访问说明
- [ ] apps/caffe-ffi-jupyter/README.md包含开发模式volume挂载说明
- [ ] apps/caffe-ffi-jupyter/README.md包含测试验证步骤
- [ ] README包含WSL验证完整命令序列（或提供wsl-verify.sh脚本）

## 风格一致性验证（human-judgment）
- [ ] libs/caffe-ffi顶层目录结构与npu-ffi一致（include/src/python/proto/cmake/tests/examples/scripts/docs/conda.recipe）
- [ ] 开发脚本风格与npu-ffi参考一致
- [ ] CMakePresets.json配置与npu-ffi风格一致
- [ ] conda.recipe配置与npu-ffi风格一致
- [ ] pyproject.toml配置风格与npu-ffi一致
- [ ] apps/caffe-ffi-jupyter/AGENTS.md遵循apps/AGENTS.md规范（嵌套优先、路由表、启动协议）

## 静态语法验证（programmatic）
- [ ] 所有Python文件py_compile通过（无语法错误）
- [ ] Dockerfile基本语法检查通过（FROM/RUN/COPY/CMD等指令合法）
- [ ] JSON文件（CMakePresets.json）语法有效
- [ ] YAML文件（environment.yml, docker-compose.yml）语法有效
- [ ] vendor/caffe/caffe-ffi原始文件未被修改或删除
