---
id: "jupyter-ml-models-rules"
title: "ML模型管理规范（OMLMD+OLOT）"
source: "README.md#ML模型管理 + AGENTS.md#核心约束"
---
# ML模型管理规范（jupyter-podman-rootless）

## 基础约定

- ML模型分发标准：OCI Artifact + KServe ModelCar
- OCI Artifact工具：OMLMD（OCIFactory AI Model Management）
- ModelCar工具：OLOT（OCI Layers On Top）
- 容器内预装：omlmd + olot[oras-py]（通过conda安装）
- 本地模型仓库：zot镜像（compose profile: registry）
- Python兼容性：omlmd/olot官方支持Python ≤3.12，已通过`--ignore-requires-python`兼容cp314t（free-threading）
- 三层后端架构同样适用于ML命令（compose → SDK → CLI）

## OMLMD — ML模型OCI Artifact分发

### 功能说明

OMLMD将ML模型作为OCI artifact存储和分发，支持：
- 模型版本化（通过OCI标签）
- 模型元数据配置（config media type）
- 跨registry复制
- 自定义媒体类型：`application/mlmodel`

### 命令参考（tasks/model.py）

#### model.push — 推送模型到OCI registry

```bash
# 推送本地模型目录到registry
invoke model.push ./my-model --ref localhost:5000/models/bert:v1

# 使用自定义容器名
invoke model.push ./my-model --ref localhost:5000/models/bert:v1 --name my-container
```

参数：
- `--path`（必填，位置参数）：本地模型目录路径
- `--ref`（必填）：OCI引用地址（registry/repo:tag）
- `--name`：容器名（默认：jupyter-podman）
- `--user`：执行用户（默认：devuser）

实现逻辑：
1. 检测后端可用性（优先在容器内执行，若容器运行则exec进入）
2. 在容器内调用`omlmd push <ref> <path>`
3. 推送进度输出到日志
4. 推送完成后打印模型引用地址

#### model.pull — 从OCI registry拉取模型

```bash
# 拉取模型到本地目录
invoke model.pull --ref localhost:5000/models/bert:v1 --output ./models

# 拉取到指定目录
invoke model.pull --ref localhost:5000/models/bert:v1 --output /workspace/models
```

参数：
- `--ref`（必填）：OCI引用地址
- `--output`（必填）：本地输出目录
- `--name`：容器名
- `--user`：执行用户

#### model.config — 查询OCI模型元数据

```bash
# 查询模型元数据配置
invoke model.config --ref localhost:5000/models/bert:v1
```

输出模型的config信息（包括媒体类型、层数、标注等）。

## OLOT — KServe ModelCar标准镜像打包

### 功能说明

OLOT遵循KServe ModelCar标准，将模型文件作为OCI镜像层附加到基础镜像（通常是推理服务器镜像）上：
- "模型即镜像"的部署模式
- KServe/Serving Runtime可直接拉取并挂载模型
- 无需额外的模型下载步骤（镜像拉取即模型拉取）
- 模型作为独立的OCI层，可缓存和复用

### 命令参考

#### model.pack — 打包模型为ModelCar镜像并推送

```bash
# 打包本地模型为ModelCar镜像（基于当前jupyter镜像）
invoke model.pack ./my-model \
  --base jupyter-podman-rootless:latest \
  --ref localhost:5000/models/car:v1

# 基于其他推理服务器镜像打包
invoke model.pack ./my-model \
  --base nvcr.io/nvidia/tritonserver:24.08-py3 \
  --ref localhost:5000/models/triton-bert:v1
```

参数：
- `--path`（必填，位置参数）：本地模型目录路径
- `--base`（必填）：基础镜像（推理服务器镜像或jupyter基础镜像）
- `--ref`（必填）：目标ModelCar镜像引用地址
- `--name`：容器名
- `--user`：执行用户

实现逻辑：
1. 确保基础镜像已存在（本地有或可拉取）
2. 在容器内调用`olot pack <base> <path> --ref <ref>`
3. olot将模型文件作为新层添加到基础镜像
4. 推送到指定registry
5. 打印ModelCar镜像引用

#### model.extract — 从ModelCar镜像提取模型目录

