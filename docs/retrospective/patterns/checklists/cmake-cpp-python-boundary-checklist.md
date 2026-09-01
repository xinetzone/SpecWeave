---
id: "cmake-cpp-python-boundary-checklist"
title: "CMake/C++/Python混合项目边界检查清单"
type: "checklist"
date: "2026-08-01"
maturity: "L1-experimental"
source: "caffe-ffi C++/Python交互边界修复 (2026-08-01)"
related_patterns:
  - "ffi-fallback-diagnostics"
  - "python-editable-import-isolation"
  - "const-cow-trigger"
  - "cmake-public-target-config-function"
  - "preflight-checks-script"
tags: ["cmake", "c++", "python", "ffi", "cow", "hybrid-project", "checklist", "build-system", "cross-language", "ci-gate"]
---

# CMake/C++/Python 混合项目边界检查清单模板

> **适用场景**：使用 pybind11 / tvm-ffi / nanobind / ctypes / cffi 等 FFI 机制的 C++/Python 混合项目
> **触发时机**：CI/CD流水线、代码审查(CR)、版本发布前、新功能开发完成后
> **检查方式**：逐项打勾，不通过项必须记录原因和修复计划

---

## 一、构建系统检查（对应模式：cmake-target-compile-def-visibility）

### 1.1 编译定义可见性

- [ ] **所有条件编译宏（`target_compile_definitions`）已正确标注可见性**
  - 仅内部实现使用的宏：`PRIVATE`
  - 需要下游（测试、其他库、Python扩展）可见的宏：`PUBLIC`
  - 仅下游需要、本目标不使用的宏：`INTERFACE`
- [ ] **测试目标能看到测试所需的宏定义**
  - 验证方法：`grep -r "CAFFE_FFI_ENABLE" build/` 确认测试编译单元中宏已定义
  - 常见陷阱：`PRIVATE` 宏不会传递给 `target_link_libraries(... _lib)` 的下游目标
- [ ] **头文件中的 `#ifdef` 与 CMake 中的 `target_compile_definitions` 一一对应**
  - 头文件中 `#ifdef FEATURE_X` 必须有对应的 CMake 定义
  - 不存在"头文件检查了但CMake从未定义"的僵尸宏
- [ ] **运行时开关优先于编译期开关**
  - 可选功能优先设计为运行时可切换（如 `SetCOWEnabled(bool)`），编译宏仅作默认值
  - 避免编译期宏在不同编译单元中不一致导致的 ODR 违规

### 1.2 目标链接与依赖

- [ ] **`target_link_libraries` 可见性正确**
  - 头文件中暴露的依赖类型：`PUBLIC`
  - 仅 .cpp 实现中使用的依赖：`PRIVATE`
- [ ] **Python 扩展模块的输出路径与 Python 搜索路径对齐**
  - 构建产物 `.so`/`.pyd`/`.dll` 输出到 Python 包目录（与 `__init__.py` 同级）
  - 构建脚本中的拷贝命令目标路径与 `_find_lib_path()` / `__file__` 搜索路径一致
- [ ] **跨平台库名变体已覆盖**（`.so`/`.pyd`/`.dll`/`.dylib`，含版本后缀如 `.cp314-win_amd64.pyd`）
- [ ] **RPATH 设置正确**（Linux/macOS）：`CMAKE_BUILD_RPATH_USE_ORIGIN=ON`，安装后不依赖构建目录

### 1.3 跨OS构建模式（"Edit outside, build inside"）

- [ ] **源码目录与构建目录分离**
  - 源码在 bind mount（宿主机文件系统，如 NTFS）
  - 构建目录在容器原生文件系统（ext4/volume），规避 CRLF/权限/文件锁问题
- [ ] **构建前有 CRLF 修复步骤**（autotools/configure/cmake 脚本对 CRLF 敏感）
- [ ] **构建产物回拷到源码树的包目录后才运行 Python 测试**

---

