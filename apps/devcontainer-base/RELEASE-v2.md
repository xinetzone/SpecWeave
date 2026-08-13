# DevContainer Base - conda-libmamba-ft 发布说明 (Release Notes)

> 版本标签：`devcontainer-base:conda-libmamba-ft` (v2.1)
> 发布日期：2026-08-13
> 构建环境：WSL2 / Linux + Docker BuildKit
> 验证状态：✅ **构建验证通过**（2026-08-14，镜像 `devcontainer-base:conda-libmamba-ft`，2.5GB）

---

## 1. 版本概述

`conda-libmamba-ft` 是 devcontainer-base 基础镜像的**free-threading默认版本**，核心变更包括：

- **Python 3.14.6 free-threading (cp314t)**：默认安装Python 3.14.6无GIL构建（cp314t），GIL默认禁用，支持真正的多线程并行；可通过`PYTHON_GIL=1`环境变量强制启用GIL兼容模式
- **Miniforge3替代Miniconda3**：从Anaconda Miniconda3迁移到conda-forge官方Miniforge3发行版，彻底解决defaults channel包与cp314t ABI冲突问题（conda-anaconda-tos/anaconda-channel-guide等包绑定cp314导致无法安装cp314t），原生支持conda-forge + libmamba
- **libmamba求解器**：Conda默认求解器预装libmamba，依赖解析速度提升10-100倍
- **GIL可选控制**：no-gil为默认行为，标准GIL模式（cp314构建）可通过构建参数`--python-build cp314`选择
- **环境统一**：移除 `/opt/venv` 虚拟环境，所有Python包/JupyterLab统一由Conda管理，消除路径歧义
- **激进瘦身**：9步清理策略（APT缓存/文档/静态库/调试符号/__pycache__/locale/遥测）
- **构建可观测性**：构建计时器、日志持久化、预检机制、错误诊断信息
- **JupyterLab替代Notebook**：默认Jupyter界面升级为Lab
- **CI/CD流水线**：GitHub Actions三job架构（lint+build-main+push），支持自动推送到私有仓库

---

## 2. 版本矩阵

| 组件 | v1（旧版） | **v2.1（本版）** | 变更类型 |
|------|-----------|---------------|---------|
| **Python** | 3.13 (系统) / 3.x (venv) | **3.14.6** (conda-forge, GCC 14.4.0编译, libgcc 16.1.0运行时, **free-threading cp314t构建**) | ⬆️ 大版本升级 |
| **GIL默认状态** | 始终启用 | **默认禁用**（PYTHON_GIL=1可启用GIL兼容模式） | 🔄 并发模型切换 |
| **标准GIL构建可选** | ❌ 唯一选择 | **✅ 可选**（构建时`--python-build cp314`选择标准构建） | 🆕 构建选项 |
| **Conda发行版** | 24.x.x (Miniconda3, defaults channel) | **Miniforge3** (conda-forge官方，无defaults包，原生libmamba) | 🔄 发行版切换 |
| **Conda Solver** | classic solver | **libmamba**（默认预装） | 🔄 求解器切换 |
| **Conda Channels** | defaults + conda-forge | **conda-forge only** | 🧹 精简 |
| **Jupyter** | Notebook (venv) | **JupyterLab** (conda main环境, free-threading kernel) | ⬆️ 升级 |
| **虚拟环境** | `/opt/venv`（253MB） | ❌ **已移除**，统一conda（main环境为默认Python） | 🧹 架构简化 |
| **镜像体积** | ~3.5GB（含venv+冗余） | **2.5GB**（验证值） | 📉 瘦身29% |
| **构建日志** | 仅stdout | **tee持久化 + plain进度** | 🆕 可观测性 |
| **预检机制** | ❌ 无 | **6项预检** | 🆕 可靠性 |
| **冒烟测试** | ❌ 手动 | **8项自动验证**（含free-threading检测） | 🆕 CI就绪 |
| **CI/CD流水线** | 5层链式构建 | **三job架构(lint+build+push)** | 🆕 自动推送 |
| **变体适配** | 旧路径(/opt/venv) | **已适配**(/opt/conda) | 🔧 路径更新 |
| **Ubuntu Base** | 26.04 | 26.04 | 无变更 |

---

## 3. 详细变更

### 3.1 🐍 Python 3.14.6 free-threading（无GIL）默认启用

