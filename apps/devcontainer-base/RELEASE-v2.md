# DevContainer Base - conda-libmamba-v2 发布说明 (Release Notes)

> 版本标签：`devcontainer-base:conda-libmamba-v2`
> 发布日期：2026-08-13
> 构建环境：WSL2 / Linux + Docker BuildKit
> 验证状态：✅ 8/8 深度验证通过 + 7/7 冒烟测试通过

---

## 1. 版本概述

`conda-libmamba-v2` 是 devcontainer-base 基础镜像的**重大架构升级版本**，核心变更包括：

- **Python 3.14.6**：Python生态最新版本，支持PEP 703无全局解释器锁（free-threading）实验性构建
- **libmamba求解器**：Conda默认求解器从经典solver切换为libmamba，依赖解析速度提升10-100倍
- **free-threading可选支持**：默认安装标准CPython构建(cp314)，可通过`conda create -n ft python=*=*_cp314t -c conda-forge`一键创建无GIL环境
- **环境统一**：移除 `/opt/venv` 虚拟环境，所有Python包/JupyterLab统一由Conda管理，消除路径歧义
- **激进瘦身**：9步清理策略（APT缓存/文档/静态库/调试符号/__pycache__/locale/遥测），最终镜像 **2.38GB**
- **构建可观测性**：构建计时器、日志持久化、预检机制、错误诊断信息
- **JupyterLab替代Notebook**：默认Jupyter界面升级为Lab
- **CI/CD流水线**：GitHub Actions三job架构（lint+build-main+push），支持自动推送到私有仓库

---

## 2. 版本矩阵

| 组件 | v1（旧版） | **v2（本版）** | 变更类型 |
|------|-----------|---------------|---------|
| **Python** | 3.13 (系统) / 3.x (venv) | **3.14.6** (conda-forge, GCC 14.4.0, 标准cp314构建) | ⬆️ 大版本升级 |
| **free-threading** | ❌ 不支持 | **✅ 可选**（`conda create -n ft python=*=*_cp314t`创建无GIL环境） | 🆕 新特性 |
| **Conda** | 24.x.x (Miniconda3) | **26.7.0** (Miniforge/mambaforge) | ⬆️ 大版本升级 |
| **Conda Solver** | classic solver | **libmamba 2.3.2**（默认） | 🔄 求解器切换 |
| **Conda Channels** | defaults + conda-forge | **conda-forge only** | 🧹 精简 |
| **Jupyter** | Notebook (venv) | **JupyterLab** (conda base env) | ⬆️ 升级 |
| **虚拟环境** | `/opt/venv`（253MB） | ❌ **已移除**，统一conda | 🧹 架构简化 |
| **镜像体积** | ~3.5GB（含venv+冗余） | **2.38GB** | 📉 ~32% 瘦身 |
| **构建日志** | 仅stdout | **tee持久化 + plain进度** | 🆕 可观测性 |
| **预检机制** | ❌ 无 | **6项预检** | 🆕 可靠性 |
| **冒烟测试** | ❌ 手动 | **7项自动验证** | 🆕 CI就绪 |
| **CI/CD流水线** | 5层链式构建 | **三job架构(lint+build+push)** | 🆕 自动推送 |
| **变体适配** | 旧路径(/opt/venv) | **已适配**(/opt/conda) | 🔧 路径更新 |
| **Ubuntu Base** | 26.04 | 26.04 | 无变更 |

---

## 3. 详细变更

### 3.1 🐍 Python 3.14 + free-threading（无GIL）可选支持

默认Python 3.14.6 来自 conda-forge，采用 GCC 14.4.0 编译，安装的是**标准CPython构建(cp314)**，GIL始终启用以保证最大兼容性。

**验证结果（默认环境）**：
```python
>>> import sys, sysconfig
>>> sys.version
'3.14.6 | packaged by conda-forge | (main, Aug 11 2026, 10:26:15) [GCC 14.4.0]'
>>> sysconfig.get_config_var('Py_GIL_DISABLED')
0                                          # 0=标准构建(GIL), 1=free-threading构建
>>> sys._is_gil_enabled()
True                                       # GIL启用（标准构建始终为True）
>>> # PEP 695 泛型语法支持
>>> type Point[T] = tuple[T, T]
>>> Point[int]
tuple[int, int]
```

