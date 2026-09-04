# XMNN Nuitka + scikit-build-core 打包系统 - 实施计划

## [ ] Task 1: 修复 xmpack 工具库已知 Bug
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修复 `src/xmpack/docker.py` 中 `compile_nuitka()` 函数缺失 `cache_dir` 参数的 bug，在函数签名中添加 `cache_dir: str = "/workspace/.temp/.nuitka_cache"` 参数
  - 修复 `build_nuitka()` 调用 `compile_nuitka()` 时缺失 `cache_dir` 参数传递
  - 审查 `nuitka_compiler.py` 中 `build_xmnn_package_script()` 的 `src_dir` 参数：当前 XMNN 源码在 `npuusertools/xmnn/`（含 xmnn 包子目录），但 cd_subdir 为空且 cd 到 src_dir 后直接执行 `python -m nuitka --module xmnn`，需确认 PYTHONPATH 包含父目录使得 `import xmnn` 可解析
  - 审查 `nuitka_compiler.py` 中 TVM 的 `include_packages` 列表是否完整（tvm.relax, tvm.dlight, tvm.script 等子包是否在 tvm python 目录中存在）
  - 检查 `build_vta_package_script()` 的 `nofollow_imports` 是否需要排除更多 VTA 外部依赖
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: `compile_nuitka()` 函数可被无参数调用，不抛 NameError/TypeError
  - `programmatic` TR-1.2: `build_nuitka()` 函数签名完整，调用 `compile_nuitka()` 时传递所有必需参数
  - `programmatic` TR-1.3: Python 对 xmpack 模块做 `compileall.compile_dir()` 无语法错误
  - `human-judgement` TR-1.4: 审查所有 Nuitka include/exclude 列表，对照实际 tvm/vta/xmnn 目录结构确认模块清单完整
- **Notes**: 先用 Python -c "from xmpack import ..." 验证导入无错误

## [ ] Task 2: 确认源码布局与路径配置
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 确认 `npuusertools/xmnn/` 目录下的 Python 源码是否完整（包含 `__init__.py`、`compile_api.py`、`adaround/` 子包等所有模块）
  - 确认 TVM C++ 构建产物目录：检查 `npu_tvm/build_llvm22/` 是否存在，如不存在则确认是 `npu_tvm/build/` 还是需要通过 CMake preset 创建
  - 确认 Python 版本一致性：Containerfile.build 使用的 conda 环境 Python 版本、packaging/pyproject.toml 的 requires-python、Nuitka 编译产物的 cpython ABI tag 三者需一致
  - 确认 VTA Python 源码位置（npu_tvm/vta/python/vta/）
  - 验证 TVM Python 包结构（npu_tvm/python/tvm/ 下是否包含 relay/topi/auto_scheduler/meta_schedule 等子包）
  - 如发现路径不一致，更新 nuitka_compiler.py 和 docker.py 中的默认路径
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: npuusertools/xmnn/__init__.py 存在且可被 Python 解析
  - `programmatic` TR-2.2: npu_tvm/python/tvm/ 目录存在，包含 relay/, topi/, ir/, tir/, runtime/ 等关键子目录
  - `programmatic` TR-2.3: npu_tvm/vta/python/vta/ 目录存在
  - `programmatic` TR-2.4: xmnn 包的动态导入模块（compile_api, infer_api, accuracy_api 等）对应的 .py 文件均存在
  - `human-judgement` TR-2.5: 确认 TVM C++ 构建产物目录名称，记录到配置中

## [ ] Task 3: 配置 scikit-build-core 使用 Ninja 生成器
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 更新 `packaging/pyproject.toml` 的 `[tool.scikit-build]` 部分，添加 `cmake.args = ["-G", "Ninja"]` 指定使用 Ninja 生成器
  - 确认 Containerfile.build 中已安装 ninja（检查是否在 pip 或 apt 安装列表中）
  - 在顶层 CMakeLists.txt 中添加 `LANGUAGES NONE` 已正确设置（已有），确保不触发 C/C++ 编译器检查（因为本阶段不编译 C++，只做 install）
  - 验证子目录 tvm/ 和 vta/ 的 CMakeLists.txt 也使用 `LANGUAGES NONE`
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: pyproject.toml 中 cmake.args 包含 "-G" "Ninja"
  - `programmatic` TR-3.2: Containerfile.build 中安装了 ninja（apt 或 pip）
  - `programmatic` TR-3.3: 在容器内执行 `ninja --version` 成功输出版本号

