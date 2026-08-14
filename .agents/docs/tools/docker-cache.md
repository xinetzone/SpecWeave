# docker-cache — Docker 镜像本地缓存管理工具

> 将 Docker 镜像持久化到 Windows 文件系统，WSL2 重置/Docker 损坏后 2-5 分钟快速恢复，避免 20-40 分钟的完整重建。

---

## 目录

- [为什么需要它？](#为什么需要它)
- [快速开始](#快速开始)
- [命令参考](#命令参考)
  - [build — 智能构建与缓存](#build--智能构建与缓存)
  - [save — 手动保存镜像](#save--手动保存镜像)
  - [load — 从缓存加载](#load--从缓存加载)
  - [list — 查看缓存状态](#list--查看缓存状态)
  - [clean — 清理缓存](#clean--清理缓存)
  - [doctor — 环境诊断](#doctor--环境诊断)
- [架构原理](#架构原理)
  - [目录结构](#目录结构)
  - [缓存命中判定](#缓存命中判定)
  - [并发安全](#并发安全)
  - [压缩策略](#压缩策略)
  - [Manifest 数据模型](#manifest-数据模型)
- [环境变量](#环境变量)
- [典型工作流](#典型工作流)
- [与现有构建脚本集成](#与现有构建脚本集成)
- [故障排查](#故障排查)

---

## 为什么需要它？

### 痛点

在 Windows + WSL2 环境下开发 Docker 镜像时，以下场景频繁发生：

| 场景 | 恢复时间 |
|------|----------|
| WSL2 重置/重装 | 20-40 分钟（需重新拉取基础镜像 + 逐层构建） |
| Docker Desktop 数据损坏 | 20-40 分钟 |
| 切换 WSL2 发行版 | 20-40 分钟 |
| 多机器同步开发环境 | 每台机器 20-40 分钟 |

本项目维护着一条 6 层镜像依赖链（base → conda → conda-llvm → onnx-pytorch → onnx-quantized → chaos-ai-npu → xmnn-whl-builder），每层构建耗时 3-15 分钟不等。

### 解决方案

`docker-cache` 将构建好的镜像以 `tar.gz` 格式保存到 Windows 文件系统（`.docker-cache/` 目录），通过 Dockerfile checksum 实现智能缓存：

- **首次构建**：正常 `docker build`，完成后自动 `docker save | pigz` 保存到缓存
- **缓存命中**：Dockerfile 未变更时直接 `pigz -dc | docker load`，**2-5 分钟**恢复全部镜像
- **变更检测**：Dockerfile 修改后自动检测 checksum 变化，重新构建并更新缓存
- **数据安全**：缓存文件在 Windows NTFS 上，WSL2 重置不会丢失

---

## 快速开始

### 前置检查

```bash
bash .agents/scripts/docker-cache doctor
```

确保输出"所有检查通过 ✅"。需要：Docker 运行中、python3 可用、gzip/pigz 可用。

### 首次构建并缓存

```bash
# 构建镜像，自动缓存（推荐方式）
bash .agents/scripts/docker-cache build \
    -i devcontainer-base:chaos-ai-npu-latest \
    -f external/chaos/ai/Dockerfile \
    -c external/chaos/ai/ \
    --cn
```

### WSL2 重置后快速恢复

```bash
# 一键加载所有缓存镜像
bash .agents/scripts/docker-cache load --all
```

### 查看缓存状态

```bash
bash .agents/scripts/docker-cache list
```

输出示例：

```
╔══════════════════════════════════════════════════════════════╗
📦 Docker 镜像缓存列表
╚══════════════════════════════════════════════════════════════╝

镜像名称                            大小    缓存时间      Docker
──────────────────────────────────────  ────────  ────────────────  ──────
devcontainer-base:onnx-pytorch-latest   2.1GB     2026-08-09 18:30  ✅
devcontainer-base:chaos-ai-npu-latest   2.4GB     2026-08-09 19:15  ✅

ℹ️  共 2 个缓存镜像，总计 4.5GB
```

Docker 列图标说明：
- ✅ 本地镜像存在且 ID 与缓存一致
- ⚠️ 本地镜像存在但 ID 不匹配（可能是旧版本）
- ❌ 本地镜像不存在（需要 load）

---

## 命令参考

全局用法：`bash .agents/scripts/docker-cache <命令> [选项]`

### build — 智能构建与缓存

**核心命令**。根据 Dockerfile checksum 自动判断走快速路径（从缓存加载）还是构建路径（docker build + 自动缓存）。

```bash
bash .agents/scripts/docker-cache build [选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-i, --image NAME` | 目标镜像名称 **（必填）** | - |
| `-f, --file PATH` | Dockerfile 路径 | `./Dockerfile` |
| `-c, --context DIR` | 构建上下文目录 | Dockerfile 所在目录 |
| `-t, --tag TAG` | 镜像标签（与 `-i` 二选一） | - |
| `--build-arg K=V` | 构建参数（可多次指定） | - |
| `--no-cache` | 忽略 Docker 构建层缓存 | `false` |
| `--no-cache-load` | 强制重新构建（忽略本地缓存，但构建后仍更新缓存） | `false` |
| `--cn` | 使用国内镜像源（APT=阿里云, Conda=清华, PIP=阿里云） | `false` |
| `--buildkit-cache` | 启用 BuildKit 缓存挂载（预留） | `false` |

**决策流程**：

```
build 命令启动
    │
    ├─ 计算 Dockerfile SHA256 checksum
    │
    ├─ 检查 manifest 中是否有该镜像记录？
    │   ├─ 无记录 → 走构建路径
    │   └─ 有记录 → 检查缓存文件存在 && Dockerfile checksum 匹配？
    │       ├─ 不匹配（文件缺失或 Dockerfile 已变更）→ 走构建路径
    │       └─ 匹配 → 走快速路径
    │
    ├─ [快速路径] ⚡
    │   ├─ 检查 Docker 中是否已有相同 ID 的镜像？
    │   │   ├─ 是 → 直接返回（0 秒）
    │   │   └─ 否 → pigz -dc | docker load（2-5 分钟）
    │   └─ 完成
    │
    └─ [构建路径] 🔨
        ├─ DOCKER_BUILDKIT=1 docker build（完整构建）
        ├─ docker save | pigz > 缓存文件（原子写入）
        ├─ 更新 manifest.json
        └─ 验证镜像可 inspect
```

**示例**：

```bash
# 基本构建
bash .agents/scripts/docker-cache build -i myapp:latest -f ./Dockerfile

# 使用国内镜像源 + 自定义构建参数
bash .agents/scripts/docker-cache build \
    -i devcontainer-base:chaos-ai-npu-latest \
    -f external/chaos/ai/Dockerfile \
    -c external/chaos/ai/ \
    --cn \
    --build-arg CUDA_VERSION=12.1

# 强制重新构建（忽略缓存，但更新缓存文件）
bash .agents/scripts/docker-cache build -i myapp:latest -f ./Dockerfile --no-cache-load

# 自定义缓存目录
DOCKER_CACHE_DIR=/mnt/d/docker-cache bash .agents/scripts/docker-cache build -i myapp:latest -f ./Dockerfile
```

---

### save — 手动保存镜像

将当前 Docker 中已存在的镜像保存到缓存。通常 `build` 命令会自动保存，此命令用于手动保存非 build 命令创建的镜像（如 `docker pull` 的镜像、手工 commit 的镜像）。

```bash
bash .agents/scripts/docker-cache save <IMAGE_NAME> [选项]
bash .agents/scripts/docker-cache save --all [选项]
```

| 选项 | 说明 |
|------|------|
| `IMAGE_NAME` | 要保存的镜像名（如 `ubuntu:22.04`） |
| `--all` | 保存 manifest 中记录的所有缓存镜像 |
| `--force` | 即使已缓存且镜像 ID 未变，也强制重新保存 |

**智能跳过**：如果镜像 ID 与 manifest 中记录的一致，自动跳过（可用 `--force` 覆盖）。

**示例**：

```bash
# 保存单个镜像
bash .agents/scripts/docker-cache save ubuntu:22.04

# 保存 manifest 中记录的所有镜像（刷新已有缓存）
bash .agents/scripts/docker-cache save --all

# 强制重新保存所有
bash .agents/scripts/docker-cache save --all --force
```

---

### load — 从缓存加载

从缓存文件恢复镜像到 Docker。

```bash
bash .agents/scripts/docker-cache load <IMAGE_NAME>
bash .agents/scripts/docker-cache load --all
```

| 选项 | 说明 |
|------|------|
| `IMAGE_NAME` | 要加载的镜像名 |
| `--all` | 加载 manifest 中记录的所有缓存镜像 |

**智能跳过**：如果 Docker 中已有相同 ID 的镜像，自动跳过。

**示例**：

```bash
# WSL2 重置后恢复所有镜像
bash .agents/scripts/docker-cache load --all

# 加载单个镜像
bash .agents/scripts/docker-cache load devcontainer-base:chaos-ai-npu-latest
```

---

### list — 查看缓存状态

列出所有缓存镜像及其元数据。

```bash
bash .agents/scripts/docker-cache list [--json]
```

| 选项 | 说明 |
|------|------|
| `--json` | 以 JSON 格式输出（机器可读，便于脚本解析） |

表格字段说明：

| 列 | 说明 |
|----|------|
| 镜像名称 | `name:tag` 格式 |
| 大小 | 压缩后文件大小（tar.gz） |
| 缓存时间 | 保存到缓存的 UTC 时间 |
| Docker | 本地 Docker 中该镜像的状态（✅/⚠️/❌） |

---

### clean — 清理缓存

清理缓存文件，支持多种清理粒度。

```bash
bash .agents/scripts/docker-cache clean [选项]
bash .agents/scripts/docker-cache clean <IMAGE_NAME> [选项]
```

| 选项 | 说明 |
|------|------|
| `IMAGE_NAME` | 清理指定镜像的缓存 |
| `--all` | 清理所有镜像缓存（保留 manifest.json 结构） |
| `--orphans` | 只清理孤立文件（images/ 中存在但 manifest 未记录的文件） |
| `--buildkit` | 同时清理 BuildKit 缓存目录 |
| `-y, --yes` | 跳过确认提示（用于 CI/脚本） |

不带参数运行时，显示当前缓存统计信息。

**示例**：

```bash
# 查看缓存统计
bash .agents/scripts/docker-cache clean

# 清理单个镜像
bash .agents/scripts/docker-cache clean myapp:latest

# 清理所有镜像缓存（需确认）
bash .agents/scripts/docker-cache clean --all

# 清理孤立文件（安全操作，不影响有效缓存）
bash .agents/scripts/docker-cache clean --orphans

# CI 中清理所有缓存（含 BuildKit），无需确认
bash .agents/scripts/docker-cache clean --all --buildkit -y
```

---

### doctor — 环境诊断

检查运行环境的各项依赖和缓存完整性。

```bash
bash .agents/scripts/docker-cache doctor
```

检查项目：

| 检查项 | 说明 | 严重级别 |
|--------|------|----------|
| Docker CLI | docker 命令是否可用 | ❌ 错误 |
| Docker Daemon | dockerd 是否运行 | ❌ 错误 |
| 缓存目录 | `.docker-cache/` 是否可写 | ❌ 错误 |
| Manifest 合法性 | `manifest.json` JSON 格式是否正确 | ❌ 错误 |
| 压缩工具 | pigz（多线程）或 gzip 是否可用 | ❌ 错误 |
| 文件锁 | flock 是否可用（降级到目录锁） | ⚠️ 警告 |
| Python 3 | python3 是否可用（manifest 管理必需） | ❌ 错误 |
| SHA256 | sha256sum/sha256 是否可用 | ❌ 错误 |
| 缓存完整性 | 文件是否缺失、hash 是否匹配、孤立文件检查 | ❌/⚠️ |

---

## 架构原理

### 目录结构

```
.docker-cache/
├── manifest.json          # 镜像元数据清单（JSON）
├── images/                # 镜像压缩包存储
│   ├── devcontainer-base_chaos-ai-npu-latest.tar.gz
│   ├── devcontainer-base_onnx-pytorch-latest.tar.gz
│   └── ...
├── buildkit-cache/        # BuildKit 缓存挂载目录（预留）
└── .locks/                # 文件锁目录
    ├── devcontainer-base_chaos-ai-npu-latest.lock
    └── ...
```

**设计决策**：缓存根目录 `.docker-cache/` 位于项目根目录（通过 `.git` 目录向上查找确定），属于 Windows 文件系统（NTFS），因此不受 WSL2 重置影响。所有缓存文件不应纳入 Git 版本控制（已在 `.gitignore` 中排除）。

### 缓存命中判定

`build` 命令使用 **Dockerfile SHA256 Checksum** 作为缓存命中的唯一判定依据：

1. 构建前，计算当前 Dockerfile 的 SHA256 hash
2. 查询 manifest.json 中该镜像的 `dockerfile_checksum` 字段
3. 比对两个 hash：
   - **一致** + 缓存文件存在 → 缓存命中 → 走快速路径
   - **不一致** 或缓存文件缺失 → 缓存未命中 → 走构建路径
4. 构建完成后，将新的 Dockerfile checksum 和镜像 ID 写入 manifest

> **注意**：此机制检测的是 Dockerfile 本身的变更，不检测构建上下文目录中其他文件（如 `COPY` 进去的源码）的变更。如果修改了源码但未修改 Dockerfile，需要使用 `--no-cache-load` 强制重建。

### 并发安全

针对多个终端/CI 进程同时操作同一镜像缓存的场景，使用文件锁（flock）保证互斥：

- **首选方案**：`flock` 系统调用（Linux/macOS/WSL2 默认支持），对每个镜像使用独立的锁文件 `.locks/<safe_name>.lock`
- **降级方案**：如果 flock 不可用，使用目录锁（`mkdir` 原子性）作为降级方案——`mkdir` 在同一时刻只有一个进程能成功创建目录，失败方循环等待
- **锁粒度**：每个镜像独立锁，不同镜像的操作可以并行
- **锁释放**：通过 `trap cleanup EXIT` 确保脚本异常退出时也能释放锁

镜像名到锁文件名的转换（`sanitize_image_name`）：
- `/` → `_`
- `:` → `_`
- 例：`devcontainer-base:chaos-ai-npu-latest` → `devcontainer-base_chaos-ai-npu-latest.lock`

### 压缩策略

| 工具 | 场景 | 特点 |
|------|------|------|
| `pigz` | 多线程并行 gzip | 默认优先使用，速度比 gzip 快 3-5 倍（取决于 CPU 核心数） |
| `gzip` | 单线程 gzip | pigz 不可用时的降级方案，所有 Unix 系统默认携带 |

压缩/解压命令自动检测：
```bash
if command -v pigz &>/dev/null; then
    COMPRESS_CMD="pigz"        # 压缩
    DECOMPRESS_CMD="pigz -dc"  # 解压
else
    COMPRESS_CMD="gzip"
    DECOMPRESS_CMD="gzip -dc"
fi
```

**流式处理**：`docker save | pigz > file.tar.gz` 和 `pigz -dc file.tar.gz | docker load` 使用管道流式处理，无需中间临时文件，内存占用恒定。

**原子写入**：保存镜像时先写入 `<final_name>.tar.gz.tmp.$$` 临时文件（在最终文件名后追加 `.tmp.$$` 后缀，`$$` 为当前进程 PID），写入成功后计算 SHA256 指纹（存入 manifest 供后续完整性校验），再通过 `mv` 原子重命名到最终路径。由于临时文件与目标文件在同一目录（同一文件系统内），`mv` 操作为原子 rename，不会出现半写入文件。

> **注意**：脚本的 `trap cleanup EXIT` 仅清理 manifest 的临时文件。如果在 `docker save | pigz` 写入过程中被 Ctrl+C 强制中断，镜像临时文件（`.tar.gz.tmp.*`）可能残留在 `images/` 目录中。可手动清理：`find .docker-cache/images/ -name "*.tmp.*" -delete`。docker save 失败时（管道命令返回非零）会显式删除临时文件。

### Manifest 数据模型

`manifest.json` 采用 JSON 格式，记录每个缓存镜像的元数据：

```json
{
  "version": "1.0",
  "images": {
    "devcontainer-base:chaos-ai-npu-latest": {
      "image_name": "devcontainer-base:chaos-ai-npu-latest",
      "image_id": "sha256:abc123...",
      "file": "devcontainer-base_chaos-ai-npu-latest.tar.gz",
      "compressed_size": 2576980377,
      "sha256": "sha256:def456...",
      "created_at": "2026-08-09T11:15:30Z",
      "dockerfile": "/path/to/Dockerfile",
      "dockerfile_checksum": "sha256:ghi789..."
    }
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `image_name` | string | 完整镜像名（含 tag） |
| `image_id` | string | Docker 镜像 ID（`sha256:...` 格式） |
| `file` | string | 缓存文件名（`images/` 目录下） |
| `compressed_size` | int | 压缩后文件大小（字节） |
| `sha256` | string | 缓存文件的 SHA256 hash，用于完整性校验 |
| `created_at` | string | 保存时间（ISO 8601 UTC） |
| `dockerfile` | string\|null | 构建时使用的 Dockerfile 绝对路径（手动 save 时为 null） |
| `dockerfile_checksum` | string\|null | Dockerfile 的 SHA256 hash（手动 save 时为 null） |

**原子更新**：所有 manifest 写入操作（`manifest_set`/`manifest_remove`/`manifest_clear_all`）统一使用「写临时文件 `manifest.json.tmp.$$` → Python `json.load()` 校验格式合法 → `mv` 覆盖」三步法。`trap cleanup EXIT` 会在脚本异常退出时自动清理未完成的 manifest 临时文件，确保不会出现半截 manifest。由于临时文件与目标在同一目录，`mv` 为原子 rename 操作。

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DOCKER_CACHE_DIR` | 缓存根目录 | 项目根目录下的 `.docker-cache/`（自动通过 `.git` 目录定位） |

**示例**：将缓存放到独立磁盘分区

```bash
DOCKER_CACHE_DIR=/mnt/d/docker-cache bash .agents/scripts/docker-cache build -i myapp:latest -f ./Dockerfile
```

也可以在 shell 配置中永久设置：

```bash
# ~/.bashrc 或 ~/.zshrc
export DOCKER_CACHE_DIR=/mnt/d/docker-cache
```

---

## 典型工作流

### 场景 1：首次环境搭建

```bash
# 1. 检查环境
bash .agents/scripts/docker-cache doctor

# 2. 构建第一层基础镜像
bash .agents/scripts/docker-cache build \
    -i devcontainer-base:onnx-pytorch-latest \
    -f apps/docker-images/devcontainer-base/variants/onnx-pytorch/Dockerfile \
    -c apps/docker-images/devcontainer-base/ \
    --cn

# 3. 构建依赖上层镜像（自动利用 Docker 层缓存 + docker-cache 缓存）
bash .agents/scripts/docker-cache build \
    -i devcontainer-base:chaos-ai-npu-latest \
    -f external/chaos/ai/Dockerfile \
    -c external/chaos/ai/ \
    --cn

# 4. 确认缓存状态
bash .agents/scripts/docker-cache list
```

### 场景 2：WSL2 重置后恢复

```bash
# 1. 启动 Docker Desktop

# 2. 一键恢复所有缓存镜像
bash .agents/scripts/docker-cache load --all

# 3. 验证镜像就绪
bash .agents/scripts/docker-cache list
# Docker 列应全部显示 ✅
```

### 场景 3：Dockerfile 修改后重建

```bash
# 修改 Dockerfile 后，直接重新运行 build 命令
# 工具自动检测到 Dockerfile checksum 变化，走构建路径
bash .agents/scripts/docker-cache build \
    -i devcontainer-base:chaos-ai-npu-latest \
    -f external/chaos/ai/Dockerfile \
    -c external/chaos/ai/ \
    --cn

# 构建完成后缓存自动更新，manifest 中 checksum 同步更新
```

### 场景 4：源码修改但 Dockerfile 未变

```bash
# 如果只改了 COPY 进去的源码，Dockerfile checksum 不会变化
# 需要用 --no-cache-load 强制重建
bash .agents/scripts/docker-cache build \
    -i devcontainer-base:chaos-ai-npu-latest \
    -f external/chaos/ai/Dockerfile \
    -c external/chaos/ai/ \
    --no-cache-load
```

### 场景 5：多机器同步缓存

```bash
# 机器 A：保存镜像到缓存后，拷贝 .docker-cache/ 到共享存储/U盘
rsync -av .docker-cache/ /path/to/usb/docker-cache/

# 机器 B：设置 DOCKER_CACHE_DIR 指向拷贝过来的目录，直接加载
DOCKER_CACHE_DIR=/path/to/usb/docker-cache bash .agents/scripts/docker-cache load --all
```

---

## 与现有构建脚本集成

### apps/docker-images/devcontainer-base/variants/build.sh

现有构建脚本支持 `--use-cache` 选项集成 docker-cache。集成方式参考：

```bash
# 原有构建命令
docker build -t "$IMAGE_NAME" -f "$DOCKERFILE" "$CONTEXT_DIR"

# 替换为 docker-cache 构建
bash "${PROJECT_ROOT}/.agents/scripts/docker-cache" build \
    -i "$IMAGE_NAME" \
    -f "$DOCKERFILE" \
    -c "$CONTEXT_DIR" \
    ${USE_CN_MIRRORS:+--cn} \
    ${BUILD_ARGS[@]/#/--build-arg }
```

### 关键集成点

1. **build 命令替代 docker build**：保持相同的 `-f`、`-c`、`--build-arg`、`-t/-i` 参数语义
2. **`--cn` 标志映射**：国内镜像源参数通过 `--cn` 传递
3. **返回值**：build 成功返回 0，失败返回非 0，与 docker build 一致
4. **输出格式**：所有输出带 emoji 前缀和彩色高亮，便于在 CI 日志中识别

---

## 故障排查

### 问题：`doctor` 报告 "Python: python3 未安装"

**解决方案**：WSL2 中安装 Python 3：

```bash
sudo apt update && sudo apt install -y python3
```

### 问题：压缩速度慢

**解决方案**：安装 pigz 启用多线程压缩：

```bash
sudo apt install -y pigz
# 验证
bash .agents/scripts/docker-cache doctor
# 应显示 "压缩工具: pigz (多线程)"
```

### 问题：`list` 显示 ⚠️（ID 不匹配）

**原因**：本地 Docker 中存在同名但不同 ID 的镜像（可能是旧版本构建或手动拉取的）。

**解决方案**：

```bash
# 方案1：直接从缓存加载正确版本（覆盖本地镜像）
bash .agents/scripts/docker-cache load <IMAGE_NAME>

# 方案2：如果本地版本是最新的，手动保存刷新缓存
bash .agents/scripts/docker-cache save <IMAGE_NAME> --force
```

### 问题：`doctor` 报告文件损坏（hash 不匹配）

**原因**：缓存文件可能在写入时磁盘空间不足或被意外中断。

**解决方案**：删除损坏文件后重新构建：

```bash
bash .agents/scripts/docker-cache clean <IMAGE_NAME>
bash .agents/scripts/docker-cache build -i <IMAGE_NAME> -f <Dockerfile> -c <context> --no-cache-load
```

### 问题：`build` 总是走构建路径（不命中缓存）

**排查步骤**：

1. 运行 `bash .agents/scripts/docker-cache doctor` 检查是否有缓存完整性问题
2. 运行 `bash .agents/scripts/docker-cache list --json` 查看 `dockerfile_checksum` 字段
3. 确认 Dockerfile 路径与构建时使用的路径一致（路径不同但内容相同也会导致缓存隔离）
4. 如果使用了不同的构建上下文目录（`-c` 参数），不影响缓存命中（只校验 Dockerfile 本身）

### 问题：WSL2 中看不到 `.docker-cache/` 目录

**原因**：`DOCKER_CACHE_DIR` 默认是通过 `.git` 目录向上查找项目根目录。如果从非项目目录运行脚本可能定位错误。

**解决方案**：显式设置 `DOCKER_CACHE_DIR`：

```bash
DOCKER_CACHE_DIR=/mnt/d/spaces/SpecWeave/.docker-cache bash .agents/scripts/docker-cache list
```

---

## 内部测试

脚本包含内置自测，用于验证核心工具函数：

```bash
bash .agents/scripts/docker-cache --test
```

测试项包括：`sanitize_image_name`（镜像名转义）和 `human_size`（字节大小格式化）。