**启用free-threading（无GIL）**：
通过conda创建独立的free-threading环境（cp314t构建）：
```bash
conda create -n ft python=*=*_cp314t -c conda-forge --solver libmamba -y
conda activate ft
# python3.14t 二进制默认GIL禁用，PYTHON_GIL=1可强制启用兼容模式
```

> **重要提示**：
> - 默认Python(cp314)是**标准构建**，设置`PYTHON_GIL=0`会报错"Disabling the GIL is not supported by this build"
> - Free-threading构建(cp314t)GIL**默认禁用**，设置`PYTHON_GIL=1`可强制启用GIL（兼容模式）
> - 正确检测free-threading构建的方式：`sysconfig.get_config_var('Py_GIL_DISABLED') == 1`，而非仅检查`hasattr(sys, '_is_gil_enabled')`（所有Python 3.14都有此函数）
> - 纯Python CPU密集型任务在无GIL模式下8线程可获得约**5x加速**（详见§4.4性能基准）
> - 含C扩展的包（NumPy等）需确认提供cp314t兼容build

### 3.2 ⚡ libmamba求解器

Conda默认求解器从经典solver切换到libmamba（C++实现），依赖解析速度提升显著：

**配置**：
```bash
$ conda config --show solver
solver: libmamba

$ conda list | grep libmamba
conda-libmamba-solver       26.7.0    pyha805d9d_0    conda-forge
libmambapy                  2.3.2     py314h18ff00b_1  conda-forge
```

**性能对比**（参考值，实际取决于网络和环境）：
| 操作 | classic solver | libmamba | 提升 |
|------|---------------|----------|------|
| 求解简单环境（10包） | 5-15s | <1s | 10-15x |
| 求解复杂环境（50+包） | 60-300s+ | 3-10s | 20-100x |
| 冲突检测 | 慢，容易hang | 快速给出冲突报告 | 质的飞跃 |

### 3.3 🧹 环境统一 & 激进清理

移除了原有的 `/opt/venv` 虚拟环境层（约253MB），所有Python包统一安装到conda base环境。执行了9步激进清理：

| # | 清理步骤 | 预计回收空间 |
|---|---------|------------|
| 1 | APT缓存清理（`apt-get clean` + lists） | ~100MB |
| 2 | 文档/man/info页（`/usr/share/doc`, `/usr/share/man`, `/usr/share/info`） | ~50MB |
| 3 | Python `__pycache__/` 和 `*.pyc` | ~20-50MB |
| 4 | 静态库 `.a`/`.la` 文件 | ~30-80MB |
| 5 | `strip --strip-unneeded` 二进制符号 | ~50-150MB |
| 6 | Conda遥测（`.updated-index`、`identity.txt`） | 微量 |
| 7 | Locale清理（仅保留C.UTF-8/en_US/zh_CN） | ~10-30MB |
| 8 | Conda包缓存（`conda clean -afy`） | ~500MB-1GB |
| 9 | 权限修复（chmod） | 0（安全修复） |

**清理后状态验证**：
- `/opt/venv` 目录：✅ 不存在
- `/usr/share/doc`：✅ 基本清理（保留copyright）
- `*.pyc` 文件：✅ 已清理
- `__pycache__/` 目录：✅ 已清理

### 3.4 🔧 构建脚本增强（build.sh）

构建脚本从简单的docker build扩展为完整的构建工具：

**新增功能**：
- **日志持久化**：构建日志自动保存到 `logs/builds/build-<timestamp>.log`，便于事后排查
- **构建前预检（6项）**：Docker状态/BuildKit/磁盘空间（≥10GB）/Dockerfile存在性/Miniconda缓存/构建参数
- **错误诊断**：trap ERR自动输出日志路径、最后50行日志、5条排障建议
- **多镜像源支持**：`--apt-mirror`/`--pip-mirror`/`--docker-mirror`/`--conda-mirror` 参数，支持 aliyun/tuna/official 三档切换
- **网络模式**：`--network-host` 使用主机网络，解决国内环境下载超时
- **自动冒烟测试**：`--test` 参数构建后自动启动容器，执行7项验证
- **私有仓库支持**：`-r/--registry` 参数配置推送前缀

**使用示例**：
```bash
# 国内环境：使用aliyun镜像 + 主机网络 + 自动测试
bash scripts/build.sh -t conda-libmamba-v2 \
  --apt-mirror aliyun --pip-mirror aliyun \
  --conda-mirror official --network-host --test

# 查看构建日志
cat logs/builds/build-<timestamp>.log
```

