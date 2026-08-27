---
id: "jupyter-ml-model-management"
title: "ML 模型管理（OMLMD + OLOT）"
source: "README.md#ML模型管理OMLMD--OLOT"
---
# ML 模型管理（OMLMD + OLOT）

容器内集成了两套 ML 模型 OCI 分发工具，实现模型版本化管理和标准化部署。

## 概述

| 工具 | 标准 | 用途 | 命令前缀 |
|------|------|------|---------|
| **OMLMD** | OCI Artifact | 模型作为OCI artifact分发 | `invoke model.push/pull/config` |
| **OLOT** | KServe ModelCar | 模型作为OCI镜像层打包 | `invoke model.pack/extract` |

两套工具都预装在容器镜像内，也可通过 `pip install -e ".[model]"` 安装到宿主机。

## 启动本地模型仓库

ML模型开发测试需要本地OCI registry：

```bash
# 启动本地model-registry服务（zot镜像）
podman-compose --profile registry up -d

# 验证registry运行
curl http://localhost:5000/v2/_catalog
```

registry服务监听在5000端口（可通过`REGISTRY_PORT`环境变量修改），使用HTTP协议（本地开发用）。

## OMLMD — ML 模型 OCI Artifact 分发

OMLMD（OCIFactory AI Model Management）将 ML 模型作为 OCI artifact 存储和分发，支持模型元数据配置和版本管理。

模型以自定义媒体类型 `application/mlmodel` 存储在 OCI registry 中，支持版本标签、配置元数据和跨 registry 复制。

### 推送模型

```bash
# 推送本地模型目录到本地仓库
invoke model.push ./my-model --ref localhost:5000/models/bert:v1

# 推送到远程仓库
invoke model.push ./my-model --ref docker.io/youruser/models/bert:v1
```

参数：
- `./my-model`：模型目录路径（包含模型文件、配置等）
- `--ref`：OCI引用地址（registry/repo:tag）

### 拉取模型

```bash
# 从仓库拉取模型
invoke model.pull --ref localhost:5000/models/bert:v1 --output ./models

# 拉取特定版本
invoke model.pull --ref localhost:5000/models/bert:v2 --output ./models-v2
```

参数：
- `--ref`：OCI引用地址
- `--output`：本地输出目录

### 查询模型元数据

```bash
# 查询模型元数据配置
invoke model.config --ref localhost:5000/models/bert:v1
```

输出模型的OCI config信息，包括媒体类型、层数、标注等。

### OMLMD使用示例

```bash
# 准备测试模型
mkdir -p ./workspace/test-model
echo "model weights" > ./workspace/test-model/model.bin
echo '{"name":"test-model","version":"1.0"}' > ./workspace/test-model/config.json

# 推送
invoke model.push ./workspace/test-model --ref localhost:5000/models/test:v1

# 查询元数据
invoke model.config --ref localhost:5000/models/test:v1

# 拉取验证
invoke model.pull --ref localhost:5000/models/test:v1 --output ./workspace/pulled
ls -la ./workspace/pulled/
```

## OLOT — KServe ModelCar 标准镜像打包

OLOT（OCI Layers On Top）遵循 KServe ModelCar 标准，将模型文件作为 OCI 镜像层附加到基础镜像（通常是推理服务器镜像）上，实现"模型即镜像"的部署模式。

ModelCar 镜像标准让 KServe/Serving Runtime 可以直接拉取并挂载模型，无需额外的模型下载步骤。

### 打包模型为 ModelCar 镜像

```bash
# 打包模型为ModelCar镜像（基于当前jupyter镜像）并推送
invoke model.pack ./my-model \
  --base jupyter-podman-rootless:latest \
  --ref localhost:5000/models/car:v1

# 基于Triton推理服务器打包（生产部署场景）
invoke model.pack ./my-model \
  --base nvcr.io/nvidia/tritonserver:24.08-py3 \
  --ref localhost:5000/models/triton-bert:v1
```

参数：
- `./my-model`：模型目录路径
- `--base`：基础镜像（推理服务器镜像）
- `--ref`：目标ModelCar镜像引用地址

olot会将模型文件作为新的OCI层添加到基础镜像之上，然后推送到registry。

### 从 ModelCar 镜像提取模型

```bash
# 从ModelCar镜像提取模型目录
invoke model.extract \
  --ref localhost:5000/models/car:v1 \
  --output ./extracted-models
```

参数：
- `--ref`：ModelCar镜像引用
- `--output`：模型提取输出目录

### OLOT使用示例

```bash
# 打包测试模型
invoke model.pack ./workspace/test-model \
  --base jupyter-podman-rootless:latest \
  --ref localhost:5000/models/test-car:v1

# 从ModelCar提取验证
invoke model.extract \
  --ref localhost:5000/models/test-car:v1 \
  --output ./workspace/extracted-car
ls -la ./workspace/extracted-car/
```

## 三层后端架构

ML 命令同样遵循三层后端优先级，对用户透明：

1. **podman-compose 后端（优先）**
   - 当`podman-compose`可用且容器运行时，通过compose exec进入容器执行omlmd/olot
   - 自动挂载workspace目录

2. **podman-py SDK 后端（其次）**
   - 通过 Podman Unix socket API exec 进入容器
   - 比 CLI 更高效，支持流式输出

3. **CLI fallback（保底）**
   - 通过 subprocess 调用 `podman`/`docker` 命令
   - 若容器未运行，检查宿主机是否安装omlmd/olot
   - 都不可用时提示安装 `pip install -e ".[model]"`

## Python兼容性说明

omlmd/olot官方支持Python ≤3.12，但本容器使用Python 3.14 cp314t（free-threading）。通过以下方式兼容：

- pip安装时使用`--ignore-requires-python`绕过版本限制
- 实际测试omlmd/olot在cp314t下可正常工作
- 如遇兼容性问题，可构建标准cp314版本镜像（见 [11-free-threading.md](11-free-threading.md)）

ML模型管理规范详见 [.agents/rules/ml-models.md](../.agents/rules/ml-models.md)。