默认Python 3.14.6 来自 conda-forge，采用 GCC 14.4.0 编译（conda-forge 构建工具链），运行时链接 libgcc 16.1.0，安装的是**free-threading构建(cp314t)**，GIL**默认禁用**，支持真正的多线程并行计算。

**验证结果（默认环境）**：
```python
>>> import sys, sysconfig
>>> sys.version
'3.14.6 free-threading build | packaged by conda-forge | (main, Aug 11 2026, 10:27:17) [GCC 14.4.0]'
>>> sysconfig.get_config_var('Py_GIL_DISABLED')
1                                          # 1=free-threading构建, 0=标准构建
>>> sysconfig.get_config_var('SOABI')
'cpython-314t-x86_64-linux-gnu'           # t后缀表示free-threading构建
>>> sys._is_gil_enabled()
False                                      # GIL默认禁用
>>> # 启用GIL兼容模式
>>> # $ PYTHON_GIL=1 python
>>> # sys._is_gil_enabled() → True
>>> # PEP 695 泛型语法支持
>>> type Point[T] = tuple[T, T]
>>> Point[int]
tuple[int, int]
```

**GIL控制方式**：
- **默认模式**：cp314t构建，GIL禁用，支持真正多线程并行
- **GIL启用模式**：设置环境变量 `PYTHON_GIL=1` 启动Python，强制启用GIL以获得最大C扩展兼容性
```bash
# 默认无GIL模式
python your_script.py

# GIL兼容模式（遇到C扩展问题时使用）
PYTHON_GIL=1 python your_script.py
```

**选择标准GIL构建（cp314）**：
如需构建使用标准CPython（GIL始终启用）的镜像，使用构建参数：
```bash
./scripts/build.sh --python-build cp314 --tag conda-libmamba-std
```

> **重要提示**：
> - 默认Python(cp314t)是**free-threading构建**，GIL默认禁用；设置`PYTHON_GIL=1`可启用兼容模式
> - 标准构建(cp314)GIL**始终启用**，设置`PYTHON_GIL=0`会报错"Disabling the GIL is not supported by this build"
> - 正确检测free-threading构建的方式：`sysconfig.get_config_var('Py_GIL_DISABLED') == 1`，而非仅检查`hasattr(sys, '_is_gil_enabled')`（所有Python 3.14都有此函数）
> - 纯Python CPU密集型任务在无GIL模式下8线程可获得约**5x加速**（详见§4.4性能基准）
> - 含C扩展的包（NumPy等）需确认提供cp314t兼容build；遇到问题时使用`PYTHON_GIL=1`回退到兼容模式

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

移除了原有的 `/opt/venv` 虚拟环境层（约253MB），所有Python包统一安装到conda `main` 环境（独立于conda base环境，避免conda自身依赖冲突）。执行了9步激进清理：

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
- **构建前预检（6项）**：Docker状态/BuildKit/磁盘空间（≥10GB）/Dockerfile存在性/Miniforge缓存/构建参数
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
BUILD_DATE=2026-08-13T16:01:21Z
BASE_IMAGE=ubuntu:26.04
PYTHON_VERSION=3.14.6
PYTHON_BUILD_TYPE=free-threading
CONDA_VERSION=26.3.2
CONDA_SOLVER=libmamba
SERVICES=sshd,dockerd,podman,jupyter
DOCKER_DIND=enabled
PODMAN_ROOTLESS=enabled
DOCKER_VERSION=29.7.2
PODMAN_VERSION=5.7.0
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
| 2 | Python 3.14.6 + GCC 14.4.0编译信息(cp314t free-threading) | ✅ |
| 3 | Conda 26.3.2版本(Miniforge3) | ✅ |
| 4 | libmambapy成功导入（base环境） | ✅ |
| 5 | PEP 695 泛型语法`type Point[T] = tuple[T, T]` | ✅ |
| 6 | Python构建类型确认（cp314t free-threading，Py_GIL_DISABLED=1） | ✅ |
| 7 | JupyterLab命令路径正确（/opt/conda/envs/main/bin/jupyter，free-threading kernel） | ✅ |
| 8 | /opt/venv不存在（已移除） | ✅ |

### 4.3 镜像体积

```
REPOSITORY           TAG                 SIZE
devcontainer-base    conda-libmamba-ft   2.5GB
```