### 3.5 📝 构建元数据

镜像内 `/etc/devcontainer-build-info` 记录完整构建元数据：

```ini
BUILD_DATE=2026-08-13
BASE_IMAGE=ubuntu:26.04
PYTHON_VERSION=3.14.6
CONDA_VERSION=26.7.0
CONDA_SOLVER=libmamba
SERVICES=sshd,dockerd,podman,jupyter
DOCKER_DIND=enabled
PODMAN_ROOTLESS=enabled
```

---

## 4. 验证结果

### 4.1 冒烟测试（7/7 通过）

| # | 测试项 | 结果 |
|---|-------|------|
| 1 | Python版本正确（3.14.x） | ✅ |
| 2 | conda命令可用 | ✅ |
| 3 | libmamba solver配置正确 | ✅ |
| 4 | conda channels仅含conda-forge | ✅ |
| 5 | pip可正常安装包 | ✅ |
| 6 | 关键包导入（libmambapy等） | ✅ |
| 7 | conda create/solve可执行（30s超时） | ✅ |

### 4.2 深度验证（8/8 通过）

| # | 测试项 | 结果 |
|---|-------|------|
| 1 | 基础服务进程（supervisord/sshd） | ✅ |
| 2 | Python 3.14.6 + GCC 14.4.0编译信息 | ✅ |
| 3 | Conda 26.7.0版本 | ✅ |
| 4 | libmambapy成功导入（无ImportError） | ✅ |
| 5 | PEP 695 泛型语法`type Point[T] = tuple[T, T]` | ✅ |
| 6 | Python构建类型确认（cp314标准构建，Py_GIL_DISABLED=0） | ✅ |
| 7 | JupyterLab命令路径正确（/opt/conda/bin/jupyter） | ✅ |
| 8 | /opt/venv不存在（已移除） | ✅ |

### 4.3 镜像体积

```
REPOSITORY           TAG                 SIZE
devcontainer-base    conda-libmamba-v2   2.38GB
```

**体积分析**：
- Ubuntu 26.04基础层：~150MB
- APT系统包（SSH/Docker/Podman/编译工具等）：~800MB
- Miniconda3 + Python 3.14 + JupyterLab + 依赖：~1.2GB
- 清理后冗余：~230MB
- **总计**：2.38GB

> 注：对比旧版含venv的conda镜像（约3.5GB），瘦身32%。但v2额外集成了Python 3.14（比3.13大）、libmamba、JupyterLab（比Notebook大），实际纯瘦身效果更显著。

### 4.4 Free-Threading 性能基准测试

**测试环境**：容器内16核CPU，素数计算任务（统计0~2,000,000内素数，纯Python CPU密集型）

| Python构建 | GIL状态 | 单线程 | 8线程(threading) | 8进程(ProcessPool) |
|-----------|---------|--------|-----------------|-------------------|
| **cp314 (标准)** | 🔒 ON | 1.555s | 1.568s (**0.99x**) | 0.369s (**4.22x**) |
| **cp314t (free-threading)** | 🔓 OFF | 1.653s (+6.3%开销) | **0.332s (4.98x)** 🎉 | 0.429s (3.85x) |
| cp314t + PYTHON_GIL=1 | 🔒 ON | 1.653s | 1.671s (0.99x) | 0.466s (3.55x) |

**关键结论**：
- 🎉 **无GIL模式下8线程加速4.98x**，且多线程性能**超越多进程**(4.22x)——省去了进程间序列化/通信开销
- 标准GIL模式下多线程完全无效(0.99x)，符合预期
- Free-threading单线程有~6%性能开销（引用计数原子操作），但多线程加速收益远超此开销
- cp314t + PYTHON_GIL=1回退到串行行为，验证了GIL开关的有效性

---

## 5. 已知问题 & 限制

