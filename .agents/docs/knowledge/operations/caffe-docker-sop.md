---
id: "caffe-docker-sop"
title: "Caffe Docker 容器构建与运行 SOP"
source: "retrospective-caffe-docker-runtime-20260722"
date: 2026-07-22
tags: [caffe, docker, sop, build, runtime, verification]
---
# Caffe Docker 容器构建与运行 SOP

> 最后验证日期：2026-07-22
> 验证镜像：`caffe-cpu:runtime` (711MB)
> 验证结果：6/6 项全部通过
> 最新更新：新增 Python 版本升级章节（8.5），conda 本地环境 Python 3.12 → 3.14

## 一、前置条件

| 条件 | 要求 | 检查命令 |
|------|------|---------|
| 操作系统 | WSL2 (Ubuntu 22.04) 或 Linux | `uname -a` |
| Docker | 29.0+，服务运行中 | `docker version` |
| 磁盘空间 | 构建目录 ≥ 10GB 可用 | `df -h` |
| 内存 | Docker Desktop ≥ 8GB（推荐 16GB） | `docker info \| grep Memory` |
| Caffe 源码 | `external/chaos/caffe/caffex/` 目录存在 | `ls external/chaos/caffe/caffex/Makefile` |

## 二、快速开始

### 2.1 一键构建 runtime 镜像

```bash
cd external/chaos/caffe/docker/local/conda
./build/build-multistage.sh --target runtime --verify
```

- 首次构建耗时：15-40 分钟
- 二次构建耗时：~10 秒（全部层缓存命中）
- 产出镜像：`caffe-cpu:runtime` (711MB)

### 2.2 构建并导出镜像

```bash
./build/build-multistage.sh --target runtime --verify --export --compress
```

导出文件：`caffe-cpu-runtime-<timestamp>.tar.gz`

### 2.3 启动开发容器

```bash
./run.sh
```

交互式 bash，默认挂载 Caffe 源码目录，可直接 `import caffe`。

## 三、Dockerfile 目标阶段

| 阶段 | 说明 | 入口 |
|------|------|------|
| `base-system` | 公共基础层（Ubuntu 22.04 + apt 阿里云镜像源） | — |
| `base-builder` | 基础构建环境（系统依赖 + Python 3.10 依赖） | — |
| `builder-dev` | 开发构建环境（含源码挂载） | `./build.sh` |
| `builder` | CI 构建阶段（编译 Caffe 源码） | `./build/build-multistage.sh --target builder` |
| `runtime` | 完整运行时镜像（从 builder 获取编译产物） | `./build/build-multistage.sh --target runtime` |

## 四、构建选项

| 选项 | 说明 |
|------|------|
| `-t TAG` | 指定镜像标签（默认：`runtime`） |
| `--target TARGET` | 指定构建阶段（默认：`runtime`） |
| `--no-cache` | 禁用缓存，强制全量重建 |
| `--verify` | 构建完成后自动运行验证脚本 |
| `--export` | 构建完成后导出镜像为 tar 文件 |
| `--compress` | 导出时使用 gzip 压缩 |
| `--verbose` | 详细日志输出 |
| `--log-file PATH` | 自定义日志文件路径 |
| `--jobs N` | 并行编译任务数（默认：`nproc`） |

## 五、验证步骤

### 5.1 自动验证（构建时）

```bash
./build/build-multistage.sh --target runtime --verify
```

构建完成后自动执行 `verify-caffe.sh`，检查以下 6 项：

| 编号 | 检查项 | 预期结果 |
|------|--------|---------|
| 1 | Python 版本 | 3.10.12 |
| 2 | Caffe 库文件 | `libcaffe.so` 3.9MB, `_caffe.so` 1.8MB |
| 3 | Python 依赖 | numpy 1.26+, scipy 1.15+, protobuf 3.20 |
| 4 | Caffe 导入 | `caffe.__version__` = 1.0.0, `caffe.Net`, `caffe.SGDSolver` 可用 |
| 5 | Proto 定义 | `caffe_pb2.NetParameter`, `caffe_pb2.BlobProto` 可用 |
| 6 | 命令行工具 | `caffe`, `compute_image_mean`, `convert_imageset`, `upgrade_net_proto_text` |