**体积分析**：
- Ubuntu 26.04基础层：~150MB
- APT系统包（SSH/Docker CE/Podman/基础工具）：~800MB
- Miniforge3 + Python 3.14.6 cp314t + JupyterLab + 依赖（main环境）：~1.3GB
- Conda base环境（conda运行时Python 3.13）：~250MB
- 清理后冗余：~0MB
- **总计**：2.5GB

> 注：对比旧版含venv的conda镜像（约3.5GB），瘦身29%。v2.1集成了Docker CE 29.7.2、Podman 5.7.0、Python 3.14 cp314t、JupyterLab、libmamba等完整开发工具链。

### 4.4 Free-Threading 性能基准测试

**测试环境A（大规模）**：容器内16核CPU，素数计算任务（统计0~2,000,000内素数，纯Python CPU密集型）

| Python构建 | GIL状态 | 单线程 | 8线程(threading) | 8进程(ProcessPool) |
|-----------|---------|--------|-----------------|-------------------|
| **cp314 (标准)** | 🔒 ON | 1.555s | 1.568s (**0.99x**) | 0.369s (**4.22x**) |
| **cp314t (free-threading)** | 🔓 OFF | 1.653s (+6.3%开销) | **0.332s (4.98x)** 🎉 | 0.429s (3.85x) |
| cp314t + PYTHON_GIL=1 | 🔒 ON | 1.653s | 1.671s (0.99x) | 0.466s (3.55x) |

**测试环境B（小规模smoke test，2026-08-14构建验证）**：16核WSL2，统计0~200,000内素数

| 并行模式 | 2线程 | 4线程 | 8线程 |
|---------|-------|-------|-------|
| threading.Thread | 1.60x | 2.91x | **4.29x** 🎉 |
| ThreadPoolExecutor | 1.57x | 2.90x | **4.37x** |
| ProcessPoolExecutor | 0.46x | 0.59x | 0.56x |

**关键结论**：
- 🎉 **无GIL模式下8线程加速4.29-4.98x**，且多线程性能**超越多进程**(4.22x)——省去了进程间序列化/通信开销
- 标准GIL模式下多线程完全无效(0.99x)，符合预期
- Free-threading单线程有~6%性能开销（引用计数原子操作），但多线程加速收益远超此开销
- cp314t + PYTHON_GIL=1回退到串行行为，验证了GIL开关的有效性
- ProcessPool在小规模测试中反而更慢（进程创建开销占主导），说明free-threading在细粒度并行场景优势明显

---

## 5. 已知问题 & 限制

| # | 问题 | 影响范围 | 状态 | 规避方案 |
|---|------|---------|------|---------|
| 1 | **国内网络下载Miniforge/conda包较慢**：GitHub Release和conda-forge官方源在国内访问不稳定 | 国内构建环境 | ⚠️ 环境相关 | 使用`--network-host`+`--conda-mirror tuna`配置TUNA镜像；或提前下载Miniforge3安装器到`.cache/`目录 |
| 2 | **Python 3.14 C扩展兼容性**：部分含C扩展的第三方包（如特定版本的PyTorch）可能尚未提供Python 3.14 wheel | 使用`conda install`安装包时 | ⚠️ 生态适配中 | conda-forge已对大部分包提供3.14 build；如遇问题可pin包版本或等待上游更新 |
| 3 | **free-threading构建(cp314t)C扩展兼容性**：cp314t无GIL环境中，非ft兼容的C扩展会自动启用GIL加载（不crash），影响多线程并行效率 | 使用cp314t无GIL环境时 | ⚠️ PEP 703实验性 | 默认cp314t环境中conda-forge包已基本适配；NumPy/pandas等主要包提供cp314t build；部分包（如`_brotli`）加载时会打印GIL启用警告（非fatal）；如遇C扩展兼容问题，可`PYTHON_GIL=1`启用GIL兼容模式，或构建时`--python-build cp314`选择标准构建 |
| 4 | **变体镜像Python 3.14兼容性**：onnx-pytorch/onnx-quantized变体依赖的PyTorch/ONNX Runtime可能尚未提供Python 3.14 wheel | 构建AI变体时 | ⚠️ 待上游适配 | CI中变体构建标记为experimental(continue-on-error)；等待PyTorch/ONNX提供3.14 wheel |
| 5 | **Miniforge3替代Miniconda3**：从Miniconda3(defaults channel)迁移到Miniforge3(conda-forge only)，不再包含Anaconda商业包(conda-anaconda-tos等) | 依赖defaults channel包的用户 | ℹ️ 设计变更 | Miniforge3使用纯conda-forge源，无ABI冲突；如需Anaconda特定包需手动添加defaults channel（不推荐，会引发cp314/cp314t ABI冲突） |
| 6 | **Podman用户提示**：容器内`podman info`显示`The cgroupv2 manager is set to systemd but there is no systemd user session available` | rootless podman使用 | ⚠️ 功能不影响 | podman命令仍可正常使用；若需彻底消除需在容器内启动user session |
| 7 | **双Python环境架构**：conda base环境保留Python 3.13（conda运行时自身依赖），用户默认使用`main`环境Python 3.14.6 cp314t | PATH配置/调试时 | ℹ️ 设计决策 | `/opt/conda/envs/main/bin`在PATH中优先级高于`/opt/conda/bin`，默认`python`即为3.14 cp314t；Jupyter kernel已注册为main环境 |
| 8 | **slim镜像不含编译工具链**：运行时镜像未安装gcc/g++/build-essential/binutils，如需编译C扩展需自行安装 | 容器内pip install编译C扩展 | ℹ️ 瘦身设计 | slim镜像定位为运行时环境；开发镜像可通过`apt-get install build-essential`安装编译工具 |
| 9 | **Docker DinD需要--privileged**：容器内Docker daemon需要特权模式才能正常运行 | 使用Docker-in-Docker时 | ℹ️ Docker限制 | 启动容器时添加`--privileged`标志；非DinD场景不受影响 |