## 二、C++ 核心逻辑检查（对应模式：cow-trigger-path-completeness）

### 2.1 COW/共享语义完整性

- [ ] **所有 mutable 访问路径都有 COW 触发检查**
  - 需检查的访问器清单：返回可写指针/引用的所有方法
  - C风格裸指针访问器（如 `cpu_mutable_data()`）
  - 引用/智能指针访问器（如 `mutable_data_tensor()`）
  - STL风格可变迭代器（如 `mutable_begin()/mutable_end()`）
  - 显式分离方法（如 `UnshareData()`）
- [ ] **COW 触发条件完整**
  - `IsCOWEnabled()`（运行时开关）
  - `tensor_.defined()`（tensor已分配）
  - `tensor_.use_count() > 1`（被多个持有者共享）
- [ ] **共享状态标志与引用计数分离**
  - 有独立的布尔标志区分"主动借出"和"use_count > 1"
  - 不能仅用 `use_count() > 1` 判断"是否需要COW"
  - Reshape/重新分配时正确清除共享标志
- [ ] **深拷贝集中化**：所有COW路径通过单一 `CloneTensor()` 函数执行memcpy，便于审计和日志

### 2.2 不变量维护

- [ ] **类不变量在所有操作后仍然成立**
  - 例：Blob的data和diff始终同shape
  - ShareData/ShareDiff/Reshape等操作后验证不变量
  - 建议：debug模式下添加断言检查不变量
- [ ] **跨方法调用的隐式假设已文档化**
  - 如"ShareDiff必须在ShareData之后调用"——如果不强制，需处理无序调用

### 2.3 零拷贝路径

- [ ] **ShareData/ShareDiff 正确设置共享标志**
- [ ] **BatchShareData/BatchShareDiff 在N<阈值时退化到逐个Share**
- [ ] **SharesDataWith/SharesDiffWith 正确比较底层指针**

---

## 三、Python FFI 边界检查（对应模式：ffi-fallback-state-consistency）

### 3.1 初始化与降级路径

- [ ] **FFI 初始化函数的所有退出路径都显式设置状态标志**
  - 成功路径：`_ffi_available = True`
  - 找不到库：`_ffi_available = False`
  - 导入失败（ImportError）：`_ffi_available = False`
  - 其他异常：`_ffi_available = False`
  - 最佳实践：函数入口统一预设 `_ffi_available = False`，成功路径覆盖为 `True`
- [ ] **纯Python降级模式可用**
  - `is_available() == False` 时，核心数据类（Blob/Net等）仍可构造
  - 纯Python模式下方法调用不依赖C++注册的类型
  - 有明确的 warning 日志提示用户原生库未加载
- [ ] **Registry/Object 代理类正确处理不可用状态**
  - `registry.Object` 在FFI不可用时抛出清晰的 RuntimeError
  - 不返回 None 导致后续 AttributeError 难以诊断

### 3.2 静默失败防护

- [ ] **所有"静默返回None/False"的分支都有 warning 级别日志**
- [ ] **`allow_missing=True` 的 FFI 函数调用后检查返回值是否为 None**
- [ ] **类型注册失败时不静默跳过**，至少记录 warning
- [ ] **环境变量控制的降级开关**（如 `CAFFE_FFI_FORCE_PYTHON_ONLY=1`）便于测试

### 3.3 库搜索路径

- [ ] **`_find_lib_path()` 搜索路径覆盖所有构建配置**
  - 包内目录（`Path(__file__).parent`）
  - 各构建目录（build/, build-cmake/, build-wheel/, build-ninja/）的 Release/lib/ 子目录
  - 跨平台库名变体
- [ ] **搜索失败返回 None 而非抛出异常**
- [ ] **Windows DLL 搜索路径已通过 `os.add_dll_directory()` 配置**

---

## 四、Python 测试隔离检查（对应模式：python-import-isolation-three-layers）

### 4.1 导入隔离三层清理

编写"库缺失/未安装"场景的测试时，必须清理三个层面：

