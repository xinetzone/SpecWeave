---
type: Wiki Tutorial

id: cpython-devguide-01
title: "01 - 贡献者快速上手"
date: 2026-08-19
tags: [cpython, quickstart, setup, build, first-pr, codespaces]
source:
  - devguide.python.org
  - github.com/python/cpython
  - external/libs/python/devguide
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/cpython-devguide-wiki/01-contributor-quickstart.toml"
maturity: L1-draft
---
# 01 - 贡献者快速上手

本章带你从零开始搭建CPython开发环境，提交你的第一个Pull Request。我们提供两种路径：**零配置Codespaces路径（5分钟）**和**本地环境路径（完整开发）**。

## 最快路径：GitHub Codespaces（5分钟）

如果你只是想快速体验或做简单修改（如文档修复、typo），GitHub Codespaces是最快方式：

1. 打开 [https://github.com/python/cpython](https://github.com/python/cpython)
2. 在键盘上按 **`,`** 键（英文逗号），这会打开GitHub Web Editor
3. 点击左上角 `≡` → `Open in Codespaces` → `Create codespace on main`
4. 等待约2-5分钟，环境自动配置完成
5. 打开终端（`Ctrl+`` `），即可使用：
   - `./python` 直接运行CPython（已预编译pydebug版本）
   - `./python -m test -j0` 运行测试
   - 编辑代码后直接在终端验证
6. 修改完成后，在Source Control面板提交并推送，然后创建PR

> 💡 Codespaces每月有免费额度（60小时/月 for 2-core），简单贡献完全够用。对于长期开发，建议搭建本地环境。

## 本地环境搭建

### 选项A：Docker Dev Container（推荐新手）

如果你安装了Docker和VS Code，可以使用Dev Container获得一致的开发环境：

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 和 [VS Code](https://code.visualstudio.com/)
2. 安装VS Code扩展：Dev Containers
3. Fork并克隆cpython仓库
4. 在VS Code中打开项目，点击右下角"Reopen in Container"
5. 等待容器构建完成，环境自动配置好

### 选项B：手动搭建

#### Step 1：安装Git

**Windows**：
- 下载 [Git for Windows](https://git-scm.com/download/win)
- 安装时确保选择 **"Checkout as-is, commit Unix-style line endings"**（即 `core.autocrlf=input`）
- 或者安装后执行：
  ```powershell
  git config --global core.autocrlf input
  ```

**macOS**：
```bash
xcode-select --install
# 这会安装Git和基本的编译工具
```

**Linux (Ubuntu/Debian)**：
```bash
sudo apt-get update
sudo apt-get install git
```

#### Step 2：Fork并克隆仓库

1. 在浏览器中打开 [https://github.com/python/cpython](https://github.com/python/cpython)
2. 点击右上角 **Fork** 按钮，将仓库fork到你的账户
3. 克隆你的fork到本地：
   ```bash
   git clone https://github.com/YOUR_USERNAME/cpython.git
   cd cpython
   ```
4. 添加官方仓库为upstream远程：
   ```bash
   git remote add upstream https://github.com/python/cpython.git
   ```
5. 验证远程配置：
   ```bash
   git remote -v
   # origin    https://github.com/YOUR_USERNAME/cpython.git (fetch)
   # origin    https://github.com/YOUR_USERNAME/cpython.git (push)
   # upstream  https://github.com/python/cpython.git (fetch)
   # upstream  https://github.com/python/cpython.git (push)
   ```

#### Step 3：安装编译依赖

**Ubuntu/Debian**：
```bash
sudo apt-get update
sudo apt-get install build-essential gdb lcov pkg-config \
  libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
  libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
  lzma lzma-dev tk-dev uuid-dev zlib1g-dev
```

**Fedora/RHEL**：
```bash
sudo dnf install dnf-plugins-core
sudo dnf builddep python3
sudo dnf install gdb lcov
```

**macOS**：
```bash
# 安装Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install openssl@3.0 xz gdbm tcl-tk

# 注意：macOS上运行编译后的python使用 ./python.exe 而非 ./python
# 这是为了避免与源码目录中的 Python/ 目录发生冲突
```

**Windows**：
- 安装 **Visual Studio 2017或更高版本**（Community版免费）
- 安装时勾选 **"Python development workload"**
- 或单独安装：MSVC v142+ 生成工具、Windows 10/11 SDK
- 无需额外安装make或configure工具

#### Step 4：编译CPython

**Unix/Linux**：
```bash
# ⚠️ 开发必须使用 --with-pydebug！
# 这会启用断言检查、调试符号、内存调试，帮助捕获bug
./configure --with-pydebug
make -j$(nproc)

# 验证编译成功
./python --version
# 输出应包含 "debug" 标识，如：Python 3.14.0a0 (debug build)
```

**macOS**：
```bash
./configure --with-pydebug
make -j$(sysctl -n hw.logicalcpu)

# ⚠️ macOS注意：使用 ./python.exe 而非 ./python
./python.exe --version
```

**Windows**：
```powershell
# ⚠️ 使用 -e -d 参数（不是 -c Debug）
# -e: 下载并构建外部依赖
# -d: Debug构建（等价于pydebug）
PCbuild\build.bat -e -d

# ⚠️ 使用 .\python.bat 运行（不是直接执行 PCbuild\amd64\python_d.exe）
.\python.bat --version
```

> ⚠️ **重要提醒**：
> - **开发必须使用pydebug/debug版本**！发行版构建（`--enable-optimizations --with-lto`）只用于基准测试，会关闭断言，隐藏bug。
> - **不需要 `make install`**！CPython支持原地运行（in-place build），编译后直接在源码目录运行即可。
> - **不要**将自己编译的CPython添加到系统PATH，这会与系统Python冲突。

#### Step 5：安装pre-commit钩子

pre-commit会在每次commit时自动检查代码风格和格式：

```bash
# 确保使用你编译的python
./python -m pip install pre-commit
# Windows: .\python.bat -m pip install pre-commit

# 安装git hooks
pre-commit install
```

pre-commit会自动运行的检查包括：
-  trailing whitespace（尾部空白）
-  Tabs vs spaces（制表符检查）
-  End of file newline（文件末尾换行）
-  Ruff linter（代码风格）
-  Spell check（拼写检查，针对文档）

#### Step 6：运行测试验证环境

```bash
# 全量测试（首次验证环境是否正确）
# -j0 表示自动使用所有CPU核心
./python -m test -j0
# macOS: ./python.exe -m test -j0
# Windows: .\python.bat -m test -j0
```

测试全部通过（或只有少量非预期失败）即说明环境搭建成功。首次全量测试可能需要5-15分钟。

## 提交第一个PR：11步完整流程

### Step 1：找到要修复的问题

- 在 [GitHub Issues](https://github.com/python/cpython/issues) 搜索带 `easy` 标签的issue
- 或发现文档中的typo、代码中的小bug
- 如果修复的是新发现的问题，先创建一个Issue描述问题

> 💡 新手建议：从文档typo修复、测试补充开始，或搜索 `label:easy` 的Issue。

### Step 2：创建特性分支

```bash
# 先更新本地main分支
git switch main
git pull upstream main

# 从upstream/main创建新分支
# 分支名建议包含issue编号和简短描述
git switch -c fix-gh-12345-typo-in-docstring upstream/main
```

### Step 3：修改代码

遵循以下原则：
- 遵循PEP 8（Python代码风格）和PEP 7（C代码风格）
- 保持最小改动，不要混入无关修改
- 修改bug时，先写能复现bug的测试，再修复
- 保持向后兼容（除非是main分支上有意为之的breaking change）

### Step 4：添加测试

任何bug修复或新功能都**必须**包含测试：

- 测试文件位于 `Lib/test/` 目录
- 测试类继承 `unittest.TestCase`
- 测试方法以 `test_` 开头
- 修复bug时，测试应在修复前失败，修复后通过

```bash
# 示例：运行你添加的测试
./python -m test test_your_module -v
```

### Step 5：本地验证

```bash
# 1. 运行相关测试
./python -m test test_your_module -v

# 2. 运行patchcheck（检查常见问题）
make patchcheck
# Windows: PCbuild\python.bat Tools\patchcheck\patchcheck.py

# 3. 如果是较大改动，运行全量测试
./python -m test -j0
```

### Step 6：添加NEWS条目（如需要）

**什么情况需要NEWS条目**：
- ✅ Bug修复（影响用户的可见变更）
- ✅ 新功能添加
- ✅ 行为变更
- ✅ C API变更
- ❌ 纯文档修改
- ❌ 纯测试修改
- ❌ Typo修正
- ❌ 内部重构（不影响用户）
- ❌ 注释/空白清理

```bash
# 使用blurb添加NEWS条目
./python -m blurb add
# Windows: .\python.bat -m blurb add

# 按提示选择分类（Library/C API/Security等）
# 输入简短描述，blurb会自动创建Misc/NEWS.d/next/目录下的文件
```

### Step 7：提交代码

```bash
# 暂存修改（推荐用-p逐块审查）
git add -p

# 提交——commit message格式很重要！
git commit -m "gh-12345: Fix typo in datetime.__add__ docstring"
```

**Commit Message格式**：
- 格式：`gh-ISSUENUM: 简短描述`
- 描述使用祈使句（Fix而非Fixed/Fixes）
- 首字母大写
- 末尾不加句号
- 不超过72字符

**好的示例**：
```
gh-12345: Fix reference leak in os.scandir()
gh-12346: Add tests for datetime.fromisoformat() edge cases
gh-12347: Improve error message for invalid mode in open()
```

**差的示例**：
```
fix bug               # 没有issue编号，描述不清
Fixed a typo.         # 没有issue编号，用了过去式
gh-12345: I fixed the bug in os module that was causing crash on Windows when path is too long.  # 太长
update                # 无意义描述
```

### Step 8：推送到你的Fork

```bash
git push origin fix-gh-12345-typo-in-docstring
```

### Step 9：在GitHub创建PR

1. 打开 [https://github.com/python/cpython](https://github.com/python/cpython)，GitHub会自动检测到你的新分支并显示 **"Compare & pull request"** 按钮
2. 点击创建PR
3. PR标题自动使用commit message，保持 `gh-NNNNN: description` 格式
4. PR描述中：
   - 说明修改内容和原因
   - 关联Issue（写 `Fixes gh-NNNNN`，合并时会自动关闭issue）
   - 描述测试情况
   - 如果是文档修改，标注 `skip issue` 和 `skip news`（如适用）
5. 点击 **Create pull request**

**PR描述模板示例**：
```markdown
# 改动内容

修复了 `datetime.__add__` 文档字符串中的typo：将"timdelta"改为"timedelta"。

# Issue关联

Fixes gh-12345

# 测试

- [x] 运行了相关测试 `./python -m test test_datetime`
- [x] 运行了 `make patchcheck`
- [x] 文档修改，不需要NEWS条目
```

### Step 10：签署CLA（仅首次）

如果你是第一次贡献，PR页面会显示CLA检查失败。

1. 点击PR中的CLA详情链接
2. 使用GitHub账户登录 [PSF CLA签署页面](https://www.python.org/psf/contrib/contrib-form/)
3. 填写信息并提交
4. 回到PR页面，回复 "I have signed the CLA" 或等待cla-bot自动检测

> CLA只需要签署一次，所有后续PR自动通过CLA检查。

### Step 11：响应Review与后续清理

- 当Core Dev要求修改时，**不要force-push、不要squash、不要rebase**
- 直接在你的分支上做修改，然后正常commit和push：
  ```bash
  # 修改代码后
  git add -p
  git commit -m "Address review comments"
  git push origin fix-gh-12345-typo-in-docstring
  ```
- PR被squash merge后，清理本地分支：
  ```bash
  git switch main
  git pull upstream main
  git branch -d fix-gh-12345-typo-in-docstring
  git push origin --delete fix-gh-12345-typo-in-docstring
  ```

> ⚠️ **PR review期间绝对禁止force-push！**
> - Core Dev需要看增量diff来理解你每次修改了什么
> - 合并时GitHub会自动squash所有commit为一个干净的commit
> - 你不需要也不应该自己squash/rebase

## 跨平台编译特殊说明

| 平台 | 说明 |
|------|------|
| **WASI (WebAssembly)** | `./configure --with-pydebug --target=wasm32-wasi && make -j$(nproc)`。需要[wasi-sdk](https://github.com/WebAssembly/wasi-sdk)。 |
| **Emscripten (浏览器)** | 使用 `Tools/wasm/configure-emscripten-wasm64` 和 `Tools/wasm/build-emscripten.sh`。需要Emscripten SDK。 |
| **iOS** | 需要Xcode，使用 `Tools/ios/build-app.py` 脚本，支持模拟器和真机。 |
| **Android** | 使用Android NDK交叉编译，参见 `Doc/using/android.rst`。 |

对于大多数贡献（stdlib、文档、测试），你只需要在本机平台编译即可，CI会在所有平台上测试你的PR。

## 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| `./configure: error: no acceptable C compiler found` | 未安装C编译器 | Ubuntu: `sudo apt install build-essential`；macOS: `xcode-select --install`；Windows: 安装VS Studio |
| `ModuleNotFoundError: No module named '_ctypes'` | 缺少libffi-dev | Ubuntu: `sudo apt install libffi-dev`；macOS: `brew install libffi` 后设置 `PKG_CONFIG_PATH` |
| `WARNING: The Python readline extension was not compiled` | 缺少readline库 | Ubuntu: `sudo apt install libreadline6-dev` |
| 编译后找不到某些C扩展模块 | 缺少对应的开发库 | 查看编译输出中的WARNING信息，安装对应的-dev包后重新编译 |
| Windows上 `PCbuild\build.bat` 失败 | VS版本不对或缺少组件 | 安装VS 2017+并勾选Python development workload |
| WSL上编译错误 | Windows换行符问题 | 设置 `git config --global core.autocrlf input` 后重新clone |
| 测试有随机失败 | Flaky test（不稳定测试） | 可以re-run CI，如果与你的改动无关，在PR中说明 |
| `make` 很慢 | 未使用并行编译 | 加 `-j$(nproc)` 参数使用多核编译 |
| pre-commit hook失败 | 代码风格问题 | 查看错误信息，自动修复的问题直接 `git add` 后重新commit |
| 生成文件过期（如Python/Python-ast.c） | AST或语法文件变更 | 运行 `make regen-all`（Unix）或 `PCbuild\build.bat --regen`（Windows） |

---

## 下一步

👉 [02 - 深度开发流程：Git工作流、PR生命周期、版本管理与测试体系](02-development-workflow.md)
