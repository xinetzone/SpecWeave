---
id: tech-advisory-defaults-channel-abi-lock
date: 2026-08-14
type: technical-advisory
severity: high
status: active
applies_to:
  - "devcontainer-base:conda-libmamba-ft (v2.x)"
  - "all conda-forge free-threading (cp314t/cp313t) environments"
  - "variants/conda, variants/ai-dev"
related_pattern: "conda-abi-variant-safe-switching.md"
related_script: "scripts/verify-cext.sh"
---

# ⚠️ 技术警示：Anaconda defaults channel 导致 free-threading ABI 静默降级风险

**严重级别**：🔴 高（功能静默失效，无错误提示）
**影响范围**：所有使用 Python 3.13t/3.14t free-threading（无 GIL）构建的 Conda 环境
**首次发现**：2026-08-14（devcontainer-base v2.1 构建验证）

---

## 一、问题概述

在 `devcontainer-base:conda-libmamba-ft` (cp314t free-threading) 镜像中，如果用户或自动化脚本执行以下操作：

```bash
conda config --add channels defaults
# 或
conda install -c defaults <package>
```

Conda 求解器会**静默地**将 Python 从 `cp314t`（free-threading，GIL默认禁用）降级为 `cp314`（标准构建，GIL始终启用），**没有任何错误或警告**。

**后果**：free-threading 功能完全失效，多线程代码退化为 GIL 串行执行，但用户看到 `python --version` 仍然显示 3.14.6，误以为 free-threading 在工作。

---

## 二、根因分析

### 2.1 Channel ABI 不对称

| Channel | cp314（标准GIL构建） | cp314t（free-threading构建） |
|---------|---------------------|---------------------------|
| **conda-forge** | ✅ 提供 | ✅ 提供（完整生态适配中） |
| **defaults (Anaconda)** | ✅ 提供 | ❌ **不提供**（截至2026-08-14） |

defaults channel 仅提供标准 GIL 构建（cp314），不提供 free-threading 构建（cp314t）。

### 2.2 静默降级机制

当 conda-forge 和 defaults 两个 channel 共存且 channel_priority 不是 strict 时：

1. 用户执行 `conda install <some-anaconda-only-package>`
2. Conda 求解器发现 defaults 中的包依赖 `python >=3.14` 且标记为 `cp314`
3. 为满足依赖，求解器将当前环境的 Python 从 `python-3.14.6-h81e9b38_2_cp314t`（conda-forge）替换为 `python-3.14.6-xxxx_cp314`（defaults）
4. **所有已安装的 conda-forge cp314t 包被同步替换为 cp314 版本**（因为 SOABI 不兼容）
5. 整个过程没有任何警告，conda 只输出 "Solving environment: done"，然后列出将要安装/降级的包（大多数用户不会仔细看）

### 2.3 为什么这比"普通包冲突"更危险

- **静默失败**（Silent Failure）：不报错、不崩溃、不打印警告
- **功能退化而非不可用**：Python 仍然可以运行，所有代码正常执行，只是多线程不再加速
- **难以排查**：用户看到 `python --version` 输出3.14.6，完全正常；只有专门检查 SOABI 才能发现
- **影响核心价值主张**：free-threading 是 v2.x 镜像的核心特性，降级后镜像价值损失

---

## 三、快速自检（3秒确认你的环境是否安全）

在你的环境中执行以下命令：

```bash
python -c "import sysconfig; soabi=sysconfig.get_config_var('SOABI'); gil=sysconfig.get_config_var('Py_GIL_DISABLED'); print(f'SOABI: {soabi}'); print(f'GIL disabled: {gil}'); assert 'cpython-314t' in soabi and gil==1, 'ABI DOWNGRADE DETECTED'"
```

**正常输出**（安全）：
```
SOABI: cpython-314t-x86_64-linux-gnu
GIL disabled: 1
```

**危险输出**（已降级）：
```
SOABI: cpython-314-x86_64-linux-gnu
GIL disabled: 0
AssertionError: ABI DOWNGRADE DETECTED
```

**channels 检查**：
```bash
conda config --show channels
# 应该只有 conda-forge，不应该有 defaults
```

---

## 四、一键诊断脚本

镜像中已内置 `verify-cext.sh` 诊断脚本，自动检测 ABI 混用和 defaults channel 风险：

```bash
# 容器内执行（推荐）
docker exec <container-name> bash /usr/local/bin/verify-cext.sh

# 本地Conda环境
bash scripts/verify-cext.sh

# 指定Python路径
PYTHON=/path/to/python bash scripts/verify-cext.sh
```

输出中包含：
- C扩展加载验证（brotli/cffi/sqlite3/ssl/zlib/hashlib）
- SOABI一致性检查
- cp314/cp314t包混用扫描
- **defaults channel 检测（警告项第11条）**

---

## 五、预防措施（强制规范）

