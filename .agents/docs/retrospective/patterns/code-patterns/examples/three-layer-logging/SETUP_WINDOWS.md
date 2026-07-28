# Windows 本地开发环境配置指南

跨语言三层日志示例包在 Windows 上的完整环境搭建、编译运行和故障排查指南。

## 目录

- [系统要求](#系统要求)
- [快速开始（5分钟）](#快速开始5分钟)
- [详细安装步骤](#详细安装步骤)
  - [1. Python 环境](#1-python-环境)
  - [2. C++ 编译器](#2-c-编译器)
  - [3. pytest（可选，用于测试套件）](#3-pytest可选用于测试套件)
- [验证安装](#验证安装)
- [运行测试](#运行测试)
- [常见问题排查](#常见问题排查)
- [编译器选项对比](#编译器选项对比)

---

## 系统要求

| 组件 | 最低版本 | 推荐版本 | 说明 |
|------|---------|---------|------|
| Windows | Windows 10 64位 | Windows 10/11 64位 | 32位系统不推荐（DLL加载受限） |
| Python | 3.9 | 3.11+ | 需与编译器架构一致（均为64位） |
| C++编译器 | Clang 14+ / GCC 11+ / MSVC 2022 | Clang 20+ (LLVM) | 需要支持 C++17 |
| pytest（可选） | 7.0 | 8.0+ | 仅运行 `test_three_layer.py` 需要 |
| 磁盘空间 | ~200MB | ~500MB | 编译器+Python+依赖 |

> **⚠️ 架构一致性（最容易踩坑）**：Python 和 C++ 编译器必须同为 64 位或同为 32 位。如果 Python 是 64 位（绝大多数现代安装），编译器也必须生成 64 位代码，否则会出现 `WinError 193: %1 不是有效的 Win32 应用程序` 错误。

---

## 快速开始（5分钟）

如果你已经有 Python 3.9+ 和一个 C++ 编译器，可以跳过安装直接验证：

```powershell
# 1. 进入示例目录
cd .agents\docs\retrospective\patterns\code-patterns\examples\three-layer-logging

# 2. 运行快速验证脚本（自动检测编译器、编译、加载、验证）
python run_test.py

# 3. 预期输出：6 passed
```

如果看到所有 6 项检查 ✅ 通过，说明环境已就绪。

---

## 详细安装步骤

### 1. Python 环境

#### 方案A：Anaconda/Miniconda（推荐）

```powershell
# 下载 Miniconda（轻量版）
# 访问 https://docs.conda.io/en/latest/miniconda.html
# 选择 "Miniconda3 Windows 64-bit" 下载安装

# 安装后验证
python --version
# 预期输出：Python 3.x.x

# 确认是64位
python -c "import struct; print(f'架构: {struct.calcsize(\"P\")*8}-bit')"
# 预期输出：架构: 64-bit
```

#### 方案B：官方 Python

```powershell
# 访问 https://www.python.org/downloads/
# 下载 "Windows installer (64-bit)"
# 安装时勾选 "Add Python to PATH"

# 验证
python --version
```

#### 方案C：检查现有 Python

```powershell
# 检查Python版本和架构
python -c "import sys, struct; print(f'Python {sys.version}'); print(f'架构: {struct.calcsize(\"P\")*8}-bit')"
```

---

### 2. C++ 编译器

Windows 上有三种编译器选择，按推荐度排序：

#### 方案A：Clang/LLVM（⭐ 推荐，最简单）

Clang 是 LLVM 项目的编译器，跨平台一致性好，错误信息友好，是本项目测试所用编译器。

```powershell
# 方法1：通过 Visual Studio Installer 安装（推荐）
# 1. 打开 Visual Studio Installer
# 2. 修改 → 单个组件 → 搜索 "C++ Clang"
# 3. 勾选 "适用于 Windows 的 C++ Clang 编译器" 和 "MSBuild 对 Clang/LLVM 的支持"
# 4. 安装

# 方法2：通过 winget 安装（需 Windows 10 1809+）
winget install LLVM.LLVM

# 方法3：手动下载
# 访问 https://releases.llvm.org/download.html
# 下载 "LLVM-xx.x.x-win64.exe"（64位安装包）
# 安装时勾选 "Add LLVM to PATH for all users"
```

安装后验证：

```powershell
clang++ --version
# 预期输出：clang version xx.x.x
# 注意Target行：显示 i686-pc-windows-msvc（32位默认）或 x86_64-pc-windows-msvc（64位）
```

> **⚠️ Clang默认架构问题**：Clang在Windows上默认目标可能是32位（i686）。如果你的Python是64位，需要在编译命令中添加 `--target=x86_64-pc-windows-msvc` 参数。本项目的 `run_test.py` 已自动处理此问题。

#### 方案B：MSVC（Visual Studio 自带）

```powershell
# 1. 安装 Visual Studio 2022（Community版免费）
#    下载：https://visualstudio.microsoft.com/
# 2. 安装时勾选"使用C++的桌面开发"工作负载
# 3. 在"开始"菜单中搜索并打开 "x64 Native Tools Command Prompt for VS 2022"
#    （注意必须是x64版本，不是x86版本）
# 4. 在该命令行中验证：
cl
# 预期输出：Microsoft (R) C/C++ Optimizing Compiler Version xx.x.x
```

#### 方案C：MinGW-w64（GCC）

```powershell
# 方法1：通过 winget 安装
winget install MSYS2.MSYS2
# 安装后打开 MSYS2 UCRT64 终端，执行：
# pacman -Syu
# pacman -S mingw-w64-ucrt-x86_64-gcc

# 方法2：通过 Chocolatey
choco install mingw

# 验证（在新终端中）
g++ --version
# 预期输出：g++ (x86_64-posix-seh-revX) xx.x.x
```

> **注意**：使用MinGW时，DLL文件扩展名为 `.dll`，但依赖的运行时（`libstdc++-6.dll`、`libgcc_s_seh-1.dll`）需要在PATH中可找到。

---

### 3. pytest（可选，用于测试套件）

`run_test.py` 不需要pytest，但 `test_three_layer.py` 是pytest测试套件，需要安装pytest：

```powershell
# 安装pytest
pip install pytest

# 验证
python -m pytest --version
# 预期输出：pytest 8.x.x
```

---

## 验证安装

### 快速诊断脚本

运行以下命令，一键检查所有依赖是否就绪：

```powershell
python -c "
import sys, struct, shutil, subprocess, os
from pathlib import Path

print('=== 环境诊断 ===')
print(f'Python: {sys.version.split()[0]} ({struct.calcsize(\"P\")*8}-bit)')

compilers = ['clang++', 'g++', 'cl']
found = []
for cc in compilers:
    if shutil.which(cc):
        found.append(cc)
print(f'编译器: {\", \".join(found) if found else \"未找到\"} (需要至少一个)')

try:
    import pytest
    print(f'pytest: {pytest.__version__}')
except ImportError:
    print('pytest: 未安装（run_test.py不需要，test_three_layer.py需要）')

# 检查源码文件
src_dir = Path('.')
required = ['log.hpp', 'ffi_bridge.cc', 'debug.py', 'run_test.py']
missing = [f for f in required if not (src_dir / f).exists()]
if missing:
    print(f'缺少文件: {missing}')
else:
    print('源码文件: 完整')

print('\\n=== 诊断结果 ===')
if found and not missing:
    print('✅ 环境就绪，可以运行 python run_test.py')
else:
    print('❌ 请先安装缺失的组件')
"
```

---

## 运行测试

### 快速验证（无需pytest）

```powershell
cd .agents\docs\retrospective\patterns\code-patterns\examples\three-layer-logging

# 自动编译+加载+验证，预期输出6项全绿
python run_test.py

# 清理之前的构建产物后重新运行
python run_test.py --clean
```

成功时输出：

```
============================================================
  Three-Layer Logging — Quick Validation
============================================================

[INFO] Platform: Windows AMD64
[INFO] Python: 3.x.x
[INFO] Compiler: clang++
[INFO] Compiling with clang++...
  ✅ Build successful: mylog_test.dll
[INFO] Loading shared library via ctypes...
  ✅ Library loaded successfully
  ✅ Default level is WARN (3)

Running validation checks...

  ✅ Check 1: Default WARN level filters correctly
  ✅ Check 2: DEBUG level shows DEBUG/INFO/WARN/ERROR
  ✅ Check 3: TRACE level shows all 5 levels
  ✅ Check 4: ERROR messages correctly routed to stderr
  ✅ Check 5: Grep-friendly format
  ✅ Check 6: GetLogLevel roundtrip

============================================================
  Results: 6 passed
============================================================
```

### 完整测试套件（需要pytest）

```powershell
# 运行全部28个测试用例
python -m pytest test_three_layer.py -v

# 只运行C++原生层测试
python -m pytest test_three_layer.py -v -k "CppNative"

# 只运行Python层测试
python -m pytest test_three_layer.py -v -k "Python"

# 只运行集成测试
python -m pytest test_three_layer.py -v -k "Integration"
```

---

## 常见问题排查

### 问题1：`OSError: [WinError 193] %1 不是有效的 Win32 应用程序`

**原因**：Python 是 64 位，但编译器生成了 32 位 DLL。

**解决方案**：

| 编译器 | 修复方法 |
|--------|---------|
| Clang | 编译命令添加 `--target=x86_64-pc-windows-msvc`（`run_test.py` 已自动处理） |
| MSVC | 使用 "x64 Native Tools Command Prompt"，不要用 "x86" 版本 |
| MinGW | 确保安装的是 `x86_64` 版本（不是 `i686` 版本） |

验证：
```powershell
# 检查Python架构
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"

# 检查Clang默认目标
clang++ --version 2>&1 | findstr "Target"
# 如果是 i686-pc-windows-msvc，说明默认32位，需要--target参数
```

---

### 问题2：`OSError: [WinError 126] 找不到指定的模块`

**原因**：DLL依赖的运行时库（如 `libc++`.dll、`libstdc++-6.dll`）不在PATH中。

**解决方案**：

- **Clang (MSVC target)**：需要从Visual Studio命令提示符运行，或确保vcruntime140.dll可访问
- **Clang (MinGW target)**：将Clang的bin目录加入PATH
- **MinGW/GCC**：将MinGW的bin目录加入PATH（如 `C:\msys64\ucrt64\bin`）

```powershell
# 临时添加到PATH（当前终端）
$env:PATH = "C:\Program Files\Microsoft Visual Studio\18\Insiders\VC\Tools\Llvm\bin;$env:PATH"

# 查看DLL依赖（需安装Dependencies工具或使用dumpbin）
# dumpbin /dependents build_test\mylog_test.dll
```

---

### 问题3：编译失败：`error: no member named 'cout' in namespace 'std'`

**原因**：MSVC的Clang默认不包含MSVC标准库路径，或缺少 `/EHsc` 异常处理标志。

**解决方案**：确保从正确的命令环境运行：

```powershell
# 使用Visual Studio开发者命令提示符（自动配置INCLUDE/LIB路径）
# 或使用clang-cl替代clang++：
clang-cl /nologo /EHsc /LD /Fe:mylog_test.dll -DMYPROJ_ENABLE_DEBUG_LOG -DMYPROJ_DLL_EXPORTS -I. ffi_bridge.cc
```

---

### 问题4：编译成功但日志输出为空（C++日志未捕获）

**原因**：在进程内通过 `os.dup2()` 重定向文件描述符时，C++ iostream（`std::cout`/`std::cerr`）在程序启动时已缓存了底层HANDLE，后续fd重定向对其无效。

**解决方案**：本项目已通过**子进程方式**解决此问题——`run_test.py` 和 `test_three_layer.py` 都通过 `_invoke_logs.py` 在子进程中加载DLL并触发日志，用 `subprocess.PIPE` 可靠捕获输出。这是Windows上捕获C++原生日志输出的推荐方式。

如果你在自己的代码中遇到此问题：
- ✅ **使用子进程**：`subprocess.run([...], capture_output=True)` 最可靠
- ❌ **避免进程内fd重定向**：`os.dup2()` 对C++ iostream无效
- ⚠️ **可以用freopen**：`freopen("NUL", "w", stdout)` 可重定向但无法恢复

---

### 问题5：`PermissionError: [WinError 5] 拒绝访问: ...mylog_test.dll`

**原因**：DLL被当前Python进程通过 `ctypes.CDLL()` 加载后，Windows锁定该文件直到进程退出。

**解决方案**：这是Windows的正常行为。`run_test.py` 已处理此问题——清理失败时不报错，下次运行时会自动覆盖编译。如果需要手动删除：

```powershell
# 关闭所有加载了该DLL的Python进程后再删除
taskkill /f /im python.exe
# 或者简单地忽略，下次编译会自动覆盖
```

---

### 问题6：`找不到clang++` 但已经安装了LLVM

**原因**：LLVM的bin目录未加入系统PATH。

**解决方案**：

```powershell
# 方法1：重新运行LLVM安装程序，勾选"Add to PATH"
# 方法2：手动添加到系统环境变量
# 右键"此电脑"→属性→高级系统设置→环境变量
# 在"系统变量"的Path中添加：C:\Program Files\LLVM\bin
# （具体路径取决于你的LLVM安装位置）

# 方法3：在当前PowerShell会话中临时添加
$env:PATH = "C:\Program Files\LLVM\bin;$env:PATH"

# 验证
clang++ --version
```

---

### 问题7：`pytest: 命令找不到`

**原因**：pytest未安装或不在PATH中。

**解决方案**：

```powershell
# 安装pytest
pip install pytest

# 如果pip安装的包不在PATH中，用python -m方式调用（推荐）
python -m pytest test_three_layer.py -v
```

---

## 编译器选项对比

如果你需要手动编译（不通过 `run_test.py`），以下是各编译器的命令：

| 编译器 | 编译命令 |
|--------|---------|
| **Clang++ (MSVC target)** | `clang++ --target=x86_64-pc-windows-msvc -shared -std=c++17 -O2 -DMYPROJ_ENABLE_DEBUG_LOG -DMYPROJ_DLL_EXPORTS -I. -o mylog.dll ffi_bridge.cc` |
| **clang-cl** | `clang-cl /nologo /EHsc /LD /Fe:mylog.dll -DMYPROJ_ENABLE_DEBUG_LOG -DMYPROJ_DLL_EXPORTS -I. ffi_bridge.cc` |
| **MSVC (cl)** | `cl /nologo /EHsc /LD /Fe:mylog.dll -DMYPROJ_ENABLE_DEBUG_LOG -DMYPROJ_DLL_EXPORTS -I. ffi_bridge.cc` |
| **MinGW (g++)** | `g++ -shared -std=c++17 -O2 -DMYPROJ_ENABLE_DEBUG_LOG -DMYPROJ_DLL_EXPORTS -I. -o mylog.dll ffi_bridge.cc` |

> **关键参数说明**：
> - `-shared` / `/LD`：编译为共享库（DLL）
> - `-DMYPROJ_ENABLE_DEBUG_LOG`：启用TRACE/DEBUG/INFO级别（Release构建不加此宏）
> - `-DMYPROJ_DLL_EXPORTS`：标记DLL导出（触发 `__declspec(dllexport)`）
> - `--target=x86_64-pc-windows-msvc`：Clang专用，强制64位MSVC目标

---

## Release vs Debug 编译

| 构建类型 | 编译参数 | 日志行为 |
|---------|---------|---------|
| **Debug/开发** | `-DMYPROJ_ENABLE_DEBUG_LOG -O0 -g` | TRACE/DEBUG/INFO/WARN/ERROR 全部受运行时级别控制 |
| **Release/生产** | 不加 `-DMYPROJ_ENABLE_DEBUG_LOG`，加 `-O2/-O3` | TRACE/DEBUG/INFO 在编译期被消除（零开销），仅保留 WARN/ERROR |

```powershell
# Debug构建（开发测试用）
clang++ --target=x86_64-pc-windows-msvc -shared -std=c++17 -O0 -g -DMYPROJ_ENABLE_DEBUG_LOG -DMYPROJ_DLL_EXPORTS -I. -o mylog_debug.dll ffi_bridge.cc

# Release构建（生产用，TRACE/DEBUG/INFO编译期消除）
clang++ --target=x86_64-pc-windows-msvc -shared -std=c++17 -O2 -DMYPROJ_DLL_EXPORTS -I. -o mylog.dll ffi_bridge.cc
```
