---
id: "docker-build-network-resilience"
title: "Docker构建网络容错模式"
type: process-pattern
date: 2026-07-18
maturity: L1 实验性
maturity_note: "单案例验证（XMNN Docker build 第2轮 ConnectionResetError），待第二个独立案例验证后升级 L2"
source: "../../reports/task-reports/retrospective-xmnn-runtime-repackaging-20260718/README.md#模式cdocker构建网络容错checklist"
related_patterns:
  - "../code-patterns/compiled-wheel-runtime-image-build.md"
  - "../code-patterns/python-implicit-dependency-detection.md"
  - "container-build-env-optimization.md"
tags: ["docker", "network", "resilience", "pip", "mirror", "retry", "build", "fallback"]
validation_count: 1
reuse_count: 0
---

# Docker构建网络容错模式

## 触发场景

- Docker 构建中网络不稳定导致 `pip install` 失败
- 构建时间因网络下载波动大（同一 Dockerfile 有时 5 分钟有时 30 分钟）
- 国内网络环境下使用国外 pip 镜像源
- 核心功能（本地 wheel）因非核心网络依赖安装失败而整体构建失败

**识别信号**：
- `ConnectionResetError` / `Connection timed out` / `ReadTimeoutError`
- 构建日志中 pip 下载进度条反复重试
- 同一 Dockerfile 多次构建结果不一致（有时成功有时失败）

**不适用场景**：
- 企业内部 CI/CD 有稳定网络和私有 PyPI 镜像
- 纯离线构建（所有依赖已 COPY 进镜像）
- 构建环境网络完全可控（如云厂商内部网络）

## 问题背景

### Docker 构建中的网络脆弱性

Docker 构建中的 `pip install` 依赖容器内网络访问外部 PyPI，面临三层风险：

1. **网络不稳定**：国内访问 pypi.org 延迟高、丢包率高
2. **Docker 网络层**：Docker 默认 bridge 网络的 DNS 解析和 NAT 转发增加额外延迟
3. **无增量缓存**：Docker build 每次都是全新容器，无法复用宿主机的 pip 缓存

### 核心矛盾

```
核心功能（本地 wheel）← 不受网络影响，但被网络依赖阻塞
非核心依赖（pip 下载）  ← 受网络影响，失败导致整体构建失败
```

传统做法是"先装本地 wheel，再装网络依赖"，但这样核心功能验证会在网络依赖之前，无法确保完整环境。

## 核心步骤（五步法）

### 步骤1：配置国内 pip 镜像源

```dockerfile
# 设置 pip 镜像源和重试参数
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_RETRIES=5
ENV PIP_DEFAULT_TIMEOUT=300
```

**为什么**：国内访问清华/阿里镜像源的速度是 pypi.org 的 10-50 倍。

### 步骤2：本地文件先于网络下载（利用 Docker cache）

```dockerfile
# 先 COPY 本地文件（利用 Docker layer cache，不受网络影响）
COPY xmnn-1.2.1+fix-cp314-cp314-linux_x86_64.whl /tmp/

# 再执行网络安装
RUN pip install pytest tomlkit pandas Pillow
```

**为什么**：`COPY` 指令不依赖网络，且利用 Docker layer cache——即使后续网络安装失败重试，本地文件层已缓存。

### 步骤3：非核心依赖容错安装

```dockerfile
# 核心依赖（必须成功）
RUN pip install pytest tomlkit pandas

# 非核心依赖（容错，失败不中断构建）
RUN pip install Pillow cloudpickle tornado || echo "[WARN] optional deps install failed"
```

**为什么**：非核心依赖缺失时核心功能仍可使用，不应因非核心依赖安装失败而中断整个构建。

### 步骤4：本地 wheel 在网络依赖之后安装

