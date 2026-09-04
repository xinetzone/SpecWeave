# caffe-ffi Conda 构建 pip install tvm-ffi 集成方案 - Implementation Plan

## [x] Task 1: 修改 Dependencies.cmake 支持 pip-installed tvm-ffi 优先
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修改 cmake/Dependencies.cmake，当 tvm-ffi 已通过 pip 安装（`python -m tvm_ffi.config --cmakedir` 成功返回）时，优先使用 find_package(tvm_ffi CONFIG)，而不是自动 add_subdirectory
  - 引入选项 `CAFFE_FFI_PREFER_SYSTEM_TVM_FFI`（默认 ON），优先通过 Python 获取 cmakedir
  - 逻辑变更：先尝试 find_package（通过 Python 获取 cmakedir），找不到时再回退到本地 add_subdirectory 模式
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: ✅ CMake 配置输出 "Found tvm-ffi CMake config via Python"
  - `programmatic` TR-1.2: 本地 vendor/tvm-ffi 存在但 tvm_ffi.config 不可用时回退到 add_subdirectory 模式（向后兼容）
  - `human-judgement` TR-1.3: ✅ 代码逻辑清晰，两条路径互斥，无重复链接

## [x] Task 2: 修改 build.sh —— 先 pip install 本地 tvm-ffi
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 build.sh 步骤1中，当检测到本地 vendor/tvm-ffi 时，执行 `$PYTHON -m pip install ${LOCAL_TVM_FFI_DIR} --no-deps -vv --no-build-isolation` 安装 tvm-ffi 到构建环境
  - pip install tvm-ffi 时清空 conda 的 CMAKE_ARGS，使用空格分隔的 SKBUILD_CMAKE_ARGS 传递参数
  - 关键：添加 -DTVM_FFI_BUILD_PYTHON_MODULE=ON 确保 Cython 扩展编译
  - 保留 pip 回退模式：本地 tvm-ffi 不存在时回退到 pip install apache-tvm-ffi
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: ✅ build.sh 输出 "Installing local tvm-ffi from: <path>" 并成功 pip install
  - `programmatic` TR-2.2: ✅ 安装后 tvm_ffi 从 $SP_DIR/tvm_ffi/ 加载（非源码目录）
  - `programmatic` TR-2.3: ✅ nm -D 显示 libtvm_ffi.so 包含 TVMFFIGetCustomAllocator 符号（T类型）
  - `human-judgement` TR-2.4: ✅ 非 editable 安装，所有文件在 $SP_DIR/tvm_ffi/ 下

## [x] Task 3: 简化 build.sh Post-build 步骤（移除手动 libtvm_ffi 复制逻辑）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 移除复杂的 libtvm_ffi.so 多位置搜索和手动复制逻辑
  - RPATH 通过 CMAKE_INSTALL_RPATH 在 CMake 构建时设置，post-build 仅验证
  - RPATH 设置为 `$ORIGIN:$ORIGIN/lib:$ORIGIN/../tvm_ffi/lib:${PREFIX}/lib`
- **Acceptance Criteria Addressed**: AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-3.1: ✅ ldd 显示 libtvm_ffi.so => $SP_DIR/tvm_ffi/lib/libtvm_ffi.so
  - `programmatic` TR-3.2: ✅ 构建日志无 "Copying libtvm_ffi" 手动复制输出
  - `programmatic` TR-3.3: ✅ RPATH 包含 $ORIGIN/../tvm_ffi/lib 相对路径
  - `human-judgement` TR-3.4: ✅ build.sh 代码量减少，逻辑更清晰

## [x] Task 4: 更新 meta.yaml 依赖配置
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - build number 递增到 1
  - host 依赖添加 setuptools-scm 和 typing-extensions
  - test 段添加 tvm_ffi import 和 native 可用性检查
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: ✅ conda build 成功完成
  - `programmatic` TR-4.2: 安装后 tvm_ffi 模块可导入
  - `human-judgement` TR-4.3: ✅ meta.yaml 依赖关系清晰

## [x] Task 5: 更新验证脚本 (full-clean-rebuild.sh)
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - 增强清理逻辑：移除指向源码目录的 .pth 文件，清理 tvm_ffi site-packages 残留
  - 修复 Blob 测试 API：使用 to_numpy() 代替不存在的 data_at()
  - 修复 conda-build --test：传入 .conda 包文件路径而非 recipe 目录
  - 添加 nm 符号检查和 ldd 依赖验证
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: ✅ full-clean-rebuild.sh 执行完成，所有检查点 PASS
  - `programmatic` TR-5.2: ✅ caffe_ffi.is_available() 返回 True
  - `programmatic` TR-5.3: ✅ Blob 测试通过（创建、填充1.0、to_numpy验证）

## [x] Task 6: 端到端验证 —— Docker 容器中完整构建+安装+测试
- **Priority**: high
- **Depends On**: Task 1-5
- **Description**:
  - 在 caffe-ffi-jupyter Docker 容器中运行 full-clean-rebuild.sh
  - 验证完整流程：清理 → 构建 → 安装 → 导入测试 → 功能测试 → ldd 检查
- **Acceptance Criteria Addressed**: AC-1 through AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: ✅ 完整构建流程 PASS
  - `programmatic` TR-6.2: ✅ caffe_ffi.is_available() = True
  - `programmatic` TR-6.3: ✅ Blob([100]).fill(1.0); count()=100, to_numpy()全为1.0
  - `programmatic` TR-6.4: ✅ ldd 无 "not found"
  - `programmatic` TR-6.5: 回退模式未测试（核心路径已验证通过）