```bash
# 从ModelCar镜像提取模型
invoke model.extract \
  --ref localhost:5000/models/car:v1 \
  --output ./extracted-models
```

参数：
- `--ref`（必填）：ModelCar镜像引用
- `--output`（必填）：模型提取输出目录
- `--name`：容器名
- `--user`：执行用户

### olot_car.py辅助脚本

容器内脚本：`scripts/olot_car.py`，提供：
- 模型层识别（区分基础镜像层和模型层）
- 模型提取验证
- ModelCar元数据标注
- 与KServe标准兼容性检查

## model-registry本地仓库

### 启动本地仓库

```bash
# 使用podman-compose启动（需要profile: registry）
podman-compose --profile registry up -d

# 或通过invoke启动（透传compose参数）
```

服务配置：
- 镜像：`ghcr.io/project-zot/zot-linux-amd64:latest`
- 端口：5000（可通过REGISTRY_PORT环境变量修改）
- 协议：HTTP（本地开发用，REGISTRY_PLAIN_HTTP=true）
- 数据持久化：Docker volume `registry-data`

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| REGISTRY_URL | localhost:5000 | ML模型OCI registry地址 |
| REGISTRY_PORT | 5000 | 本地model-registry服务端口 |
| REGISTRY_PLAIN_HTTP | true | 本地registry使用HTTP（非HTTPS） |

## 三层后端架构（ML命令）

ML命令同样遵循三层后端优先级：

1. **podman-compose后端（优先）**
   - 容器运行时直接在容器内调用omlmd/olot
   - 支持通过compose exec执行命令
   - 自动挂载workspace目录

2. **podman-py SDK后端（其次）**
   - 通过Podman Unix socket API exec进入容器
   - 比CLI更高效，支持流式输出

3. **CLI fallback（保底）**
   - 通过subprocess调用podman exec
   - 若容器未运行，检查宿主机是否安装omlmd/olot
   - 都不可用时提示安装`pip install -e ".[model]"`

所有后端对用户透明，`invoke model.*`命令自动选择最优后端。

## conda环境配置

ML工具在conda-lock/environment.yml中定义：

```yaml
name: base
channels:
  - conda-forge
dependencies:
  - python=3.14
  - jupyterlab>=4.4
  - notebook>=7.3
  - ipykernel
  - ipywidgets
  - pip:
      - omlmd
      - "olot[oras-py]"
```

注意：omlmd和olot通过pip安装（conda-forge可能没有最新版本），并使用`--ignore-requires-python`绕过cp314t版本限制。

## 使用流程示例

### 开发测试流程

```bash
# 1. 构建镜像
invoke build --apt-mirror tuna

# 2. 启动容器+本地模型仓库
podman-compose -f compose.yaml -f compose.dev.yaml --profile registry up -d

# 3. 推送测试模型
mkdir -p ./workspace/test-model
echo "test model" > ./workspace/test-model/model.bin
invoke model.push ./workspace/test-model --ref localhost:5000/models/test:v1

# 4. 查询模型元数据
invoke model.config --ref localhost:5000/models/test:v1

# 5. 拉取验证
invoke model.pull --ref localhost:5000/models/test:v1 --output ./workspace/pulled-model

# 6. 打包为ModelCar
invoke model.pack ./workspace/test-model \
  --base jupyter-podman-rootless:latest \
  --ref localhost:5000/models/test-car:v1

# 7. 从ModelCar提取
invoke model.extract --ref localhost:5000/models/test-car:v1 \
  --output ./workspace/extracted-model
```

## 验证清单

ML模型功能修改后必须验证：
- [ ] 容器内omlmd命令可执行：`omlmd --version`
- [ ] 容器内olot命令可执行：`olot --version`
- [ ] model-registry服务可启动（--profile registry）
- [ ] model.push可推送模型到本地registry
- [ ] model.config可查询元数据
- [ ] model.pull可拉取模型
- [ ] model.pack可打包ModelCar镜像
- [ ] model.extract可从ModelCar提取模型
- [ ] 三层后端自动降级正常工作
- [ ] cp314t free-threading环境下omlmd/olot无崩溃
