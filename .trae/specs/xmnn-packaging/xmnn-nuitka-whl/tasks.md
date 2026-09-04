# XMNN Nuitka Wheel 包构建系统 - 实现计划（v2，基于 scikit-build-core + CMake）

## [x] Task 1: 清理旧 setuptools 配置并创建新 pyproject.toml
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 删除旧的 setup.py、MANIFEST.in（如有）
  - 创建新的 pyproject.toml，build-backend 设为 `scikit_build_core.build`
  - 在 [project] 中声明 name="xmnn"、version、dependencies（numpy 等）
  - 在 [tool.scikit-build] 中配置 cmake/ninja 最低版本、build-type、wheel 相关设置
  - 在 [build-system] requires 中声明 scikit-build-core、cmake、ninja、nuitka 为构建时依赖
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: pyproject.toml 存在且 TOML 语法正确
  - `programmatic` TR-1.2: build-backend 值为 "scikit_build_core.build"，无 setuptools 引用
  - `programmatic` TR-1.3: 目录下无 setup.py、无 MANIFEST.in
  - `human-judgement` TR-1.4: [project] 元数据完整，依赖列表合理
- **Notes**: 不保留任何 setuptools 残留

## [x] Task 2: 创建 CMakeLists.txt 构建脚本
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 xmtools/CMakeLists.txt，使用 cmake_minimum_required(VERSION 3.18...3.27)
  - project(xmnn LANGUAGES NONE)（纯 Python 包，不需要 C/C++ 编译器）
  - find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
  - 定义变量：TVM_ROOT、XMN_ROOT、NUITKA_OUTPUT_DIR（build/nuitka）、TVM_BUILD_DIR
  - install(DIRECTORY) 安装 xmnn 纯 Python 包到 site-packages/xmnn
  - install(FILES) 安装 Nuitka 编译产物 tvm.so/tvm.pyi 到 site-packages/tvm
  - install(DIRECTORY) 安装 tvm.data/ 数据目录到 site-packages/tvm（包含 relay/std）
  - install(FILES) 安装 vta.so/vta.pyi 到 site-packages/vta
  - install(DIRECTORY) 安装 vta.data/ 数据目录到 site-packages/vta（包含 vta_hw/config）
  - install(FILES) 安装 libtvm.so/libtvm_runtime.so/libvta*.so 到 site-packages/tvm 或 lib 目录
  - install(FILES) 安装路径适配 __init__.py 引导文件（处理 Nuitka 编译后数据路径和原生库路径）
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: CMakeLists.txt 存在且语法正确
  - `programmatic` TR-2.2: `cmake -S . -B build/cmake-test` 配置成功（无错误）
  - `programmatic` TR-2.3: install 规则覆盖 tvm、vta、xmnn 三个包以及所有 .so 库
  - `human-judgement` TR-2.4: CMake 结构清晰，变量命名规范
- **Notes**: 使用 LANGUAGES NONE 避免不必要的 C 编译器检查；所有路径用相对于 PROJECT_SOURCE_DIR 的方式表达

## [x] Task 3: 完善 invoke tasks.py - 环境管理与 TVM 构建
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 完善 tasks.py 中 init、check_deps、clean 任务
  - 实现 build-tvm 任务：cd 到 npu_tvm 执行 `inv config -f` 和 `inv make`
  - build-tvm 完成后验证 libtvm.so、libtvm_runtime.so 存在并打印路径/大小
  - check_deps 检查 cmake、ninja、nuitka、python、invoke 可用性
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: `inv --list` 显示所有注册的任务
  - `programmatic` TR-3.2: `inv check-deps` 能正确报告工具可用性
  - `programmatic` TR-3.3: `inv init` 创建 build/、build/nuitka/、dist/ 目录
  - `programmatic` TR-3.4: `inv clean` 删除 build/ 和 dist/
  - `human-judgement` TR-3.5: build-tvm 任务有清晰进度输出和错误处理
- **Notes**: 当前环境为 Windows，实际构建命令需在 WSL/Linux 执行

## [x] Task 4: 实现 Nuitka 编译 tvm 任务
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 实现 `nuitka-tvm` invoke 任务
  - 命令：`python -m nuitka --module --follow-imports --include-data-dir=<std_dir>=relay/std --output-dir=build/nuitka --output-filename=tvm.so <tvm_python_dir>/tvm`
  - 设置 PYTHONPATH 包含 npu_tvm/python 让 Nuitka 能找到 tvm 包
  - 编译完成后验证 tvm.so、tvm.pyi、tvm.data/relay/std 存在
  - 处理可能的 Nuitka 编译选项（--noinclude-* 排除不需要的模块，--lto 可选）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 任务存在，命令行参数包含 --module 和 --include-data-dir
  - `programmatic` TR-4.2: 目标数据目录 relay/std 路径正确传递给 Nuitka
  - `human-judgement` TR-4.3: 编译命令设置了合理的 PYTHONPATH 和输出目录
- **Notes**: Nuitka 编译大型包可能耗时较长；--include-data-dir 语法为 `源目录=目标相对路径`

## [x] Task 5: 实现 Nuitka 编译 vta 任务
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 实现 `nuitka-vta` invoke 任务
  - 命令：`python -m nuitka --module --follow-imports --include-data-dir=<config_dir>=vta_hw/config --output-dir=build/nuitka --output-filename=vta.so <vta_python_dir>/vta`
  - 设置 PYTHONPATH 包含 npu_tvm/vta/python 和 npu_tvm/python
  - 编译完成后验证 vta.so、vta.pyi、vta.data/vta_hw/config 存在
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: 任务存在，命令行参数包含 --module 和 --include-data-dir
  - `programmatic` TR-5.2: 目标数据目录 vta_hw/config 路径正确传递
  - `human-judgement` TR-5.3: PYTHONPATH 包含 tvm 和 vta 的 Python 路径