### 5.2 手动验证

```bash
docker run --rm caffe-cpu:runtime verify-caffe.sh
```

或交互式验证：

```bash
docker run --rm -it caffe-cpu:runtime bash
python3 -c "import caffe; print('Caffe version:', caffe.__version__)"
```

### 5.3 运行时验证（挂载源码）

```bash
docker run --rm \
  -v /mnt/d/spaces/SpecWeave/external/chaos/caffe/docker/local/conda/scripts/verify-runtime.sh:/tmp/verify-runtime.sh \
  caffe-cpu:runtime bash /tmp/verify-runtime.sh
```

## 六、环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| `CAFFE_ROOT` | `/workspace/caffex` | Caffe 源码根目录 |
| `PYTHONPATH` | `/workspace/caffex/python` | Python 模块搜索路径 |
| `LD_LIBRARY_PATH` | `/workspace/caffex/build/lib:/usr/lib:/usr/lib/x86_64-linux-gnu:/usr/local/lib` | 动态库搜索路径 |
| `PIP_INDEX_URL` | `https://mirrors.aliyun.com/pypi/simple` | pip 镜像源 |
| `DEBIAN_FRONTEND` | `noninteractive` | 非交互式 apt 安装 |

## 七、镜像导出与分发

```bash
cd external/chaos/caffe/docker/local/conda

# 导出未压缩的 tar（约 711MB）
./build/export-image.sh

# 导出 gzip 压缩的 tar.gz（约 250MB）
./build/export-image.sh --compress

# 指定输出路径
./build/export-image.sh --output /tmp/caffe-cpu-runtime.tar.gz --compress
```

加载导出的镜像：

```bash
docker load < caffe-cpu-runtime.tar.gz
```

## 八、故障排查

### 8.1 构建失败：网络问题

- 已默认使用阿里云 apt / pip 镜像
- 可重试，Docker 会尽量复用缓存

### 8.2 构建失败：内存不足

- Docker Desktop 建议至少分配 8GB 内存，推荐 16GB+

### 8.3 编译兼容性问题

Caffe 1.0（2017）在 Ubuntu 22.04 + Python 3.10 环境下存在系统性兼容性问题。已萃取的预检清单覆盖 6 项常见问题：

- BLAS 库选择（libatlas → openblas）
- Python 版本兼容性（setuptools 废弃函数）
- OpenCV 版本（头文件路径 + imgcodecs 链接）
- protobuf 版本
- Boost 版本（库命名差异）
- C++ 标准（C++11 → C++14）

详见：[老旧 C++ 项目编译兼容性预检清单](../patterns/process-patterns/legacy-cpp-compilation-compatibility-checklist.md)

### 8.4 `import caffe` 失败

- 确认使用 `./run.sh` 启动（自动设置环境变量）
- 若手动 `docker run`，需显式设置 `CAFFE_ROOT`、`PYTHONPATH`、`LD_LIBRARY_PATH`

### 8.5 Python 版本升级

Caffe 项目支持两种 Python 环境：**Docker 运行时**（Ubuntu 22.04 系统 Python 3.10）和 **conda 本地开发环境**（`proto-env`）。

#### 8.5.1 升级 conda 本地环境 Python 版本

修改 `external/chaos/caffe/README.md` 中的 conda 环境创建命令：

```bash
# 升级前（Python 3.12）
conda create -n proto-env python=3.12

# 升级后（Python 3.14）
conda create -n proto-env python=3.14
```

升级后需重建环境：