### 5.1 镜像构建时（Dockerfile）

v2.1+ Dockerfile Stage 7 已内置防御：

```dockerfile
# Step 7.1: 移除 defaults channel，设置 strict priority
RUN conda config --remove channels defaults 2>/dev/null || true && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda config --set solver libmamba

# Step 7.2: 验证SOABI和GIL状态（构建门禁）
RUN python -c "import sysconfig; assert sysconfig.get_config_var('Py_GIL_DISABLED')==1, 'GIL not disabled'" && \
    python -c "import sysconfig; assert 'cpython-314t' in sysconfig.get_config_var('SOABI'), 'SOABI mismatch'"

# Step 7.3: C扩展功能验证
RUN python -c "import brotli; d=b'test'; assert brotli.decompress(brotli.compress(d))==d" && \
    python -c "import cffi, sqlite3, ssl, zlib, hashlib; print('C extensions OK')"
```

### 5.2 用户使用规范

| 操作 | 安全 | 危险 |
|------|------|------|
| `conda install <package>` | ✅ 仅使用conda-forge | — |
| `conda install -c conda-forge <package>` | ✅ 显式指定conda-forge | — |
| `conda config --add channels conda-forge` | ✅ （但已默认存在） | — |
| `conda config --add channels defaults` | — | 🔴 **禁止** |
| `conda install -c defaults <package>` | — | 🔴 **禁止** |
| `pip install <package>` | ✅ pip不受channel影响 | — |
| `mamba install <package>` | ✅ 同conda规则 | — |

### 5.3 如果确实需要 Anaconda 特定包

**方案A（推荐）：创建独立环境**
```bash
conda create -n anaconda-stuff python=3.14
conda activate anaconda-stuff
conda config --add channels defaults  # 仅在这个环境中（注意：实际会写入全局.condarc）
conda install -c defaults <package>
# 在这个环境中工作，不影响 main 环境的 cp314t
```
⚠️ 注意：`conda config --add channels` 是全局操作，会影响所有环境。建议在独立环境中使用后立即移除。

**方案B（安全）：一次性安装不修改全局配置**
```bash
conda install --override-channels -c defaults <package>
# --override-channels 仅本次命令使用指定channel，不修改配置
# 注意：这仍可能导致当前环境降级，仅在确定包不依赖cp314时使用
```

**方案C（最安全）：寻找 conda-forge 替代品**
```bash
# 大多数包在conda-forge上都有
conda search -c conda-forge <package>
# 或使用pip安装
pip install <package>
```

### 5.4 环境降级后的恢复方法

如果发现环境已被降级：

```bash
# 方法1：重新安装Python（推荐）
conda install -c conda-forge python=3.14.6 free-threading=*=cp314t --force-reinstall

# 方法2：重建环境（最干净）
conda create -n main -c conda-forge python=3.14.6 free-threading libmambapy jupyterlab ipykernel brotli cffi pyyaml psutil
# 删除旧环境后重命名
conda remove -n main --all -y
conda rename -n main_new main  # 或直接激活新环境

# 方法3：重新构建镜像（容器场景）
docker build -t devcontainer-base:conda-libmamba-ft .
```

---

## 六、验证检查清单

- [ ] Dockerfile中已执行 `conda config --remove channels defaults` 和 `--set channel_priority strict`
- [ ] Dockerfile末尾有SOABI和GIL状态验证RUN命令
- [ ] build.sh预检检查必需脚本（verify-cext.sh）存在
- [ ] 冒烟测试包含free-threading性能验证（8线程加速≥3x）
- [ ] 镜像中部署了verify-cext.sh到/usr/local/bin/
- [ ] README/RELEASE文档中标注了defaults channel风险
- [ ] 团队成员已知悉此警示
- [ ] CI流水线运行verify-cext.sh作为构建门禁

---

## 七、相关资源

- 模式文档：[conda-abi-variant-safe-switching.md](../../../../.agents/docs/retrospective/patterns/code-patterns/conda-abi-variant-safe-switching.md)
- 验证脚本：[../scripts/verify-cext.sh](../scripts/verify-cext.sh)
- 基准脚本：[../scripts/ft-benchmark.sh](../scripts/ft-benchmark.sh)
- 发布说明：[RELEASE-v2.md](RELEASE-v2.md) §5已知问题#5
- 复盘报告：[retrospective-devcontainer-conda-libmamba-ft-v2.1-20260814](../../../../.agents/docs/retrospective/reports/build-engineering/retrospective-devcontainer-conda-libmamba-ft-v2.1-20260814/)
- PEP 703: https://peps.python.org/pep-0703/
- conda-forge free-threading: https://conda-forge.org/docs/user/knowledge/free-threading/

---

## 八、变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-08-14 | v1.0 | 初始发布：defaults channel ABI锁定风险，含自检方法、恢复方法和预防规范 |
