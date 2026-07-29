# XMNN Nuitka Wheel 包构建系统 - 验证检查清单（v2，基于 scikit-build-core + CMake）

## 构建环境检查（需在 Linux/WSL 中执行）
- [ ] Linux/WSL 环境，GCC/G++ 可用
- [ ] CMake ≥ 3.18 已安装
- [ ] Ninja 已安装
- [ ] Python 3.8+ 开发头文件可用
- [ ] Nuitka 已安装（pip install nuitka）
- [ ] scikit-build-core 已安装（pip install scikit-build-core）
- [ ] build 已安装（pip install build）
- [ ] invoke 已安装（pip install invoke）
- [ ] numpy 等 TVM 运行时依赖已安装

## Task 1 验证：pyproject.toml 配置（已完成 ✓）
- [x] pyproject.toml 使用 scikit_build_core.build 作为 build-backend
- [x] 无 setuptools 依赖声明
- [x] [project] 节包含 name、version、dependencies
- [x] [tool.scikit-build] 节配置 cmake/ninja 版本、build-type、wheel.install-dir
- [x] [build-system] requires 包含 scikit-build-core、cmake、ninja、nuitka
- [x] 目录下无 setup.py 文件
- [x] 目录下无 MANIFEST.in 文件
- [x] TOML 语法验证通过

## Task 2 验证：CMakeLists.txt（已完成 ✓）
- [x] cmake_minimum_required(VERSION 3.18...3.27) 版本声明正确
- [x] project(xmnn LANGUAGES NONE) 使用 LANGUAGES NONE
- [x] find_package(Python3 COMPONENTS Interpreter REQUIRED) 正确
- [x] 定义了 XMN_ROOT、NUITKA_OUTPUT_DIR、TVM_BUILD_DIR 路径变量（TVM_ROOT 通过外部传入）
- [x] install(DIRECTORY) 规则安装 xmnn 源码（PATTERN 排除 __pycache__ 和 build）
- [x] install(FILES) 规则安装 tvm.so/tvm.pyi、vta.so/vta.pyi
- [x] install(DIRECTORY) 规则安装 tvm.data/、vta.data/ 数据目录
- [x] install(FILES) 规则安装 libtvm.so、libtvm_runtime.so 到 tvm/ 目录
- [x] install(FILES) 规则安装引导 __init__.py（通过 file(GENERATE) 动态生成）
- [x] 相对路径自动转换为绝对路径（基于 PROJECT_SOURCE_DIR）
- [ ] `cmake -S . -B build/cmake-test` 配置无错误（需 Linux 环境）

## Task 3 验证：invoke tasks.py 环境管理（已完成 ✓）
- [x] inv --list 列出所有任务（init、check-deps、clean、build-tvm、nuitka-tvm、nuitka-vta、build-wheel、build-all、verify）
- [x] inv check-deps 正确显示工具可用性和路径
- [x] inv init 创建 build/、build/nuitka/、dist/ 目录
- [x] inv clean 删除 build/ 和 dist/
- [x] inv build-tvm 切换到 npu_tvm 执行 inv config -f 和 inv make
- [x] build-tvm 完成后列出构建的 .so 文件和大小
- [x] Python 语法验证通过