## [ ] Task 4: 完善 packaging/CMakeLists.txt 安装规则
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 审查顶层 CMakeLists.txt，确保 xmnn 数据目录（autolibs/fonts/tools_cpp）的安装路径正确
  - 确认 tools_cpp/bin/ 和 tools_cpp/libs/ 下的二进制文件和库的安装权限（USE_SOURCE_PERMISSIONS 已有）
  - 审查 tvm/CMakeLists.txt 中 TVM 原生库的 glob 模式：确认 libtvm.so、libtvm_runtime.so、libvta.so 的文件名模式是否与实际 CMake 构建产物匹配（可能包含版本后缀如 libtvm.so.0.19.0）
  - 确认 vta/CMakeLists.txt 中 vta_hw/config 目录的来源路径正确
  - 添加对 .pyi stub 文件的安装规则（Nuitka 自动生成的类型提示文件）
  - 检查是否需要安装 TVM Python 包中的非 .so 数据文件（如 relay/std/prelude.rly 等）—— Nuitka 编译后这些数据文件是否被打包到 .so 中？需要验证；如果没有，需要额外安装规则
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `human-judgement` TR-4.1: 审查 CMakeLists.txt install 规则覆盖所有必需文件类型
  - `programmatic` TR-4.2: CMakeLists.txt 语法正确（cmake -P 检查无语法错误）

## [ ] Task 5: 修复 Containerfile.build 构建镜像
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 检查 Containerfile.build 中基础镜像 `localhost/miniconda3:llvm22` 是否可用，如不可用则需提供构建该基础镜像的说明或 Dockerfile
  - 确认 Containerfile.build 中安装了 ninja（apt 或 pip）
  - 确认 pip 安装包含 wheel 包（用于 wheel unpack 验证）
  - 确认 conda 环境名为 tvm-build，Python 版本为 3.13 或 3.14
  - 确认 LLVM 安装和 LLVM_CONFIG 路径正确
  - 如需支持 Python 3.14，更新相关路径和包版本
- **Acceptance Criteria Addressed**: AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: Containerfile.build 可成功构建为 Docker 镜像
  - `programmatic` TR-5.2: 构建镜像内 python --version 输出符合预期
  - `programmatic` TR-5.3: 构建镜像内 nuitka --version 成功
  - `programmatic` TR-5.4: 构建镜像内 cmake --version 和 ninja --version 成功

## [ ] Task 6: 端到端 Nuitka 编译验证（容器内）
- **Priority**: high
- **Depends On**: Task 2, Task 5
- **Description**:
  - 在构建容器内先完成 TVM C++ 编译（inv build 或手动 cmake + ninja）
  - 执行 Nuitka 编译阶段，依次编译 tvm → vta → xmnn
  - 验证每个组件的 .so 文件正确生成
  - 对每个 .so 做基础导入测试（cd /tmp && PYTHONPATH=. python -c "import tvm"）
  - 修复 Nuitka 编译中遇到的问题（缺失模块、动态导入失败、链接错误等）
  - 特别关注：tvm 的动态注册机制、xmnn 的 importlib.import_module 动态加载 _api 模块
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-6.1: tvm.cpython-*.so 生成且 > 10MB
  - `programmatic` TR-6.2: vta.cpython-*.so 生成且可 import
  - `programmatic` TR-6.3: xmnn.cpython-*.so 生成且可 import（包括动态导入的 compile_api 等）
  - `programmatic` TR-6.4: 从 /tmp 目录导入 tvm 可正常找到 libtvm.so（LD_LIBRARY_PATH 或 TVM_LIBRARY_PATH 正确设置）

## [ ] Task 7: 端到端 wheel 打包验证
- **Priority**: high
- **Depends On**: Task 4, Task 6
- **Description**:
  - 在 Nuitka 编译产物就绪后，执行 wheel 打包（pip wheel / scikit-build-core）
  - 验证 wheel 文件生成，文件名符合 PEP 427 规范
  - 解包 wheel 检查内容：.so 文件、原生库、数据目录、bootstrap 文件
  - 修复打包中遇到的问题（路径错误、缺少文件、CMAKE_ARGS 传递等）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: wheel 文件生成在 packaging/dist/ 下
  - `programmatic` TR-7.2: wheel 文件名匹配 xmnn-*.whl 模式
  - `programmatic` TR-7.3: wheel 解包后包含 tvm.cpython-*.so, vta.cpython-*.so, xmnn.cpython-*.so
  - `programmatic` TR-7.4: wheel 解包后包含 tvm/_libs/libtvm*.so
  - `programmatic` TR-7.5: wheel 解包后包含 _tvm_nuitka_init.py 和 tvm_nuitka_init.pth
  - `programmatic` TR-7.6: wheel 解包后包含 xmnn/autolibs/, xmnn/fonts/, xmnn/tools_cpp/
  - `programmatic` TR-7.7: wheel 解包后不包含任何 tvm/vta/xmnn 的 .py 源码文件（bootstrap 除外）

