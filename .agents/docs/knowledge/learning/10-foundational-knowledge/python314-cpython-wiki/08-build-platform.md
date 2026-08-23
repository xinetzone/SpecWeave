---
id: "python314-cpython-wiki-08"
title: "Python 3.14 构建系统与平台支持"
source: "https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html#build-changes"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/10-foundational-knowledge/python314-cpython-wiki/08-build-platform.toml"
---

# Python 3.14 构建系统与平台支持

本章介绍 Python 3.14 的构建选项变更、官方二进制新特性、平台支持扩展和签名机制变化。

---

## 1. 构建选项变更

### 新的配置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--disable-gil` | 构建自由线程版本（无 GIL） | 关闭（标准构建） |
| `--with-tail-call-interp` | 使用尾调用解释器 | 关闭 |
| `--enable-experimental-jit` | 启用 Copy-and-Patch JIT | macOS/Windows 官方二进制开启 |
| `--without-remote-debug` | 禁用 PEP 768 远程调试接口 | 开启（远程调试可用） |

### 安全编译器选项默认启用

Python 3.14 在编译器支持时默认启用以下安全选项：
- `-fstack-protector-strong`：栈保护
- `-D_FORTIFY_SOURCE=2`：缓冲区溢出检测
- `-Wl,-z,relro,-z,now`：重定位表只读（RELRO）
- Control Flow Integrity（CFI）如果编译器支持

### WITH_FREELISTS 移除

Python 3.14 移除了 `WITH_FREELISTS` 编译选项和相关的自由列表（free-lists）优化。自由列表之前用于加速小对象（float、list、dict 等）的分配/释放。移除原因：
- 与 mimalloc（自由线程模式默认分配器）功能重复
- 简化内存管理代码
- mimalloc 已提供类似或更好的性能

### Autoconf 2.72 要求

从源码构建 Python 3.14 需要 Autoconf 2.72 或更高版本（如果需要重新生成 configure 脚本）。

### 构建示例

```bash
# 标准发布构建（类似官方二进制）
./configure --enable-optimizations --with-lto

# 自由线程 + JIT + 尾调用（性能最优的开发构建）
./configure --disable-gil --enable-experimental-jit --with-tail-call-interp --enable-optimizations

# 调试构建
./configure --with-pydebug --without-pymalloc

make -j$(nproc)
make test  # 运行测试
sudo make install
```

---

## 2. 官方二进制新特性

### macOS/Windows 包含实验性 JIT

Python 3.14 官方 macOS 和 Windows 安装包**包含实验性 JIT 编译器**，不需要从源码构建：

```bash
# macOS/Windows 上直接使用
PYTHON_JIT=1 python3.14 your_script.py
```

Linux 官方构建（python.org 下载）也包含 JIT 支持，但各 Linux 发行版的包可能不同。

### Android 官方二进制

Python 3.14 首次提供 Android 平台的官方二进制构建：
- ARM64-v8a 架构
- 可用于 Android 应用内嵌 Python
- 支持通过 Chaquopy 或类似框架使用

### Emscripten Tier 3 支持（PEP 776）

[PEP 776](https://peps.python.org/pep-0776/) 将 Emscripten（WebAssembly/WASI）提升为 Tier 3 支持平台：

| Tier | 含义 | Emscripten 状态 |
|------|------|----------------|
| Tier 1 | 官方完全支持，每个 PR 都测试 | Linux/macOS/Windows |
| Tier 2 | 官方支持，定期构建 | 更多 Unix 平台、某些架构 |
| Tier 3 | 社区支持，构建可用但不保证测试通过 | **Emscripten (3.14 新增)** |

```bash
# Web 浏览器中运行 Python（通过 Pyodide 等项目）
# Python 3.14 为 Emscripten 提供更好的官方支持
```

---

## 3. PEP 739：build-details.json

PEP 739 引入了 `build-details.json` 文件，包含 Python 构建的完整配置信息：

```bash
# 查看构建信息
python3.14 -m sysconfig --build-details
# 或
import json, sysconfig
with open(sysconfig.get_config_var('BUILD_DETAILS')) as f:
    details = json.load(f)
```

build-details.json 包含：
- Python 版本和 ABI 信息
- 编译器标志和选项
- 构建配置（自由线程/JIT/尾调用等）
- 平台信息
- 启用/禁用的模块列表

### 用途

- 构建系统检测 Python 配置（是否为自由线程版本、JIT 是否可用等）
- C 扩展构建时的配置匹配
- 诊断环境问题

---

## 4. PEP 761：Sigstore 替代 PGP 签名

### 变更

从 Python 3.14 开始，CPython 发布版本不再使用 PGP 签名验证，改用 **Sigstore**：

| 方面 | 旧方式（PGP） | 新方式（Sigstore） |
|------|--------------|-------------------|
| 签名格式 | `.asc` 文件 | Sigstore bundle（`.sigstore`） |
| 密钥分发 | 需要信任公钥网络 | 基于证书透明性和 OIDC |
| 验证工具 | gpg | `sigstore` CLI 或 Python 库 |

### 验证下载

```bash
# 旧方式
gpg --verify Python-3.14.0.tgz.asc Python-3.14.0.tgz

# 新方式
pip install sigstore
sigstore verify identity Python-3.14.0.tgz \
    --cert-identity pablogsal@python.org \
    --cert-oidc-issuer https://accounts.google.com
```

---

## 5. 平台支持变化

### FreeBSD 平台名简化

FreeBSD 构建的平台标识简化，不再包含版本号在 platform string 中。

### Windows C99 实数/复数运算

Windows 构建现在正确使用 C99 标准的实数和复数运算，不再使用 MSVC 特有的模拟实现。这改善了复数运算在 Windows 上的正确性和性能。

### iOS/macOS stdout/stderr 重定向

iOS 和 macOS 上 stdout/stderr 的重定向行为得到修复，在 GUI 应用中捕获 Python 输出更可靠。

---

## 6. 自由线程构建命名约定

| 构建类型 | Unix 可执行文件 | Windows | pkg-config |
|---------|---------------|---------|------------|
| 标准构建 | `python3.14` | `python.exe` | `python-3.14` |
| 自由线程构建 | `python3.14t` | `pythont.exe` | `python-3.14t` |
| 调试构建 | `python3.14d` | `pythond.exe` | `python-3.14d` |
| 自由线程+调试 | `python3.14td` | `pythontd.exe` | `python-3.14td` |

ABI 标签中，自由线程构建使用 `t` 后缀：
- 标准：`cpython-314-x86_64-linux-gnu`
- 自由线程：`cpython-314t-x86_64-linux-gnu`

```python
import sysconfig
print(sysconfig.get_config_var('EXT_SUFFIX'))
# 标准: '.cpython-314-x86_64-linux-gnu.so'
# 自由线程: '.cpython-314t-x86_64-linux-gnu.so'
```

---

- [上一章：C API 与扩展开发](07-c-api-changes.md) ←
- [下一章：迁移指南](09-migration-guide.md) →