```dockerfile
# 1. 网络依赖（核心）
RUN pip install pytest tomlkit pandas

# 2. 网络依赖（非核心，容错）
RUN pip install Pillow cloudpickle tornado || echo "[WARN]"

# 3. 本地 wheel（不受网络影响，确保核心功能可用）
RUN pip install /tmp/xmnn-1.2.1+fix-cp314-cp314-linux_x86_64.whl
```

**为什么**：先确保网络依赖安装，再装本地 wheel。如果先装本地 wheel 再装网络依赖失败，wheel 已安装但环境不完整，验证可能误判为成功。

### 步骤5：核心验证在非核心依赖之后执行

```dockerfile
# 1-4. 安装所有依赖（核心+非核心+本地wheel）

# 5. 验证核心功能（在所有依赖安装之后）
RUN python -c "import tvm; import xmnn; from xmnn import compile_api; print('OK')"
```

**为什么**：核心功能验证应覆盖所有 import 路径（见 python-implicit-dependency-detection.md），必须在所有依赖安装之后执行。

## 网络容错 Checklist

- [ ] 设置 `PIP_INDEX_URL` 为国内镜像源
- [ ] 设置 `PIP_RETRIES=5` 增加重试次数
- [ ] 设置 `PIP_DEFAULT_TIMEOUT=300` 增加超时时间
- [ ] 本地 `COPY` 文件先于网络下载（利用 Docker cache）
- [ ] 非核心依赖安装使用 `|| echo "[WARN]"` 容错
- [ ] 核心验证在非核心依赖之后执行
- [ ] 使用 `--no-cache-dir` 避免镜像体积膨胀（但会失去 pip 层缓存）
- [ ] 考虑使用 `--mount=type=cache` 复用 pip 缓存（BuildKit）

## 适用条件

- ✅ Docker 构建中 `pip install` 依赖网络下载
- ✅ 网络不稳定导致构建失败率高
- ✅ 有本地 wheel/文件不受网络影响
- ✅ 需要区分核心依赖和非核心依赖

## 反模式（不要这么做）

### ❌ 反模式1：核心依赖和非核心依赖不区分

- **错误**：`RUN pip install pytest tomlkit pandas Pillow tornado` 一条命令装所有
- **后果**：Pillow 安装失败导致 pytest/tomlkit/pandas 也不可用，核心功能被阻塞
- **正确做法**：核心依赖和非核心依赖分步安装，非核心依赖使用 `|| echo "[WARN]"` 容错

### ❌ 反模式2：先装本地 wheel 再装网络依赖

- **错误**：先 `pip install /tmp/xxx.whl`，再 `pip install pytest tomlkit`
- **后果**：网络依赖安装失败时，wheel 已安装但环境不完整，验证可能因惰性 import 误判为成功
- **正确做法**：先装网络依赖（核心+非核心），再装本地 wheel

### ❌ 反模式3：不设置 pip 镜像源和重试参数

- **错误**：使用默认 pypi.org，不设置 `PIP_RETRIES` 和 `PIP_DEFAULT_TIMEOUT`
- **后果**：网络不稳定时 pip 快速失败，构建中断
- **正确做法**：设置国内镜像源 + `PIP_RETRIES=5` + `PIP_DEFAULT_TIMEOUT=300`

### ❌ 反模式4：用 `--no-cache-dir` 但不设置 `--mount=type=cache`

- **错误**：为了减小镜像体积使用 `--no-cache-dir`，但每次构建都重新下载所有包
- **后果**：构建时间长，网络不稳定时更容易失败
- **正确做法**：如果使用 BuildKit，用 `--mount=type=cache,target=/root/.cache/pip` 复用缓存；否则接受缓存层增加的体积

### ❌ 反模式5：非核心依赖失败直接中断构建

- **错误**：`RUN pip install Pillow tornado` 失败时 Docker build 中断
- **后果**：因非核心依赖（如图像处理库）失败导致整个镜像构建失败，核心功能无法使用
- **正确做法**：非核心依赖使用 `|| echo "[WARN]"` 容错，构建继续，核心功能验证时再检查

## 检验标准

做完之后怎么知道做对了？