---

## 6. 快速开始

```bash
# 构建镜像（国内网络推荐配置）
bash scripts/build.sh -t conda-libmamba-ft \
  --apt-mirror aliyun --pip-mirror aliyun \
  --conda-mirror official --network-host --test

# 开发模式启动（DinD + SSH + JupyterLab）
docker run -d --privileged \
  -p 2222:22 -p 2375:2375 -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:conda-libmamba-ft

# 验证Python 3.14 free-threading环境
docker exec -it <container> python -c "
import sys, sysconfig
print(f'Python: {sys.version}')
print(f'Build type: cp314t (free-threading)' if sysconfig.get_config_var('Py_GIL_DISABLED') else 'Build type: cp314 (standard, GIL always on)')
print(f'SOABI: {sysconfig.get_config_var(\"SOABI\")}')
"

# 运行free-threading性能演示脚本（容器内）
python /examples/free_threading_demo.py
# 或指定测试规模
BENCHMARK_RANGE=200000 python /examples/free_threading_demo.py
```

---

## 7. 相关文档

- [README.md](README.md) - 镜像使用说明
- [scripts/build.sh](scripts/build.sh) - 构建脚本
- [scripts/deep-verify.py](scripts/deep-verify.py) - 深度验证脚本
- [.trae/specs/devcontainer-base-image-slim/spec.md](../../.trae/specs/devcontainer-base-image-slim/spec.md) - 瘦身项目Spec
- [examples/free_threading_demo.py](examples/free_threading_demo.py) - Free-threading并发性能演示脚本

---

## 8. 构建计时（2026-08-13构建验证）

| Stage | 耗时 | 累计 |
|-------|------|------|
| Stage 1/7 (system+locale) | 3043s | 3043s |
| Stage 2/7 (Docker CE) | 1413s | 4456s |
| Stage 3/7 (Podman) | 525s | 4981s |
| Stage 4/7 (conda+libmamba+jupyter) | 177s | 5158s |
| Stage 5/7 (user+dirs+daemon) | 0s | 5159s |
| Stage 6/7 (config+validation) | 0s | 5160s |
| Stage 7/7 (cleanup+build-info) | 129s | ~5289s (~88min) |

---

## 9. 变更提交记录

| Commit | 说明 |
|--------|------|
| `ceec9c07` | feat(docker): 主Dockerfile集成Miniconda3+Python3.14+libmamba，9步激进清理，build.sh日志/预检/冒烟测试增强 |
| `5efd3eac` | docs: 更新README文档反映Python3.14+libmamba+JupyterLab新架构 |
| `62f4a809` | feat(devcontainer): conda-libmamba-v2发布 - CI流水线重构+发布说明+free-threading示例+变体适配 |
| (待提交) | fix: Miniforge3替代Miniconda3，双环境架构(base py313/main py314.6 cp314t)，修复TUNA conda镜像URL，Jupyter kernel注册free-threading环境，build.sh集成demo自动验证，RELEASE-v2.md更新为实际验证数据 |