## Task 4 验证：Nuitka 编译 tvm（代码完成 ✓，需 Linux 运行时验证）
- [x] inv nuitka-tvm 命令包含 --module 标志
- [x] --include-data-dir 参数指向 relay/std 目录
- [x] PYTHONPATH 包含 npu_tvm/python
- [x] 输出目录为 build/nuitka/
- [x] 输出文件名为 tvm.so
- [x] 编译后验证 tvm.so 存在（前置检查）
- [x] 编译后验证 tvm.data/relay/std/ 包含 .rly 文件
- [x] 添加了 --nofollow-import-to=tvm 避免重复编译
- [ ] inv nuitka-tvm 编译成功无错误（需 Linux 环境）
- [ ] tvm.so、tvm.pyi、tvm.data/relay/std/*.rly 产物存在（需 Linux 环境）

## Task 5 验证：Nuitka 编译 vta（代码完成 ✓，需 Linux 运行时验证）
- [x] inv nuitka-vta 命令包含 --module 标志
- [x] --include-data-dir 参数指向 vta_hw/config 目录
- [x] PYTHONPATH 包含 npu_tvm/vta/python 和 npu_tvm/python
- [x] 输出文件名为 vta.so
- [x] --nofollow-import-to=tvm,vta 避免重复编译
- [x] 编译后验证 vta.so、vta.pyi、vta.data/ 存在（前置检查）
- [ ] inv nuitka-vta 编译成功无错误（需 Linux 环境）
- [ ] vta.so、vta.pyi、vta.data/vta_hw/config/*.json 产物存在（需 Linux 环境）

## Task 6 验证：路径适配引导（已完成 ✓）
- [x] tvm/__init__.py 引导文件设置 TVM_LIBRARY_PATH 指向包目录
- [x] vta/__init__.py 引导文件设置路径并从 vta.so 导入
- [x] 引导文件在导入 .so 前通过 ctypes.CDLL 预加载 C++ 原生库（RTLD_GLOBAL）
- [x] 数据文件路径基于 __file__（引导 __init__.py 的路径）计算，适配 Nuitka 编译后路径
- [x] 引导文件通过 CMake file(GENERATE) 在配置阶段生成，使用 [=[ ]=] 长括号避免转义
- [x] xmnn/__init__.py 添加了 tvm/vta 包路径引导逻辑

## Task 7 验证：wheel 构建（代码完成 ✓，需 Linux 运行时验证）
- [x] inv build-wheel 检查前置产物（tvm.so、vta.so、libtvm*.so），缺失时给出明确错误提示
- [x] 通过 CMake 变量（NUITKA_OUTPUT_DIR、TVM_BUILD_DIR）传入预编译产物路径
- [x] 执行 python -m build --wheel --outdir=dist --no-isolation 生成 whl
- [x] inv build-all 串联完整构建流程（clean → build-tvm → nuitka-tvm → nuitka-vta → build-wheel）
- [ ] dist/ 目录生成 .whl 文件（需 Linux 环境）
- [ ] whl 文件名符合 PEP 427 规范（需 Linux 环境）

## Task 8 验证：CMake install 目录结构（代码完成 ✓，需 Linux 运行时验证）
- [x] install 规则覆盖 tvm/、vta/、xmnn/ 三个包
- [x] install 规则包含 tvm.so、vta.so、.pyi 文件
- [x] install 规则包含 tvm.data/、vta.data/ 数据目录
- [x] install 规则包含 libtvm.so、libtvm_runtime.so
- [x] install 规则包含引导 __init__.py（通过 file(GENERATE) 生成）
- [x] 安装目录通过 wheel.install-dir="." 映射到 site-packages 根
- [ ] cmake --install 成功执行（需 Linux 环境）
- [ ] 安装目录结构符合预期（需 Linux 环境）

## Task 9 验证：端到端验证脚本（脚本完成 ✓，需 Linux 运行时验证）
- [x] scripts/verify_wheel.py 存在且语法正确
- [x] inv verify 任务注册正确（自动发现 dist/ 中最新 whl）
- [x] 验证点覆盖：import tvm/vta/xmnn、ctypes 加载 libtvm、.rly 数据文件、.json 配置文件
- [x] 使用临时虚拟环境隔离测试
- [ ] 干净虚拟环境中 pip install xmnn-*.whl 成功（需 Linux 环境）
- [ ] python -c "import tvm" 成功（需 Linux 环境）
- [ ] python -c "import vta" 成功（需 Linux 环境）
- [ ] python -c "import xmnn" 成功（需 Linux 环境）
- [ ] libtvm.so 可被 ctypes 加载（需 Linux 环境）
- [ ] .rly 数据文件可通过 tvm 包内路径访问（需 Linux 环境）
- [ ] .json 配置文件可通过 vta 包内路径访问（需 Linux 环境）
- [ ] 无 ImportError、无 OSError、无 FileNotFoundError（需 Linux 环境）

## 一键构建验证（需 Linux 环境）
- [ ] inv clean 清空构建目录
- [ ] inv build-all 从头至尾无中断执行成功
- [ ] 最终 dist/ 目录生成可用的 whl 文件
- [ ] inv verify 所有检查通过
