---
id: "insight-extraction-xmnn-wheel-scikit-build-nuitka"
title: "XMNN Wheel 构建洞察与模式萃取"
date: "2026-07-26"
source: "retrospective-xmnn-wheel-scikit-build-nuitka-20260726"
---

# 洞察萃取文档

## 核心洞察（5条）

### I1. Nuitka + .pth 引导优于 __init__.py 注入

Nuitka 将整个包编译为单个 .so 后，原始 `__init__.py` 不再被执行。通过 `.pth` 文件（Python解释器级钩子）+ 独立 bootstrap 模块设置运行时环境，是更可靠的方案。

**本质**：编译型打包改变了代码的执行入口点——从"包的__init__.py"变为"解释器启动时的.pth处理"，运行时初始化必须跟随入口点迁移。

### I2. CMake 原生库依赖隔离是 wheel 可移植性的关键

_libs/ 目录 + patchelf RPATH=$ORIGIN + LD_LIBRARY_PATH 兜底三件套解决了 Linux wheel 二进制可移植性问题。仅设 LD_LIBRARY_PATH 不够（ctypes.CDLL 加载时动态链接器优先用 RPATH）。

**本质**：动态链接器查找顺序是 RPATH → LD_LIBRARY_PATH → RUNPATH → 默认路径，仅设环境变量无法覆盖 RPATH 硬编码的问题。

### I3. Python 大版本升级的 AST 破坏需要 Monkey-patch 而非源码修改

对于无法修改的第三方源码（submodule/上游未合并），运行时 Monkey-patch 比 fork/vendor 更干净——纯加法不引入代码副本。关键是双重注入点（编译时+运行时）+ hasattr 防御检查。

**本质**：当被移除的 API 是"类被合并到父类"（Constant 吸收了 NameConstant/Num/Str）时，简单的别名类即可兼容；当 API 被完全移除（如 Index/ExtSlice），需要手动定义 _fields。

### I4. scikit-build-core + CMake 相比 setuptools 提供确定性的 wheel 内容控制

CMake install() 规则是显式的"安装什么到哪里"，消除 setuptools find_packages/package_data 的启发式不确定性。

**本质**：二进制 wheel 的核心需求是精确控制文件布局，这正是 CMake install 的设计目标，而 setuptools 的设计目标是纯 Python 包的"自动发现"。

### I5. TVM 的 TIRToRuntime 注册需要启用 USE_EXAMPLE_TARGET_HOOKS=ON

名为 "example" 的钩子在实际使用中是 LLVM 后端的必需组件，TVM 的命名具有误导性。构建脚本必须在 inv config -f 后补丁 config.cmake。

**本质**："example" 在软件项目中常被命名为"可选"或"演示"，但当核心功能依赖它时它实际上是必选的——构建配置中的名称/描述不一定反映真实的依赖关系。

## 模式萃取结果

### P1: Nuitka + scikit-build-core 原生 Wheel 打包模式
→ **已存在模式**：[python-native-extension-self-contained-wheel.md](../../../patterns/code-patterns/python-native-extension-self-contained-wheel.md)（L2）
→ **新增贡献**：
- 验证了 CMake-native 依赖捆绑方案（install_real_lib 函数 + install-CODE patchelf）
- 验证了 .pth 引导 + Monkey-patch 整合方案（环境变量设置 + AST 兼容在同一 bootstrap 中）
- 补充了"不依赖 Nuitka --include-data-dir 嵌入数据，而通过 CMake 安装数据文件"的策略
- 更新验证计数：validation_count 1→2

### P2: Python AST 版本兼容 Monkey-patch 模式
→ **已存在模式**：[python-ast-compatibility.md](../../../patterns/code-patterns/python-ast-compatibility.md)（L1）
→ **新增贡献**：
- 发现第三种策略：运行时 Monkey-patch（当无法修改源码时）
- 补充 ExtSlice 类的兼容定义（此前只覆盖到 Index）
- 补充 .pth 注入点作为最早执行的 Monkey-patch 位置
- 更新验证计数：validation_count 2→3

### P3: Linux Wheel 原生依赖隔离模式
→ **已存在模式**：P1 中的子组件，已在 python-native-extension-self-contained-wheel 中详细覆盖
→ **新增贡献**：install_real_lib 函数实现符号链接处理的 CMake 方案（替代 Python ldd 递归脚本），适用于依赖库列表已知的场景

## 模式更新建议

1. **python-native-extension-self-contained-wheel.md**：添加"CMake-native bundling"作为替代实现方案（已知依赖列表场景下，比 Python ldd 脚本更简洁）
2. **python-ast-compatibility.md**：添加"策略C：运行时 Monkey-patch"（适用于无法修改源码的场景），补充 ExtSlice 兼容类