- [ ] **Layer 1: sys.meta_path（Meta Path Finders）**
  - 移除 editable install finders（如 `ScikitBuildRedirectingFinder`）
  - 移除 namespace package finders
  - 判断方式：`type(f).__name__` 含 'editable' 或 'redirecting'
- [ ] **Layer 2: sys.path（搜索路径）**
  - 移除真实源码目录路径
  - 移除 `.pth` 文件注入的路径
  - 注意：项目根目录（脚本所在目录）也在 sys.path 中
- [ ] **Layer 3: sys.modules（模块缓存）**
  - 清除已缓存的目标模块及其子模块
  - 防止之前的 import 结果影响隔离环境

### 4.2 子进程测试模式

- [ ] **需要完全干净的Python环境时使用 subprocess**
  - 在子进程中做三层清理后再 import
  - 父进程的 import 状态不会泄漏到子进程
- [ ] **使用 `tempfile.TemporaryDirectory` 创建临时包副本**
  - 用 `shutil.copytree` 复制不含 `.so`/`.pyd`/`.dll` 的纯Python包
  - 设置 `PYTHONDONTWRITEBYTECODE=1` 防止 `.pyc` 缓存
- [ ] **子进程超时保护**：`subprocess.run(..., timeout=N)` 防止挂起
- [ ] **断言同时检查 stdout 和 stderr**，失败时输出两者便于诊断

### 4.3 Editable Install 感知

- [ ] **测试代码感知 editable install 的存在**
  - scikit-build-core、setuptools、flit 等各有不同的 finder 机制
  - CI环境可能也通过 `pip install -e .` 安装
- [ ] **不要依赖 sys.path 顺序来控制导入**，meta_path finder 优先于 sys.path 搜索

---

## 五、跨语言通用检查项

### 5.1 错误处理

- [ ] **C++ 异常在 FFI 边界被正确翻译为 Python 异常**
- [ ] **Python 回调中的异常不会导致 C++ 段错误**
- [ ] **资源释放路径在异常发生时仍然执行（RAII/try-finally）**

### 5.2 内存管理

- [ ] **numpy array 与 C++ tensor 的生命周期绑定正确**
  - 不出现 numpy array 持有悬空指针
  - 不出现 ctypes 指针上绑定引用导致的循环引用
- [ ] **COW 后的 tensor 引用计数正确**
- [ ] **零拷贝路径下 tensor 的 use_count 管理正确**

### 5.3 类型安全

- [ ] **Python 端有类型检查，拒绝错误 dtype/shape 的 tensor**
- [ ] **C++ 端有 CAFFE_FFI_CHECK_TYPE 宏验证前置条件**
- [ ] **DLPack/缓冲区协议互操作时验证 dtype 和 device**

---

## 使用说明

1. **新项目启动**：复制本模板作为 CR Checklist，逐项确认
2. **Bug修复后**：对照失败案例所在分类，补充检查项
3. **CI集成**：将可自动化的检查项（如 CMake PUBLIC/PRIVATE 检查、.so路径检查）编写为脚本
4. **团队分享**：每个模式配一个"反例→修复"的实际案例，帮助团队理解陷阱

### 快速自检命令

```bash
# 1. 检查PRIVATE宏是否被测试需要
cmake --build build --verbose 2>&1 | grep -D "CAFFE_FFI_ENABLE" | grep -v "test"  # 看测试编译时宏是否定义

# 2. 检查.so是否在正确位置
python -c "import caffe_ffi; print(caffe_ffi._ffi_api.lib_path())"  # 应输出非None路径

# 3. 检查Python-only模式
CAFFE_FFI_FORCE_PYTHON_ONLY=1 python -c "import caffe_ffi; print(caffe_ffi.is_available())"  # 应输出False

# 4. 运行Python隔离测试
python -m pytest tests/python/test_python_api.py::TestModuleAPI::test_python_only_fallback_when_native_lib_missing -v
```