- [ ] 标准1：`PIP_INDEX_URL`、`PIP_RETRIES`、`PIP_DEFAULT_TIMEOUT` 已设置
- [ ] 标准2：本地 `COPY` 指令在网络 `pip install` 之前
- [ ] 标准3：非核心依赖安装使用 `|| echo "[WARN]"` 容错
- [ ] 标准4：本地 wheel 在网络依赖之后安装
- [ ] 标准5：核心功能验证在所有依赖安装之后执行
- [ ] 标准6：模拟网络中断（`--network=none`）时，核心功能仍可安装和验证

## 迁移示例

这个模式还能用在什么场景？

### 场景1：XMNN Docker build（本项目，源案例）

- **网络问题**：第2轮 build 因 `ConnectionResetError` 失败
- **核心依赖**：pytest、tomlkit、pandas（tvm/xmnn 运行必需）
- **非核心依赖**：Pillow、tornado（图像处理/RPC，非必需）
- **本地 wheel**：xmnn-1.2.1+fix-cp314-cp314-linux_x86_64.whl（121MB）
- **结果**：✅ 分层安装 + 容错策略后构建稳定

### 场景2：ML 模型服务镜像构建（推断，待验证）

- **网络问题**：下载 PyTorch/TensorFlow 大包超时
- **核心依赖**：torch/tensorflow（从本地 wheel 安装）
- **非核心依赖**：matplotlib、jupyter（可视化/交互，非必需）
- **验证方法**：模拟网络中断，验证模型推理功能

### 场景3：Node.js 项目 Docker 构建（跨领域推断）

- **类似问题**：`npm install` 从 npmjs.org 下载超时
- **对应策略**：设置 `npm_config_registry` 为淘宝镜像 + `npm_config_fetch_retries`
- **差异**：Node.js 的 `package-lock.json` 更严格，但 devDependencies 可容错

### 场景4：Rust 项目 Docker 构建（跨领域推断）

- **类似问题**：`cargo build` 从 crates.io 下载超时
- **对应策略**：配置 `~/.cargo/config.toml` 使用国内镜像 + `CARGO_NET_RETRY`
- **差异**：Rust 的 `Cargo.lock` 类似 `package-lock.json`，但 vendor 策略不同

## 待验证问题（升级 L2 需确认）

1. **BuildKit cache mount**：`--mount=type=cache,target=/root/.cache/pip` 在实际项目中的缓存命中率如何？
2. **多阶段构建**：builder 阶段装依赖，runtime 阶段只复制 wheel，是否能完全避免网络问题？
3. **私有 PyPI**：企业内部 PyPI 镜像是否比公共镜像更稳定？
4. **网络模拟测试**：如何在 CI 中模拟网络不稳定，验证容错策略有效性？

## 与相关模式的关系

- **[container-build-env-optimization.md](container-build-env-optimization.md)**：该模式关注构建环境整体优化（镜像源、重试、命令拆分），本模式专注于网络容错策略（本地优先+网络可选）。两者互补：该模式是"预防"，本模式是"容错"
- **[compiled-wheel-runtime-image-build.md](../code-patterns/compiled-wheel-runtime-image-build.md)**：该模式步骤3（安装依赖）使用本模式的网络容错策略
- **[python-implicit-dependency-detection.md](../code-patterns/python-implicit-dependency-detection.md)**：隐式依赖安装时的网络容错使用本模式
- **[dev-env-dockerfile-optimization.md](../methodology-patterns/governance-strategy/dev-env-dockerfile-optimization.md)**：该模式关注开发环境 Dockerfile 优化，本模式关注网络容错，两者在"按变化频率排序"和"本地文件先于网络下载"上有交集

## Changelog

- **2026-07-18** (v1.0.0): 初始版本，从 XMNN Runtime 1.2.1-fix-cp314 重新打包复盘萃取，单案例验证（Docker build 第2轮 ConnectionResetError），标记 L1 实验性