| # | 问题 | 影响范围 | 状态 | 规避方案 |
|---|------|---------|------|---------|
| 1 | **TUNA conda镜像连接失败**：清华TUNA的conda-forge镜像在构建时返回`CondaHTTPError: HTTP 000 CONNECTION FAILED` | 国内使用TUNA源构建时 | ⚠️ 环境相关 | 使用`--conda-mirror official`切换官方源，或使用`--network-host` |
| 2 | **Python 3.14 C扩展兼容性**：部分含C扩展的第三方包（如特定版本的PyTorch）可能尚未提供Python 3.14 wheel | 使用`conda install`安装包时 | ⚠️ 生态适配中 | conda-forge已对大部分包提供3.14 build；如遇问题可pin包版本或等待上游更新 |
| 3 | **free-threading构建(cp314t)C扩展兼容性**：cp314t无GIL环境中，非ft兼容的C扩展可能crash或不可用 | 使用cp314t无GIL环境时 | ⚠️ PEP 703实验性 | cp314t环境中安装包需确认提供cp314t/abi3兼容build；NumPy等主要包正在适配中；生产环境建议使用默认cp314 |
| 4 | **变体镜像Python 3.14兼容性**：onnx-pytorch/onnx-quantized变体依赖的PyTorch/ONNX Runtime可能尚未提供Python 3.14 wheel | 构建AI变体时 | ⚠️ 待上游适配 | CI中变体构建标记为experimental(continue-on-error)；等待PyTorch/ONNX提供3.14 wheel |
| 5 | **默认Python非free-threading构建**：镜像默认安装cp314（GIL始终启用），非cp314t（无GIL） | 期望默认无GIL的用户 | ℹ️ 设计决策 | 稳定性优先：标准构建兼容性最好；需free-threading时执行`conda create -n ft python=*=*_cp314t -c conda-forge` |
| 6 | **Podman用户提示**：容器内`podman info`显示`The cgroupv2 manager is set to systemd but there is no systemd user session available` | rootless podman使用 | ⚠️ 功能不影响 | podman命令仍可正常使用；若需彻底消除需在容器内启动user session |
| 7 | **conda solve容器内测试**：容器内执行`conda create --dry-run`需`--network=host`才能在30秒内完成 | 容器网络模式 | ⚠️ 环境相关 | 默认容器网络下conda solve可能较慢；生产使用不受影响 |

---

## 6. 快速开始

```bash
# 拉取/构建镜像
docker build -t devcontainer-base:conda-libmamba-v2 .

# 开发模式启动（DinD + SSH + JupyterLab）
docker run -d --privileged \
  -p 2222:22 -p 2375:2375 -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:conda-libmamba-v2

# 验证Python 3.14环境
docker exec -it <container> python -c "
import sys, sysconfig
print(f'Python: {sys.version}')
print(f'Build type: cp314t (free-threading)' if sysconfig.get_config_var('Py_GIL_DISABLED') else 'Build type: cp314 (standard, GIL always on)')
print(f'GIL enabled: {sys._is_gil_enabled()}')
"

# 创建free-threading环境（无GIL并行计算）
docker exec -it <container> conda create -n ft python=*=*_cp314t -c conda-forge --solver libmamba -y
docker exec -it <container> /opt/conda/envs/ft/bin/python -c "
import sys; print(f'Free-threading: GIL enabled={sys._is_gil_enabled()}')  # 应输出False
"

# 使用libmamba快速创建环境
docker exec -it <container> conda create -n test python=3.14 numpy -y

# 运行free-threading性能演示脚本
docker exec -it <container> python examples/free_threading_demo.py
```

---

## 7. 相关文档

- [README.md](README.md) - 镜像使用说明
- [scripts/build.sh](scripts/build.sh) - 构建脚本
- [scripts/deep-verify.py](scripts/deep-verify.py) - 深度验证脚本
- [.trae/specs/devcontainer-base-image-slim/spec.md](../../.trae/specs/devcontainer-base-image-slim/spec.md) - 瘦身项目Spec
- [examples/free_threading_demo.py](examples/free_threading_demo.py) - Free-threading并发性能演示脚本

---

## 8. 变更提交记录

| Commit | 说明 |
|--------|------|
| `ceec9c07` | feat(docker): 主Dockerfile集成Miniconda3+Python3.14+libmamba，9步激进清理，build.sh日志/预检/冒烟测试增强 |
| `5efd3eac` | docs: 更新README文档反映Python3.14+libmamba+JupyterLab新架构 |
| `62f4a809` | feat(devcontainer): conda-libmamba-v2发布 - CI流水线重构+发布说明+free-threading示例+变体适配 |
| (待提交) | fix: 修正free-threading检测逻辑(sysconfig)，更新RELEASE-v2.md性能基准数据，CI增加cp314t环境验证 |