## [ ] Task 8: wheel 安装与导入测试
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 在干净的 Python 环境（或新的 Docker 容器）中 pip install 生成的 wheel
  - 验证 tvm 导入和版本号
  - 验证 vta 导入
  - 验证 xmnn 导入和所有动态加载的 API 模块（compile_api, infer_api, accuracy_api, performance_api, bandwidth_api, autotune_api, excel_report_api）
  - 验证 TVM 基础功能（tvm.relay, tvm.topi 导入）
  - 验证 xmnn 数据文件路径（autolibs, fonts, tools_cpp 可被找到）
  - 验证 libtvm.so 可被正确加载（无需手动设置 LD_LIBRARY_PATH）
  - 修复安装/导入中发现的问题
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: pip install 退出码为 0
  - `programmatic` TR-8.2: `import tvm; print(tvm.__version__)` 成功
  - `programmatic` TR-8.3: `import vta` 成功
  - `programmatic` TR-8.4: `import xmnn; from xmnn import compile_api, infer_api, accuracy_api` 成功
  - `programmatic` TR-8.5: `from tvm import relay, topi, autotvm` 成功
  - `programmatic` TR-8.6: site-packages 中无 tvm/vta/xmnn 的 .py 源码（_tvm_nuitka_init.py 除外）

## [ ] Task 9: inv 命令行任务验证与修复
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 验证 `inv image-build` 可成功构建 nuitka-gcc-llvm 镜像
  - 验证 `inv build` 可在容器内完成 TVM C++ 编译
  - 验证 `inv nuitka-compile` 可在容器内完成 Nuitka 编译
  - 验证 `inv nuitka-package` 可在容器内完成 wheel 打包
  - 验证 `inv nuitka` 一键流水线端到端成功
  - 修复任务执行中发现的路径错误、参数传递问题
  - 确保 tasks.py 中的路径在 WSL2/Docker 环境下正确解析
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: `inv image-build` 退出码为 0
  - `programmatic` TR-9.2: `inv nuitka` 一键流水线退出码为 0
  - `programmatic` TR-9.3: `inv nuitka` 执行后 packaging/dist/ 下存在 wheel 文件

## [ ] Task 10: 客户端镜像构建与验证
- **Priority**: medium
- **Depends On**: Task 8, Task 9
- **Description**:
  - 确认 client/Containerfile 与新 wheel 包兼容（wheel 安装路径、Python 版本、conda 环境名等）
  - 修复 client/Containerfile 中可能存在的路径或版本不匹配问题
  - 将 wheel 复制到 client/.temp/ 目录
  - 执行 `inv client` 构建客户端运行时镜像
  - 运行客户端镜像验证 tvm/vta/xmnn 导入
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: `inv client` 退出码为 0，镜像构建成功
  - `programmatic` TR-10.2: `docker run --rm xmnn-client:1.2.1 python -c "import tvm; import vta; import xmnn"` 退出码为 0

## [ ] Task 11: 统一 docker-runtime 与 xmpack 打包方案
- **Priority**: low
- **Depends On**: Task 10
- **Description**:
  - 评估 npuusertools/docker-runtime/Dockerfile（.pyc 字节码方案）与 xmpack client 镜像（Nuitka .so wheel 方案）的关系
  - 更新 docker-runtime/Dockerfile 使其基于 Nuitka 编译的 wheel 安装，或标记为旧方案并指向新的 client 镜像
  - 确保两套方案文档清晰，避免混淆
- **Acceptance Criteria Addressed**: AC-8, FR-11
- **Test Requirements**:
  - `human-judgement` TR-11.1: 审查两个 Docker 方案的关系，决定统一策略
  - `programmatic` TR-11.2: 最终运行时镜像内所有依赖正确（numpy/scipy/psutil/pytest）

## [ ] Task 12: 文档更新与使用说明
- **Priority**: low
- **Depends On**: Task 10
- **Description**:
  - 更新或创建 README.md 说明构建流程：前置条件、构建命令、产物位置
  - 记录 inv 命令的使用方法
  - 记录常见问题排查（Nuitka 编译失败、wheel 安装后导入失败等）
- **Acceptance Criteria Addressed**: NFR-4
- **Test Requirements**:
  - `human-judgement` TR-12.1: README 包含完整的构建步骤说明
  - `human-judgement` TR-12.2: README 包含常见问题和故障排查指南
