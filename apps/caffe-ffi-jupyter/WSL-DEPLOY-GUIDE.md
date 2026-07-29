# Caffe-FFI WSL 环境部署指南

> 本文档提供从基础镜像构建到最终 Python 导入验证的完整 WSL 部署流程，以及常见报错的快速定位与修复方案。

---

## 目录

1. [前置条件](#1-前置条件)
2. [一键部署（推荐）](#2-一键部署推荐)
3. [手动分步部署](#3-手动分步部署)
4. [验证清单](#4-验证清单)
5. [常见报错与解决方案](#5-常见报错与解决方案)
6. [故障诊断工具使用](#6-故障诊断工具使用)
7. [开发模式](#7-开发模式)

---

## 1. 前置条件

### 1.1 WSL2 环境

```powershell
# Windows PowerShell（管理员）中安装 WSL2
wsl --install -d Ubuntu-24.04
# 或使用更新的版本：wsl --install -d Ubuntu-26.04

# 验证 WSL 版本（应为 WSL 2）
wsl --list --verbose
```

### 1.2 Docker 环境

**方案 A：Docker Desktop（推荐新手）**

1. 下载安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 安装时勾选 "Use WSL 2 instead of Hyper-V"
3. 在 Settings → Resources → WSL Integration 中启用你的 WSL2 发行版
4. 在 WSL 中验证：

```bash
docker --version
docker compose version
docker run --rm hello-world
```

**方案 B：WSL2 原生 Docker**

```bash
# 在 WSL Ubuntu 中执行
sudo apt update
sudo apt install -y docker.io
sudo service docker start
sudo usermod -aG docker $USER
# 重新登录 WSL 使权限生效
```

### 1.3 项目代码准备

```bash
# 进入 WSL 后，克隆或定位到 SpecWeave 根目录
cd /mnt/d/spaces/SpecWeave  # 或你的实际路径

# 初始化子模块（如果尚未初始化）
git submodule update --init --recursive projects/xuanspace

# 确认 caffe-ffi 源码存在
ls projects/xuanspace/libs/caffe-ffi/CMakeLists.txt
```

---

## 2. 一键部署（推荐）

### 2.1 执行一键部署脚本

在 WSL 终端中，从 SpecWeave 根目录执行：

```bash
cd /mnt/d/spaces/SpecWeave/apps/caffe-ffi-jupyter

# 国内用户（使用阿里云/清华镜像源，推荐）
bash scripts/wsl-deploy.sh --cn

# 国际网络用户
# bash scripts/wsl-deploy.sh

# 构建并验证后自动清理测试容器
# bash scripts/wsl-deploy.sh --cn --cleanup

# 强制无缓存重建
# bash scripts/wsl-deploy.sh --cn --rebuild --no-cache
```

### 2.2 脚本参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--cn` | 使用国内镜像源（apt/pip/conda） | 关闭 |
| `--no-cache` | 禁用 Docker 构建缓存 | 关闭 |
| `--skip-base` | 跳过基础镜像检查/构建 | 关闭 |
| `--skip-run` | 仅构建，不启动容器和运行时验证 | 关闭 |
| `--rebuild` | 清理旧容器和镜像后重建 | 关闭 |
| `--cleanup` | 验证完成后自动删除容器 | 关闭 |
| `--tag TAG` | 镜像标签 | `latest` |
| `--ssh-port PORT` | SSH 端口映射 | `2222` |
| `--jupyter-port PORT` | Jupyter 端口映射 | `8888` |
| `--password PASS` | SSH 用户密码 | `deploy-test` |
| `--token TOKEN` | Jupyter Token | `deploy-token` |
| `-v, --verbose` | 详细构建日志输出 | 关闭 |

### 2.3 一键部署执行流程

脚本自动完成以下 **7 个阶段**：

| 阶段 | 内容 | 失败处理 |
|------|------|----------|
| 0. 环境预检 | WSL/Linux检测、Docker引擎、Compose、BuildKit、子模块、源码、端口 | 立即终止并报告错误 |
| 1. 清理旧资源 | 删除同名旧容器（--rebuild时） | 警告后继续 |
| 2. 构建基础镜像 | 构建 jupyter-ssh-base:1.1（如不存在） | 终止 |
| 3. 构建目标镜像 | 构建 caffe-ffi-jupyter（双阶段：builder+runtime） | 终止并输出日志尾部 |
| 4. 启动容器 | 启动验证容器并等待服务就绪 | 终止并输出容器日志 |
| 5. 服务级验证 | supervisord、SSH、Jupyter服务、HTTP API | 报告失败项 |
| 6. Python运行时验证 | Python版本、caffe_ffi导入、共享库ldd、numpy、protobuf、protoc、Kernel、Blob测试、内存API | 报告失败项，给出诊断命令 |
| 7. 结果汇总 | 输出通过/失败统计、连接信息 | 失败时输出排查指南 |

---

## 3. 手动分步部署

如果需要更细粒度控制，可按以下步骤手动执行。

### 3.1 构建基础镜像

```bash
cd /mnt/d/spaces/SpecWeave/apps/jupyter-ssh-base
bash scripts/build.sh --cn  # 国内用户加 --cn
```

### 3.2 构建 caffe-ffi-jupyter 镜像

```bash
cd /mnt/d/spaces/SpecWeave/apps/caffe-ffi-jupyter
bash scripts/build.sh --cn --verify
```

### 3.3 启动容器

```bash
docker run -d \
  -p 2222:22 \
  -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  --name caffe-ffi \
  caffe-ffi-jupyter:latest
```

### 3.4 等待服务启动

```bash
sleep 20
docker exec caffe-ffi supervisorctl status
```

### 3.5 验证 caffe_ffi 导入

```bash
docker exec caffe-ffi bash -lc \
  "source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \
   python -c 'import caffe_ffi; print(caffe_ffi.version())'"
```

---

## 4. 验证清单

部署完成后，逐项确认以下检查点：

### 4.1 服务级验证

| 检查项 | 命令 | 期望结果 |
|--------|------|----------|
| 容器运行 | `docker ps \| grep caffe-ffi` | 状态 Up |
| supervisord | `docker exec caffe-ffi supervisorctl status` | sshd/jupyter 均为 RUNNING |
| SSH 端口 | `curl -s telnet://localhost:2222 2>&1 \| head -1` | SSH-2.0 响应 |
| Jupyter API | `curl -sf http://localhost:8888/api?token=mysecret` | JSON 响应 |

### 4.2 Python 运行时验证

在容器内执行（`docker exec -it caffe-ffi bash`）：

```bash
# 激活环境
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi

# 1. Python 版本
python --version  # 应输出 Python 3.14.x

# 2. caffe_ffi 导入和版本
python -c "import caffe_ffi; print(caffe_ffi.__version__)"

# 3. 共享库依赖（应无 "not found"）
_SO=$(python -c "import caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi.so'))")
ldd "$_SO" | grep "not found"  # 应无输出

# 4. protobuf 版本（应 >= 7.0.0）
python -c "import google.protobuf; print(google.protobuf.__version__)"

# 5. numpy
python -c "import numpy; print(numpy.__version__)"

# 6. Jupyter Kernel
jupyter kernelspec list | grep caffe-ffi

# 7. Blob 功能
python -c "
from caffe_ffi import Blob
import numpy as np
b = Blob()
b.reshape(1, 3, 224, 224)
data = b.data
assert data.shape == (1, 3, 224, 224)
print('Blob OK')
"
```

### 4.3 远程访问验证

```bash
# SSH 验证（需要 sshpass 或手动输入密码 changeme）
ssh -p 2222 -o StrictHostKeyChecking=no jupyteruser@localhost \
  "python -c 'import caffe_ffi; print(\"SSH OK\")'"
```

浏览器访问：`http://localhost:8888/?token=mysecret`，选择 Kernel `Python 3.14 (caffe-ffi)`。

---

## 5. 常见报错与解决方案

### 5.1 Protobuf 版本冲突

#### 症状

```
ImportError: This program requires version 3.0.0 of the Protocol Buffer
runtime library, but the installed version is 4.25.3.
```

或 Python 导入时报：

```
TypeError: Descriptors cannot be created directly.
```

或构建日志中：

```
Could NOT find Protobuf (missing: Protobuf_LIBRARIES Protobuf_INCLUDE_DIR)
```

或运行时：

```
ImportError: libprotobuf.so.32: cannot open shared object file
```

#### 根因分析

caffe-ffi 要求 `protobuf >= 7.0.0`。当出现版本冲突时，通常是以下情况之一：

1. **apt 安装了旧版 protobuf**（Ubuntu 22.04/24.04 默认 apt 源的 libprotobuf-dev 版本通常为 3.x，过旧；Ubuntu 26.04 的 apt 源提供 protobuf 4.x，仍不满足 >= 7 的要求）
2. **pip 和 conda protobuf 版本不一致**：pip 装的 protobuf Python 包和 conda 的 libprotobuf C++ 库主版本不匹配
3. **系统级 libprotobuf 干扰**：/usr/lib 下存在旧版 libprotobuf.so，被运行时动态链接器优先加载

#### 快速定位

```bash
# 运行诊断脚本
bash scripts/diagnose.sh --container caffe-ffi

# 或手动检查容器内各版本
docker exec caffe-ffi bash -lc "
  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi
  echo '=== Python protobuf ==='
  python -c 'import google.protobuf; print(google.protobuf.__version__)'
  echo '=== Conda libprotobuf ==='
  conda list libprotobuf
  echo '=== protoc version ==='
  protoc --version
  echo '=== System libprotobuf ==='
  ldconfig -p | grep libprotobuf
  echo '=== caffe-ffi linked protobuf ==='
  _SO=\$(python -c 'import caffe_ffi,os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))')
  ldd \$_SO | grep protobuf
"
```

**判断标准**：
- Python protobuf 主版本号必须 >= 7
- conda libprotobuf 主版本号必须与 Python protobuf 主版本一致
- ldd 显示链接的 libprotobuf.so 必须来自 `/opt/conda/envs/caffe-ffi/lib/`

#### 修复方案

**方案一：使用诊断脚本自动修复（推荐）**

```bash
bash scripts/diagnose.sh --container caffe-ffi --fix-protobuf
```

**方案二：容器内手动修复**

```bash
docker exec -it caffe-ffi bash
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi

# 强制重新安装 protobuf >= 7
pip install --no-cache-dir 'protobuf>=7.0.0' --force-reinstall

# 如果 pip 修复后仍有 C++ 库问题，使用 conda
conda install -y -c conda-forge 'libprotobuf>=7.0.0' 'protobuf>=7.0.0'

# 验证
python -c "import google.protobuf; print(google.protobuf.__version__)"
```

**方案三：重建镜像（终极方案）**

如果修复失败，可能是构建时就使用了错误的依赖版本：

```bash
# 清理后无缓存重建
docker rmi caffe-ffi-jupyter:latest
docker rmi $(docker images -q --filter "dangling=true") 2>/dev/null || true
bash scripts/build.sh --cn --no-cache --verify
```

---

### 5.2 共享库解析失败

#### 症状

```
ImportError: libcaffe_ffi.so: cannot open shared object file: No such file or directory
```

或：

```
ImportError: libtvm_ffi.so: cannot open shared object file
```

或：

```
OSError: /opt/conda/envs/caffe-ffi/lib/python3.14/site-packages/caffe_ffi/_caffe_ffi.so:
  undefined symbol: _ZN6caffe_ffi3NetC1Ev
```

或 ldd 显示：

```
libtvm_ffi.so => not found
libopenblas.so.0 => not found
libprotobuf.so.32 => not found
```

#### 根因分析

共享库找不到的原因包括：

1. **RPATH 未正确嵌入**：编译时未设置 RPATH，导致 `_caffe_ffi.so` 无法找到同目录的依赖
2. **LD_LIBRARY_PATH 未包含 conda lib 目录**：运行时环境变量未正确设置
3. **ld.so.conf.d 未配置**：系统动态链接器缓存未包含 caffe-ffi 库路径
4. **conda 环境未激活**：直接用 python3 而不是 conda 环境中的 python
5. **构建时 BLAS/Protobuf 路径错误**：编译时链接到了系统库而非 conda 库

#### 快速定位

```bash
# 使用诊断脚本
bash scripts/diagnose.sh --container caffe-ffi --fix-ldpath

# 或手动检查
docker exec caffe-ffi bash -lc "
  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi
  
  # 1. 确认 conda 环境激活
  which python  # 应在 /opt/conda/envs/caffe-ffi/bin/python
  
  # 2. 查看 _caffe_ffi.so 位置
  python -c 'import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))'
  
  # 3. ldd 检查
  _SO=\$(python -c 'import caffe_ffi,os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))')
  echo '=== ldd _caffe_ffi.so ==='
  ldd \$_SO
  
  # 4. 检查 LD_LIBRARY_PATH
  echo '=== LD_LIBRARY_PATH ==='
  echo \$LD_LIBRARY_PATH
  
  # 5. 检查 RPATH
  echo '=== RPATH ==='
  readelf -d \$_SO | grep -E 'RPATH|RUNPATH' || echo 'NO RPATH'
  
  # 6. 检查 ldconfig
  echo '=== ldconfig caffe paths ==='
  ldconfig -p | grep -E 'caffe|tvm_ffi|openblas|protobuf'
"
```

#### 修复方案

**方案一：自动修复（推荐）**

```bash
bash scripts/diagnose.sh --container caffe-ffi --fix-ldpath
```

**方案二：容器内手动修复**

```bash
docker exec -it caffe-ffi bash

# 确保 conda 环境正确激活
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi

# 重建 ld.so.conf.d
CAFFE_DIR=$(python -c "import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))")
echo "/opt/conda/envs/caffe-ffi/lib" > /etc/ld.so.conf.d/caffe-ffi.conf
echo "$CAFFE_DIR" >> /etc/ld.so.conf.d/caffe-ffi.conf
ldconfig

# 设置 LD_LIBRARY_PATH
export LD_LIBRARY_PATH="/opt/conda/envs/caffe-ffi/lib:$CAFFE_DIR:${LD_LIBRARY_PATH:-}"

# 永久设置（SSH 登录生效）
grep -q 'caffe-ffi/lib' ~/.bashrc || \
  echo 'export LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:${LD_LIBRARY_PATH}' >> ~/.bashrc

# 验证
_SO=$(python -c "import caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi.so'))")
ldd "$_SO" | grep "not found"  # 应无输出
```

**方案三：修复 RPATH 后重新安装**

如果 RPATH 缺失，说明编译时未正确配置：

```bash
docker exec -it caffe-ffi bash
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi

# 如果有开发卷挂载了源码，重新编译安装
cd /path/to/caffe-ffi
pip install --no-build-isolation -e . -v \
  --config-settings=cmake.define.CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON \
  --config-settings=cmake.define.CMAKE_BUILD_RPATH_USE_ORIGIN=ON \
  --config-settings=cmake.define.CMAKE_BUILD_WITH_INSTALL_RPATH=ON
```

---

### 5.3 Docker/WSL 环境问题

#### 症状：`docker: command not found`

```bash
# 检查 Docker 是否安装
which docker

# WSL2 + Docker Desktop: 确保 Docker Desktop 已启动
# WSL2 原生 Docker:
sudo service docker start
```

#### 症状：`Cannot connect to the Docker daemon`

```bash
# Docker Desktop: 打开 Docker Desktop 应用
# WSL 原生:
sudo service docker start
sudo usermod -aG docker $USER
newgrp docker  # 或重新登录 WSL
```

#### 症状：端口被占用

```bash
# 检查端口占用
ss -tlnp | grep -E '2222|8888'

# 使用其他端口启动容器
docker run -d -p 2223:22 -p 8889:8888 \
  -e USER_PASSWORD=changeme -e JUPYTER_TOKEN=mysecret \
  --name caffe-ffi caffe-ffi-jupyter:latest
```

#### 症状：构建超时/网络错误

```bash
# 使用国内镜像源
bash scripts/build.sh --cn

# 或者在 wsl-deploy.sh 中加 --cn
bash scripts/wsl-deploy.sh --cn
```

---

### 5.4 构建阶段失败

#### 症状：cmake configure 失败 — Could NOT find BLAS

```
Could NOT find BLAS (missing: BLAS_LIBRARIES)
```

**修复**：Dockerfile 中通过 conda-forge 安装了 `libopenblas`，确保 CMAKE_PREFIX_PATH 包含 conda 环境路径。诊断检查：

```bash
docker exec -it caffe-ffi bash
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi
echo $CMAKE_PREFIX_PATH  # 应包含 /opt/conda/envs/caffe-ffi
conda list openblas       # 应已安装
```

#### 症状：编译错误 — 编译器不支持 C++17

Dockerfile 中已安装 build-essential（含 GCC 9+），如出现此错误检查：

```bash
docker exec -it <builder-container> bash
g++ --version  # 应 >= 9
```

#### 症状：tvm-ffi 找不到

```
Could NOT find tvm_ffi (missing: tvm_ffi_DIR)
```

**修复**：builder 阶段通过 pip 安装了 `apache-tvm-ffi`，Python 回退机制会自动发现。手动检查：

```bash
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi
python -m tvm_ffi.config --cmakedir  # 应输出 CMake 配置目录
```

---

### 5.5 Jupyter/Kernel 问题

#### 症状：Kernel 启动失败或不断重启

```bash
# 检查 kernel 注册
docker exec caffe-ffi jupyter kernelspec list

# 检查 kernel.json
docker exec caffe-ffi cat /usr/local/share/jupyter/kernels/caffe-ffi/kernel.json

# 查看 Jupyter 日志
docker exec caffe-ffi cat /var/log/jupyter.log 2>/dev/null || \
  docker logs caffe-ffi 2>&1 | grep -i jupyter
```

手动修复：

```bash
docker exec -it caffe-ffi bash
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi
python -m ipykernel install --name caffe-ffi \
  --display-name "Python 3.14 (caffe-ffi)" \
  --prefix=/usr/local --replace
```

---

### 5.6 SSH 连接问题

#### 症状：SSH 连接被拒绝

```bash
# 检查 sshd 是否运行
docker exec caffe-ffi supervisorctl status sshd

# 检查端口映射
docker port caffe-ffi

# 检查容器内 sshd 配置
docker exec caffe-ffi cat /etc/ssh/sshd_config | grep -E 'Port|PasswordAuth'
```

---

## 6. 故障诊断工具使用

### 6.1 diagnose.sh 诊断脚本

诊断脚本提供 **10 项自动检查**和**自动修复能力**：

```bash
# 完整诊断
bash scripts/diagnose.sh --container caffe-ffi

# 诊断并自动修复 protobuf 和共享库问题
bash scripts/diagnose.sh --container caffe-ffi --fix-all

# 仅修复 protobuf
bash scripts/diagnose.sh --container caffe-ffi --fix-protobuf

# 仅修复共享库路径
bash scripts/diagnose.sh --container caffe-ffi --fix-ldpath

# 导出诊断报告到文件
bash scripts/diagnose.sh --container caffe-ffi --dump
```

### 6.2 诊断项说明

| 序号 | 诊断项 | 检查内容 | 自动修复 |
|------|--------|----------|----------|
| 1 | 容器状态 | 存在性、运行状态、自动启动 | ✅ |
| 2 | 服务状态 | supervisord/SSH/Jupyter | ❌ |
| 3 | Conda 环境 | Python版本、关键包（libprotobuf/protobuf/ninja/cmake/numpy/openblas） | ❌ |
| 4 | Protobuf 一致性 | Python/conda/protoc/链接库 四重版本校验 | ✅ --fix-protobuf |
| 5 | 共享库依赖 | ldd分析、RPATH、LD_LIBRARY_PATH、ld.so.conf.d | ✅ --fix-ldpath |
| 6 | tvm_ffi 依赖 | 导入、路径、共享库 | ❌ |
| 7 | Jupyter Kernel | 注册状态、kernel.json 检查 | ✅（--fix-all时） |

### 6.3 容器日志分析

```bash
# 查看完整容器日志
docker logs caffe-ffi 2>&1 | tail -100

# 实时跟踪日志
docker logs -f caffe-ffi

# 查看 supervisord 日志
docker exec caffe-ffi ls /var/log/supervisor/
docker exec caffe-ffi cat /var/log/supervisor/jupyter-stderr*.log 2>/dev/null
```

---

## 7. 开发模式

### 7.1 Volume 挂载源码进行开发

启动容器时挂载本地 caffe-ffi 源码：

```bash
cd /mnt/d/spaces/SpecWeave/apps/caffe-ffi-jupyter

docker run -d \
  -p 2222:22 \
  -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v /mnt/d/spaces/SpecWeave:/workspace/SpecWeave \
  -w /workspace/SpecWeave/projects/xuanspace/libs/caffe-ffi \
  --name caffe-ffi-dev \
  caffe-ffi-jupyter:latest
```

### 7.2 Editable 模式重新安装

```bash
ssh -p 2222 jupyteruser@localhost
cd /workspace/SpecWeave/projects/xuanspace/libs/caffe-ffi
pip install --no-build-isolation -e . -v
```

### 7.3 运行测试

```bash
# Python 单元测试
pytest tests/python -v

# FFI 前缀一致性检查
python scripts/check_ffi_prefix.py --verbose

# 安装验证
python scripts/verify_install.py
```

### 7.4 使用 docker compose 开发模式

编辑 `docker-compose.yml` 取消开发卷注释：

```yaml
volumes:
  - ../../projects/xuanspace/libs/caffe-ffi:/workspace/caffe-ffi:cached
```

```bash
APT_MIRROR=aliyun PIP_MIRROR=aliyun CONDA_MIRROR=tuna docker compose up -d
```

---

## 附录：快速参考卡片

```
┌─────────────────────────────────────────────────────────────┐
│  一键部署:   bash scripts/wsl-deploy.sh --cn                │
│  故障诊断:   bash scripts/diagnose.sh --fix-all             │
│  容器Shell:  docker exec -it caffe-ffi bash                 │
│  SSH连接:    ssh -p 2222 jupyteruser@localhost              │
│  Jupyter:    http://localhost:8888/?token=deploy-token      │
│  验证导入:   docker exec caffe-ffi bash -lc \              │
│    'source /opt/conda/.../conda.sh && conda activate caffe-ffi\│
│     && python -c "import caffe_ffi; print(caffe_ffi.version())"'│
│  容器日志:   docker logs caffe-ffi 2>&1 | tail -50          │
│  重启服务:   docker exec caffe-ffi supervisorctl restart all│
│  清理容器:   docker rm -f caffe-ffi                         │
└─────────────────────────────────────────────────────────────┘
```