```bash
conda deactivate
conda env remove -n proto-env
conda create -n proto-env python=3.14
conda activate proto-env
conda install -c conda-forge libprotobuf
pip install protobuf -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 8.5.2 升级注意事项

| 注意事项 | 说明 |
|---------|------|
| protobuf 兼容性 | 确认 `libprotobuf` 和 `pip protobuf` 版本匹配，避免 C++ 库与 Python 绑定版本不一致 |
| conda-forge 可用性 | 新版 Python 的某些包可能尚未在 conda-forge 发布，需提前验证 `conda search python=3.14` |
| 环境重建 | Python 大版本升级（3.12→3.14）必须重建 conda 环境，不可原地升级 |
| Docker 镜像独立 | Docker 运行时镜像使用系统 Python 3.10，与 conda 本地环境版本无关，升级 conda 不影响 Docker 镜像 |
| 交叉验证 | 升级后分别验证 conda 环境和 Docker 镜像均可正常运行 Caffe |

#### 8.5.3 升级 Docker 镜像 Python 版本

若需升级 Docker 镜像中的 Python 版本，需修改 `Dockerfile` 和 `generate-makefile-config.sh`：

1. 更新 `Dockerfile` 中 `python3-dev` 等系统包的 Python 版本号
2. 更新 `generate-makefile-config.sh` 中 Boost.Python 库名检测逻辑（如 `boost_python310` → `boost_python314`）
3. 确认所有 pip 依赖在新 Python 版本下可用
4. 无缓存重建：`./build/build-multistage.sh --target runtime --no-cache --verify`

### 8.6 Boost.Python 库找不到

- `generate-makefile-config.sh` 自动检测多种 Boost.Python 命名方式
- 如仍失败，检查容器内：`ldconfig -p | grep boost_python`

## 九、容器生命周期管理

```bash
# 查看本地 Caffe 镜像
docker images caffe-cpu*

# 查看运行中的容器
docker ps --filter "ancestor=caffe-cpu"

# 停止容器
docker stop <container_name>

# 清理未使用的镜像
docker image prune -a
```

## 十、目录结构

```
external/chaos/caffe/docker/local/
├── conda/
│   ├── Dockerfile              # 多阶段 Dockerfile（266 行，5 个阶段）
│   ├── build.sh                # 开发构建（builder-dev）
│   ├── run.sh                  # 开发容器启动（挂载源码）
│   ├── RUNTIME_IMAGE_USAGE.md  # 使用指南
│   ├── build/
│   │   ├── build-multistage.sh # 多阶段构建（runtime 构建 + 验证 + 导出）
│   │   └── export-image.sh     # 镜像导出
│   ├── config/
│   │   ├── condarc             # conda 镜像源配置
│   │   └── pip.conf            # pip 镜像源配置
│   └── scripts/
│       ├── generate-makefile-config.sh  # Makefile.config 动态生成
│       ├── verify-caffe.sh              # 编译验证
│       └── verify-runtime.sh            # 运行时验证
├── lib/
│   ├── log.sh                   # 彩色日志库
│   └── check_env.sh             # 环境检查库
└── logs/                        # 构建日志
```

## 十一、关联文档

| 文档 | 说明 |
|------|------|
| [RUNTIME_IMAGE_USAGE.md](../../../external/chaos/caffe/docker/local/conda/RUNTIME_IMAGE_USAGE.md) | 运行时镜像使用指南 |
| [可参考项目索引](../../assets/reference-project-index.md) | 同类项目参考模板 |
| [老旧 C++ 编译兼容性预检清单](../../patterns/process-patterns/legacy-cpp-compilation-compatibility-checklist.md) | 编译兼容性检查清单 |
| [复盘报告](../../retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/README.md) | 全流程复盘 |
| [导出报告](../../retrospective/reports/bug-fix/docker-build/retrospective-caffe-docker-runtime-20260722/export-summary.md) | 项目汇总导出 |