- **Notes**: vta 可能依赖 tvm，确保 PYTHONPATH 顺序正确

## [x] Task 6: 路径适配与原生库加载引导
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - 创建 xmtools/xmnn/_loader.py 或在 install 时生成引导文件
  - 引导逻辑：
    1. 在 import tvm 前设置 `TVM_LIBRARY_PATH` 指向 wheel 包内的 .so 文件所在目录
    2. 处理 Nuitka 编译后 `__file__` 指向 .so 文件的问题，计算正确的数据文件路径
    3. 添加 wheel 包内 lib 目录到 LD_LIBRARY_PATH（或通过 ctypes.CDLL 直接加载）
  - 安装到 site-packages 的 tvm/ 和 vta/ 目录需要一个 `__init__.py` 来：
    - 从 .so 文件导入所有内容
    - 暴露 `__file__` 和数据目录路径给子模块使用
  - 由于 Nuitka --module 已经生成一个 tvm.so（作为扩展模块，可以直接 import），可能需要一个薄 __init__.py 做路径修复后再从 .so 导入
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `human-judgement` TR-6.1: 引导逻辑清晰，处理了 .so 加载路径和数据路径
  - `programmatic` TR-6.2: 引导文件会被 CMake install 到正确位置
  - `programmatic` TR-6.3: 设置了 TVM_LIBRARY_PATH 或等效机制
- **Notes**: 这是最高风险任务，Nuitka 编译后 __path__ 和 __file__ 的行为需要实际测试；可先设计引导框架，Linux 环境中调试

## [x] Task 7: 实现 wheel 构建任务
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 实现 `build-wheel` invoke 任务
  - 任务逻辑：
    1. 确保 build/nuitka/ 下 tvm.so、vta.so 存在（否则给出错误提示）
    2. 确保 npu_tvm/build/ 下 libtvm*.so 存在
    3. 设置 CMake 变量指向预编译产物路径（如 -DNUITKA_OUTPUT_DIR=... -DTVM_BUILD_DIR=...）
    4. 执行 `python -m build --wheel --outdir dist/` 或 `pip wheel . --no-deps -w dist/`
    5. 构建完成后列出 dist/ 中的 whl 文件信息
  - 实现 `build-all` 一键任务：clean → build-tvm → nuitka-tvm → nuitka-vta → build-wheel
- **Acceptance Criteria Addressed**: AC-6, AC-11
- **Test Requirements**:
  - `programmatic` TR-7.1: `inv build-wheel` 任务存在且依赖检查完整
  - `programmatic` TR-7.2: `inv build-all` 串联所有前置任务
  - `human-judgement` TR-7.3: 错误处理友好（前置产物缺失时给出明确提示）
- **Notes**: scikit-build-core 会自动调用 cmake 配置和构建；我们通过 CMake 变量传入预编译产物位置

## [x] Task 8: CMakeLists.txt install 规则完善
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - CMakeLists.txt 已完善 install 规则，覆盖 tvm、vta、xmnn 三个包以及所有 .so 库
  - 路径引导 __init__.py 通过 file(GENERATE) 在配置时生成
  - 相对路径自动转换为绝对路径（基于 PROJECT_SOURCE_DIR）
  - **运行时验证需在 Linux 环境执行**（需要 Nuitka 编译产物和 TVM 构建产物）
  - 预期安装后的目录结构：
    ```
    site-packages/
    ├── tvm/
    │   ├── __init__.py (路径引导)
    │   ├── tvm.so
    │   ├── tvm.pyi
    │   ├── tvm.data/
    │   │   └── relay/std/*.rly
    │   ├── libtvm.so
    │   └── libtvm_runtime.so
    ├── vta/
    │   ├── __init__.py (路径引导)
    │   ├── vta.so
    │   ├── vta.pyi
    │   └── vta.data/vta_hw/config/*.json
    └── xmnn/
        ├── __init__.py
        └── ... (其他 Python 模块)
    ```
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-8.1: CMakeLists.txt install 规则语法正确（静态检查通过）
  - `programmatic` TR-8.2: install 规则覆盖 tvm、vta、xmnn 三个包和 .so 库
  - `programmatic` TR-8.3: 路径引导文件由 CMake file(GENERATE) 生成
  - `programmatic` TR-8.4: **运行时验证**: `cmake --install` 成功，目录结构符合预期（需 Linux 环境）
- **Notes**: 运行时验证需在 WSL/Linux 中执行 `inv build-all` 后验证

## [x] Task 9: 端到端验证脚本
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 已创建验证脚本 scripts/verify_wheel.py
  - 验证逻辑：
    1. 接受 whl 文件路径参数
    2. 创建临时虚拟环境
    3. pip install whl
    4. 执行 import 测试：import tvm, import vta, import xmnn
    5. 验证 libtvm.so/libtvm_runtime.so 能被 ctypes 加载
    6. 验证 tvm.data/relay/std 目录中 .rly 文件可访问
    7. 验证 vta.data/vta_hw/config 配置文件可访问
    8. 清理临时环境
  - 已添加 `inv verify` 任务，可自动发现 dist/ 中最新的 whl 进行验证
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9, AC-10
- **Test Requirements**:
  - `programmatic` TR-9.1: 验证脚本存在且语法正确 ✓
  - `human-judgement` TR-9.2: 验证点覆盖所有 acceptance criteria ✓
  - `programmatic` TR-9.3: `inv verify` 任务注册正确（自动发现 whl 文件）
  - `programmatic` TR-9.4: **运行时验证**: 脚本在 Linux 环境中成功通过所有检查（需实际 whl 包）
- **Notes**: 运行时验证需在 Linux 环境构建 whl 后执行 `inv verify`
